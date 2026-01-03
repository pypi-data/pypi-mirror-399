"""Dynaconf configuration wrappers used across SoCX."""

from __future__ import annotations

import sys
import logging
from typing import Any, Literal, ParamSpec, TypeVar
from pathlib import Path
from collections import ChainMap
from collections.abc import Callable

try:
    import box

    sys.modules["dynaconf.vendor.box"] = box
except ImportError:
    from dynaconf.vendor import box

from dynaconf import LazySettings, get_history
from dynaconf.base import SourceMetadata, ensure_a_list
from dynaconf.utils.boxing import DynaBox
from dynaconf.utils.inspect import get_debug_info, _get_data_by_key
from dynaconf.utils.parse_conf import unparse_conf_data
from pydantic_core import to_jsonable_python

from socx.config.serializers import SettingsSerializer


logger = logging.getLogger(__name__)

T = TypeVar("T")
P = ParamSpec("P")
KT = TypeVar("KT", bound=str)
VT = TypeVar("VT")


SETTINGS_DEFAULTS: dict[str, Any] = dict(
    env="default",
    envvar="SOCX_SETTINGS_PATH",
    encoding="utf-8",
    auto_cast=True,
    load_dotenv=True,
    environments=False,
    dotted_lookup=True,
    envvar_prefix="SOCX",
    merge_enabled=True,
    lowercase_read=True,
    sysenv_fallback=True,
    dotenv_override=False,
    commentjson_enabled=True,
    apply_default_on_none=False,
)
"""Default options passed to Dynaconf constructor in `get_settings`."""


