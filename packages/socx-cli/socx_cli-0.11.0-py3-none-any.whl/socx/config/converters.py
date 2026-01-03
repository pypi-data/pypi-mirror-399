"""Dynaconf converter implementations tailored for SoCX."""

from __future__ import annotations

from collections import ChainMap
import os
import sys
import abc
import runpy
import shlex
import logging
from types import CodeType, ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
    overload,
    override,
    TypeVar,
    ClassVar,
)
from pathlib import Path
from importlib import import_module
from functools import cached_property, singledispatchmethod
from collections.abc import Iterable, Callable

import sh
import rich_click as click
import rich_click.patch as click_patch
import rich_click.rich_click_theme as click_theme
from pydantic import validate_call, ConfigDict
from dynaconf import add_converter
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.parse_conf import Lazy
from click.utils import _detect_program_name

from socx.config.schema.plugin import PluginModel


AnyCallableT = TypeVar("AnyCallableT", bound=Callable[..., Any])

_validate = validate_call(config=ConfigDict(arbitrary_types_allowed=True))

logger = logging.getLogger(__name__)


class Converter[TI, TO](abc.ABC):
    """Base protocol for Dynaconf converters used by SoCX."""

    @abc.abstractmethod
    def __call__(self, value: TI, *args: Any, **kwargs: Any) -> TO:
        """Convert Dynaconf configuration values into runtime objects."""

    @cached_property
    def name(self) -> str:
        """Return the name of the converter."""
        return self.get_name()

    @cached_property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"{logger.name}.{self.name}")

    def log_exception(
        self, msg: str, *args: Any, exc: Exception | None = None, **kwargs: Any
    ) -> None:
        """Log a recoverable converter error message."""
        if exc is not None:
            exc.add_note(msg)
        self.logger.exception(msg, *args, **kwargs)

    def convert(self, value: TI, *args: Any, **kwargs: Any) -> TO:
        """Convert a configuration value to a python object."""
        return self(value, *args, **kwargs)

    def get_name(self) -> str:
        return self.__class__.__name__.lower().removesuffix("converter")


class PathConverter(Converter[str | Path | Lazy, Path | Lazy]):
    """Resolve string inputs into concrete filesystem paths."""

    @overload
    def __call__(
        self, value: str | Path, *args: Any, **kwargs: Any
    ) -> Path: ...

    @overload
    def __call__(self, value: Lazy, *args: Any, **kwargs: Any) -> Lazy: ...

    @override
    @_validate
    def __call__(
        self, value: str | Path | Lazy, *args: Any, **kwargs: Any
    ) -> Lazy | Path:
        """Return a resolved ``Path`` or preserve deferred conversion."""
        if isinstance(value, Lazy):
            if value.casting is self:
                return value
            return value.set_casting(self)

        path = Path(value) if isinstance(value, str) else value

        try:
            path = path.resolve()
        except OSError:
            self.log_exception(str(value))

        return path


class CompileConverter(Converter[str | Path | Lazy, CodeType | Lazy | None]):
    """Compile python source files referenced in configuration values."""

    @overload
    def __call__(self, value: Lazy, *args: Any, **kwargs: Any) -> Lazy: ...
    @overload
    def __call__(
        self, value: str, *args: Any, **kwargs: Any
    ) -> CodeType | None: ...
    @overload
    def __call__(
        self, value: Path, *args: Any, **kwargs: Any
    ) -> CodeType | None: ...

    @override
    @_validate
    def __call__(
        self, value: str | Path | Lazy, *args: Any, **kwargs: Any
    ) -> CodeType | Lazy | None:
        """Return compiled code objects or propagate lazy evaluation."""
        if isinstance(value, Lazy):
            if value.casting is self:
                return value
            return value.set_casting(self)

        if isinstance(value, str):
            value = Path(value)

        try:
            value = value.resolve()
        except OSError:
            self.log_exception(str(value))
            return None

        try:
            rv = compile(value.read_text(), str(value), "exec")
        except (SyntaxError, ValueError):
            rv = None
            self.log_exception(str(value))
        return rv


class ImportConverter(Converter[str | Lazy, ModuleType | Lazy | None]):
    """Import modules referenced in configuration entries."""

    @override
    @_validate
    def __call__(
        self, value: str | Lazy, *args: Any, **kwargs: Any
    ) -> ModuleType | Lazy | None:
        """Import a module referenced by dotted string or handle laziness."""
        if isinstance(value, Lazy):
            if value.casting is self:
                return value
            return value.set_casting(self)

        if not self.is_module_path(value):
            return None

        if TYPE_CHECKING:
            value = cast(str, value)

        try:
            rv = import_module(value)
        except ImportError:
            rv = None
            self.log_exception(value)
        else:
            return rv

    @classmethod
    def is_module_path(cls, path: Any) -> bool:
        return isinstance(path, str) and all(
            part.isidentifier() for part in path.split(".")
        )


class EvalConverter(
    Converter[str | Path | CodeType | Lazy, Lazy | dict[str, Any]]
):
    """Evaluate compiled python code in an isolated namespace."""

    def __init__(self) -> None:
        self.compiler = CompileConverter()

    @overload
    def __call__(self, value: Lazy, *args: Any, **kwargs: Any) -> Lazy: ...
    @overload
    def __call__(
        self, value: str, *args: Any, **kwargs: Any
    ) -> dict[str, Any]: ...
    @overload
    def __call__(
        self, value: Path, *args: Any, **kwargs: Any
    ) -> dict[str, Any]: ...
    @overload
    def __call__(
        self, value: CodeType, *args: Any, **kwargs: Any
    ) -> dict[str, Any]: ...

    @override
    @_validate
    def __call__(
        self, value: str | Path | CodeType | Lazy, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | Lazy:
        """Provide an execution namespace for compiled configuration code."""
        if isinstance(value, Lazy):
            if value.casting is self:
                return value
            return value.set_casting(self)

        code = self.compiler(value) if isinstance(value, str | Path) else value

        if isinstance(code, Lazy):
            code = code(code.value)

        if code is not None:
            ns = {**globals(), **locals()}
            try:
                eval(code, ns, ns)
            except Exception:
                self.log_exception(str(value))
            return ns
        return {}


class SymbolConverter(Converter[str | Lazy, Any]):
    """Resolve dotted ``path:attribute`` references or file symbols."""

    def __init__(self) -> None:
        self.importer = ImportConverter()
        self.compiler = CompileConverter()
        self.evaluator = EvalConverter()

    @overload
    def __call__(self, value: str) -> Any: ...
    @overload
    def __call__(self, value: Lazy) -> Lazy: ...

    @override
    @_validate
    def __call__(self, value: str | Lazy, *args: Any, **kwargs: Any) -> Any:
        """Resolve a symbol from a module or python file path."""
        if isinstance(value, Lazy):
            if value.casting is self:
                return value
            return value.set_casting(self)

        path, _, symbol = value.partition(":")

        if not path:
            self.log_exception(f"Command path/pathspec is missing: {value}")
            return None

        if not symbol:
            self.log_exception(f"Command symbol is missing: {value}")
            return None

        if not Path(path).exists():
            module = self.importer(path)
            return getattr(module, symbol)

        path = Path(path)

        if path.is_file():
            if str(path.parent) not in sys.path:
                sys.path.insert(0, str(path.parent))
            code = self.compiler(path)
            return code and self.evaluator(code).get(symbol)

        return None


class CommandConverter(
    Converter[
        str | Lazy | sh.Command | click.Command | PluginModel,
        str | Lazy | click.Command,
    ]
):
    """Turn module or script references into Rich Click commands."""

    group_kwargs: ClassVar[dict[str, Any]] = dict(
        options_metavar="",
        subcommand_metavar="",
        add_help_option=False,
        no_args_is_help=False,
        invoke_without_command=True,
        context_settings=dict(
            help_option_names=[],
            allow_extra_args=True,
            ignore_unknown_options=True,
            allow_interspersed_args=False,
        ),
    )

    def __init__(self) -> None:
        self.importer = ImportConverter()
        self.sh_converter = ShConverter()

    @overload
    def __call__(
        self,
        value: Lazy,
        *args: Any,
        **kwargs: Any,
    ) -> Lazy: ...
    @overload
    def __call__(
        self,
        value: str,
        *args: Any,
        **kwargs: Any,
    ) -> click.Command: ...
    @overload
    def __call__(
        self,
        value: sh.Command,
        *args: Any,
        **kwargs: Any,
    ) -> click.Command: ...
    @overload
    def __call__(
        self,
        value: click.Command,
        *args: Any,
        **kwargs: Any,
    ) -> click.Command: ...
    @overload
    def __call__(
        self,
        value: PluginModel,
        *args: Any,
        **kwargs: Any,
    ) -> click.Command: ...

    @override
    @_validate
    def __call__(
        self,
        value: str | Lazy | sh.Command | click.Command | PluginModel,
        *args: Any,
        **kwargs: Any,
    ) -> Lazy | click.Command | click.Group:
        """Build a Click command from dotted paths or reuse existing ones."""
        if isinstance(value, Lazy):
            if value.casting is self:
                return value
            return value.set_casting(self)

        self._patch_theme()

        if isinstance(value, click.Command):
            return value

        @click.group(**self.group_kwargs)
        @click.argument(
            "args",
            nargs=-1,
            required=False,
            expose_value=True,
            type=click.UNPROCESSED,
            metavar="[<subcommand>] [<args>...]",
        )
        def cli(args):
            nonlocal value

            if TYPE_CHECKING:
                value = cast(str | sh.Command | PluginModel, value)

            if isinstance(value, str):
                return self._run_from_pathspec(value, *args)

            if isinstance(value, sh.Command):
                return self._run_shell_script(value, *args)

            if isinstance(value, PluginModel) and value.is_script():
                return self._run_shell_script(value, *args)

            return self._run_from_pathspec(value, *args)

        if TYPE_CHECKING:
            cli = cast(click.Group, cli)

        return cli

    @singledispatchmethod
    def _run_shell_script(self, value, *args, env=None, **kwargs) -> int: ...

    @_run_shell_script.register
    def _(
        self,
        value: str,
        *args: Any,
        env: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> int:
        cmd = self.sh_converter.convert(value)
        if isinstance(cmd, str):
            return -1
        else:
            return self._run_shell_script(cmd, *args, env=env, **kwargs)

    @_run_shell_script.register
    def _(
        self,
        value: sh.Command,
        *args: Any,
        env: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> int:
        proc = value(
            *args,
            **kwargs,
            _bg=True,
            _env=env,
            _in=sys.stdin,
            _out=sys.stdout,
            _err=sys.stderr,
            _return_cmd=True,
        )

        if TYPE_CHECKING:
            proc = cast(sh.RunningCommand, proc)

        rv = proc.exit_code
        return rv if rv is not None else -1

    @_run_shell_script.register
    def _(
        self,
        value: PluginModel,
        *args: Any,
        env: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> int:
        env = env or (
            value.env
            if value.fresh_env
            else dict(ChainMap(os.environ.copy(), value.env))
        )
        return self._run_shell_script(value.script, *args, env=env, **kwargs)

    @singledispatchmethod
    def _run_from_pathspec(self, value, *args, env=None, **kwargs) -> Any: ...

    @_run_from_pathspec.register
    def _(
        self,
        value: str,
        env: dict[str, str] | None = None,
    ) -> dict[str, Any] | Any:
        def noop(**_) -> None:
            return None

        rv = {}
        ctx = click.get_current_context(silent=True)
        path, _, symbol = value.rpartition(":")
        argv = sys.argv.copy()
        syspath = sys.path.copy()
        environ = os.environ.copy()

        if ctx:
            name = ctx.command.name
        elif symbol:
            name = symbol
        elif path:
            name = Path(path).stem
        else:
            err = "Could not infer command name"
            raise RuntimeError(err)

        while sys.argv and sys.argv[0] != name:
            sys.argv.pop(0)

        sys.argv[0] = f"socx {sys.argv[0]}"

        if env:
            os.environ.clear()
            os.environ.update(env)

        if self.is_script_path(path):
            sys.path.insert(0, str(Path(path).parent))
        elif self.is_package_path(path):
            sys.path.insert(0, path)

        try:
            if self.is_module_path(path) and symbol:
                obj = self.importer(path)
                obj = getattr(obj, symbol, noop)
                if callable(obj):
                    if isinstance(obj, click.Command):
                        rv = obj.main(
                            sys.argv[1:], sys.argv[0], standalone_mode=False
                        )
                    else:
                        rv = obj()
            elif symbol:
                rv = None
                obj = runpy.run_path(path).get(symbol, noop)
                if callable(obj):
                    if isinstance(obj, click.Command):
                        rv = obj.main(
                            sys.argv[1:], sys.argv[0], standalone_mode=False
                        )
                    else:
                        rv = obj()
            else:
                rv = runpy.run_path(path, run_name=_detect_program_name())
        except Exception as exc:
            err = f"Failed to run pathspec '{value}'"
            self.log_exception(err, exc=exc)
            raise
        finally:
            sys.argv = argv
            sys.path = syspath
            os.environ.clear()
            os.environ.update(environ)

        return rv

    @_run_from_pathspec.register
    def _(
        self,
        value: Path,
        *args: Any,
        env: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any] | Any:
        return self._run_from_pathspec(str(value), *args, env=env, **kwargs)

    @_run_from_pathspec.register
    def _(
        self, value: PluginModel, *args: Any, **kwargs: Any
    ) -> dict[str, Any] | Any:
        if not value.command:
            return {}
        env = (
            value.env
            if value.fresh_env
            else {**os.environ.copy(), **value.env}
        )
        if "-h" in sys.argv or "--help" in sys.argv:
            ctx = click.get_current_context()
            if ctx:
                if value.epilog:
                    ctx.command.epilog = ctx.command.epilog or value.epilog
                if value.short_help:
                    ctx.command.short_help = (
                        ctx.command.short_help or value.short_help
                    )
                if value.help:
                    ctx.command.help = ctx.command.help or value.help
                    click.echo(ctx.get_help())
                    ctx.exit()
        return self._run_from_pathspec(value.command, env=env)

    @classmethod
    def _patch_theme(cls) -> None:
        theme = (
            click.rich_click.THEME.name
            if isinstance(click.rich_click.THEME, click_theme.RichClickTheme)
            else click.rich_click.THEME
        )
        cfg = click.RichHelpConfiguration.load_from_globals(theme=theme)
        click_patch.patch(cfg, patch_rich_click=True, patch_typer=True)

    def is_pathspec(self, path: Any) -> bool:
        """Return ``True`` if ``path`` is either a script or package path."""
        return (
            self.is_module_path(path)
            or self.is_script_path(path)
            or self.is_package_path(path)
        )

    def is_shell_command(self, value: Any) -> bool:
        return isinstance(value, sh.Command)

    def is_click_command(self, value: Any) -> bool:
        return isinstance(value, click.Command)

    def is_module_path(self, path: Any) -> bool:
        return self.importer.is_module_path(path)

    def is_script_path(self, value: Any) -> bool:
        """Return ``True`` if ``path`` points to a python script file."""
        if isinstance(value, str):
            value = Path(value)
        return (
            isinstance(value, Path)
            and value.exists()
            and value.is_file()
            and value.suffix == ".py"
        )

    def is_package_path(self, value: Any) -> bool:
        """Return ``True`` if ``path`` points to a python package directory."""
        if isinstance(value, str):
            value = Path(value)
        return (
            isinstance(value, Path)
            and value.exists()
            and value.is_dir()
            and (value / "__init__.py").exists()
        )


class IncludeConverter(Converter[str | Path | Lazy, DynaBox | Lazy | None]):
    """Load configuration files referenced within other settings."""

    @overload
    def __call__(self, value: Lazy) -> Lazy: ...
    @overload
    def __call__(self, value: str) -> DynaBox | None: ...
    @overload
    def __call__(self, value: Path) -> DynaBox | None: ...

    @override
    @_validate
    def __call__(self, value: str | Path | Lazy) -> DynaBox | Lazy | None:
        """Return a new ``Settings`` instance for the provided include path."""
        if isinstance(value, Lazy):
            if value.casting is self:
                return value
            return value.set_casting(self)

        path = Path(value) if isinstance(value, str) else value

        if not self.is_yaml_path(path):
            return DynaBox()

        try:
            obj = DynaBox.from_yaml(path.read_text())
        except Exception:
            self.log_exception(str(value))
            obj = DynaBox()
        return obj

    @classmethod
    def is_yaml_path(cls, value: Path) -> bool:
        return (
            value.exists()
            and value.is_file()
            and value.suffix in [".yml", ".yaml"]
        )


class ShConverter(
    Converter[str | Lazy | sh.Command | PluginModel, str | Lazy | sh.Command]
):
    @singledispatchmethod
    @override
    def __call__(  # pyright: ignore[reportIncompatibleMethodOverride]
        self,
        value,
        *args: Any,
        **kwargs: Any,
    ) -> str | Lazy | sh.Command: ...

    @__call__.register
    def _(self, value: str, *args: Any, **kwargs: Any) -> str | sh.Command:
        cmd_args = [arg.strip() for arg in value.split()]

        if not cmd_args:
            err = f"Invalid script '{shlex.quote(value)}'"
            self.log_exception(err)
            return value

        try:
            cmd = sh.Command(cmd_args.pop(0))
        except sh.CommandNotFound as exc:
            err = f"Invalid script '{shlex.quote(value)}': {exc}"
            self.log_exception(err)
            exc.add_note(err)
            raise
        else:
            return cmd.bake(*cmd_args) if cmd_args else cmd

    @__call__.register
    def _(self, value: Lazy, *args: Any, **kwargs: Any) -> Lazy:
        return value if value.casting is self else value.set_casting(self)

    @__call__.register
    def _(self, value: sh.Command, *args: Any, **kwargs: Any) -> sh.Command:
        return value

    @__call__.register
    def _(
        self, value: PluginModel, *args: Any, **kwargs: Any
    ) -> str | sh.Command:
        if isinstance(value.script, str):
            return value.script

        env = (
            value.env
            if value.fresh_env
            else {**os.environ.copy(), **value.env}
        )

        return value.script.bake(_env=env)


class GenericConverter[TI, TO](Converter[TI, TO]):
    """Adapter turning plain callables into ``Converter`` instances."""

    def __init__(self, name: str, cvt: Callable[..., TO]) -> None:
        self._cvt = cvt
        self._name = name

    @override
    def __call__(self, value: TI, *args: Any, **kwargs: Any) -> TO:
        """Delegate conversion to the wrapped callable."""
        return self._cvt(value, *args, **kwargs)

    @override
    def get_name(self) -> str:
        return self._name


def add_converters(converters: Iterable[Converter]) -> None:
    """Register converters with Dynaconf using their inferred names."""
    for converter in converters:
        add_converter(converter.name, converter)


def get_converters() -> Iterable[tuple[str, Converter]]:
    """Yield converter registrations, wrapping raw callables as needed."""
    from dynaconf.utils.parse_conf import converters

    rv = []
    for name, cvt in converters.items():
        if not isinstance(cvt, Converter):
            cvt = GenericConverter(name, cvt)
        rv.append((name, cvt))
    return rv


def init() -> None:
    """Register the default set of converters used by SoCX."""
    converters = [
        ShConverter(),
        PathConverter(),
        ImportConverter(),
        CompileConverter(),
        EvalConverter(),
        SymbolConverter(),
        CommandConverter(),
        IncludeConverter(),
    ]
    add_converters(converters)