class Settings(LazySettings):
    """Singleton settings instance of loaded `socx` configurations."""

    def __init__(self, wrapped=None, **kwargs: Any) -> None:
        kwargs = dict(ChainMap(kwargs, SETTINGS_DEFAULTS))
        LazySettings.__init__(self, wrapped=wrapped, **kwargs)
        for file in self.dynaconf_include:
            if file not in self.loaded_files:
                self.load_file(path=file)

    def __contains__(self, key):
        return self.exists(key) or (
            isinstance(key, str) and hasattr(self, key)
        )

    @property
    def raw(self) -> dict[str, Any]:
        """Return this instance with all nested values as raw values.

        See Also
        --------
        get_raw : Further information regarding 'raw values'.

        """
        return self.encode(SettingsSerializer.serialize(self))

    @property
    def root(self) -> Path:
        """Get the root path of the current settings instance."""
        return Path(self._root_path)

    @root.setter
    def root(self, value: str | Path) -> None:
        if isinstance(value, str):
            value = Path(value)

        if value.is_file() and value.exists():
            self.set(
                "SETTINGS_FILE_FOR_DYNACONF",
                value,
                loader_identifier="init_settings_module",
            )
            self.reload()

    @property
    def history(self) -> tuple[dict[str, Any], ...]:
        """Get the history of this instance.

        See Also
        --------
        get_history : Additional options for retrieving the settings history.

        """
        return self.get_history()

    @property
    def metadata(self) -> list[SourceMetadata]:
        """Return the ``SourceMetadata`` of loaded settings history."""
        return self._loaded_by_loaders.keys()

    @property
    def excludes(self) -> list[str]:
        """Get a list of settings paths and glob expressions not to load."""
        return self.get("SKIP_FILES_FOR_DYNACONF", [])

    @excludes.setter
    def excludes(self, value: str | Path | list[str | Path]) -> None:
        """Set the list of settings paths and glob expressions not to load."""
        excludes = [str(v) for v in ensure_a_list(value)]
        self.update(
            data={"SKIP_FILES_FOR_DYNACONF": excludes},
            merge=bool("merge" in excludes),
            tomlfy=True,
        )
        self.reload()

    @property
    def includes(self) -> list[str]:
        """Get a list of settings paths and glob expressions to load."""
        return [
            *self.get("DYNACONF_INCLUDE", []),
            *[str(f) for f in self.settings_file],
        ]

    @includes.setter
    def includes(self, value: str | Path | list[str | Path]) -> None:
        """Set the list of settings paths and glob expressions to load."""
        self.dynaconf_include = [*self.dynaconf_include, value]
        self.reload()

    @property
    def loaded_files(self):
        """Get a list of paths to all loaded settings files."""
        return self._loaded_files

    @property
    def debug_info(self) -> dict[str, Any]:
        """Return a ``dict`` with useful debugging information of settings."""
        return self.get_debug_info()

    def as_box(self, key: str | None = None) -> DynaBox | box.BoxList:
        """Get the current settings as a ``DynaBox`` instance."""
        rv = self.get_raw(key)
        return DynaBox({key: rv}) if key is not None else DynaBox(rv)

    def to_json(self, key: str | None = None) -> str:
        """Serialize the current settings to JSON."""
        return self.as_box(key).to_json() or ""

    def to_toml(self, key: str | None = None) -> str:
        """Serialize the current settings to TOML."""
        return self.as_box(key).to_toml() or ""

    def to_yaml(self, key: str | None = None) -> str:
        """Serialize the current settings to YAML."""
        return self.as_box(key).to_yaml() or ""

    def get_raw(
        self,
        key: str | None = None,
        default: Any = None,
        sep: str | None = None,
    ) -> Any:
        """Return the raw value for key if such exists, else default.

        A raw value is the original value string as it was originally defined
        in the a configuration file, prior to casting it into a python object
        type.

        This is useful when writing back configuration files in order to
        revert unserializable python types into their original configuration
        string form.

        Parameters
        ----------
        key: str, optional
            The dictionary key of the raw value to return.
        default: Any, optional
            A default value to return if the key does not exist.
        sep: str, optional
            An optional seperator in the original key that will be replaced
            with a dot before performing a dotted lookup.

        Returns
        -------
        value_or_default: Any
            The value in its raw configuration format or default if key does
            not exist.

        """
        if key is None:
            return self.raw

        if self.exists(key):
            return self.encode(
                _get_data_by_key(
                    data=self.raw,
                    key_dotted_path=key,
                    default=default,
                    sep=(sep or "__"),
                )
            )

        if hasattr(self, key):
            return self.encode(getattr(self, key))

        return default

    def get_history(
        self, key: str | None = None, limit: int = 0
    ) -> tuple[dict[str, Any], ...]:
        """Get up to limit entries of loaded data history.

        Parameters
        ----------
        key: str | None, optional
            An optional key to by which to filter history entries in order
            to search for changes applied to a specific settings key.

        limit : int, optional
            If limit > 0, it specifies the maximum number of history entries
            to append to the returned result.

            If limit == 0, all history entries are returned in the result.

            entries are sorted from newest to oldest, with the newest entry
            being at index 0.

        Returns
        -------
        entries: tuple[dict[str, Any], ...]
            A tuple of history entries where each entry is a transformation
            that has been previously applied to the settings instance.

            The returned entries are ordered from oldest to newest.
        """
        return tuple(
            reversed(
                [
                    DynaBox(self.encode(entry))
                    for i, entry in enumerate(get_history(obj=self, key=key))
                    if limit == 0 or i < limit
                ]
            )
        )

    def get_debug_info(
        self, key: str | None = None, verbosity: Literal[0, 1, 2] = 0
    ) -> dict[str, Any]:
        """Get a dict of debugging information about the settings instance."""
        return get_debug_info(settings=self, verbosity=verbosity, key=key)

    @classmethod
    def encode(cls, obj: Any) -> Any:
        """Encode an object to a python serializable value."""
        rv = cls.transform(obj, cls._encode, skip_values=False)
        return cls.transform(
            rv, cls._lowerfy, cls._normalize_key, skip_values=True
        )

    @classmethod
    def transform(
        cls,
        obj: T,
        *funcs: Callable[..., Any],
        skip_values: bool = True,
    ) -> T:
        """Apply one or more callables to obj and return the result."""
        rv = obj
        for fn in funcs:
            rv = cls._transform(rv, fn, skip_values=skip_values)
        return rv

    @classmethod
    def _transform(
        cls,
        obj: T,
        fn: Callable[[T], T],
        skip_values: bool = True,
    ):
        if isinstance(obj, dict):
            rv = {}

            for k, v in obj.items():
                k = cls._transform(k, fn, skip_values=False)
                v = cls._transform(v, fn, skip_values=skip_values)
                rv[k] = v

            return rv

        if isinstance(obj, list | set | tuple):
            rv = [cls._transform(v, fn, skip_values=skip_values) for v in obj]

            if isinstance(obj, tuple):
                return tuple(rv)

            if isinstance(obj, set):
                return frozenset(rv)

            return rv

        if skip_values:
            return obj

        return fn(obj)

    @classmethod
    def _encode(cls, obj: Any):
        rv = unparse_conf_data(obj)

        if isinstance(rv, str):
            if rv.startswith("@none"):
                rv = rv.strip()

            return rv

        if isinstance(rv, Path):
            return str(rv)

        return to_jsonable_python(rv)

    @classmethod
    def _lowerfy(cls, obj: Any):
        if isinstance(obj, str):
            return obj.lower()
        else:
            return obj

    @classmethod
    def _normalize_key(cls, obj: Any):
        if isinstance(obj, str):
            return (
                obj.lower()
                .replace("_for_dynaconf", "")
                .replace("dynaconf", "")
            )
        return obj
