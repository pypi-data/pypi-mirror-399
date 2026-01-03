"""Click command group that exposes configuration management workflows."""

from __future__ import annotations

from textwrap import dedent

from dynaconf.utils.boxing import DynaBox
import rich
from rich.syntax import Syntax
from rich.json import JSON
import rich_click as click

from socx import (
    group,
    command,
    console,
    print_with_pager,
    settings,
    get_logger,
    print_outputs,
)


logger = get_logger(__name__)


@group()
def cli():
    """Get, set, inspect, or debug configuration settings."""


@command(parent=cli)
@click.option(
    "--user",
    "-u",
    is_flag=True,
    type=click.BOOL,
    default=False,
    help=f"""
        Edit user configuration file at '{settings.paths.USER_CONFIG_FILE}'
        instead of the default local .socx.yaml file.
    """.strip(),
)
def edit(user: bool):
    """Interactively edit configuration settings in your preferred editor."""
    from socx_plugins.config.edit import edit as _edit

    _edit(settings.paths.USER_CONFIG_FILE if user else None)


@command(parent=cli)
@click.option(
    "--pager",
    "-p",
    is_flag=True,
    default=False,
    show_default=True,
    help="Display the output in a pager.",
)
def tree(pager: bool):
    """Print a pretty tree structure of all loaded configurations."""
    print_outputs({"config tree": settings.raw}, pager=pager, title="Tree")


@command(parent=cli)
@click.option(
    "--pager",
    "-p",
    is_flag=True,
    default=False,
    show_default=True,
    help="Display the output in a pager.",
)
@click.argument(
    "field",
    type=click.STRING,
    default=None,
    required=False,
    metavar="[field]",
    help="The configuration field to debug.",
)
@click.pass_context
def debug(ctx: click.Context, pager: bool, field: str | None):
    """Dump cli debug info and modification history."""
    if field and field not in settings:
        ctx.fail(f"No such field: {field}")

    output = settings.get_debug_info(key=field, verbosity=2)
    if not pager:
        console.print(output)
    else:
        print_with_pager(output)


@command(parent=cli)
@click.option(
    "--limit",
    "-n",
    "limit",
    nargs=1,
    default=0,
    required=False,
    type=click.IntRange(min=0),
    metavar="integer range",
    show_default=True,
    help="""
    Number of history entries to show. A value of 0 will show all entries.
    """,
)
@click.option(
    "--format",
    "-f",
    "format_",
    nargs=1,
    type=click.Choice(["yaml", "toml", "json"]),
    help="Specify a format for dumping configurations.",
    default="yaml",
    show_default=True,
)
@click.option(
    "--pager",
    "-p",
    is_flag=True,
    default=False,
    show_default=True,
    help="Display the output in a pager.",
)
@click.argument(
    "key",
    type=click.STRING,
    required=False,
    metavar="[key]",
    help="""
    An optional field to show history for.
    If not provided, the full history will be shown.
    """,
)
def history(limit: int, format_: str, pager: bool, key: str | None = None):
    """Print configuration settings modification history."""

    def noop(*args, **kwargs):
        return ""

    history = []
    entries = settings.encode(settings.get_history(key=key, limit=limit))
    for entry in entries:
        code = getattr(DynaBox(entry), f"to_{format_}", noop)()
        if format_ == "json":
            code = JSON(code).text.plain
        history.append(Syntax(code=code, lexer=format_, theme="ansi_dark"))
    print_outputs(*history, pager=pager, title="Settings History")


@command(parent=cli)
def inspect():
    """Inspect the current settings instance and print the results."""
    rich.inspect(
        settings,
        title="Settings",
        help=True,
        docs=True,
        value=True,
        dunder=False,
        private=True,
        methods=True,
        console=console,
    )


@command(
    "get",
    parent=cli,
    no_args_is_help=True,
    help=dedent("""
    Get the current value of a configuration field.\b\n

    > **Common Fields**:
    {}
    """).format(
        "\n".join(
            sorted(
                f"> - {key.lower()}"
                for key in settings
                if not key.startswith("_") and "dynaconf" not in key.lower()
            )
        )
    ),
)
@click.option(
    "--pager",
    "-p",
    is_flag=True,
    default=False,
    show_default=True,
    help="Display the output in a pager.",
)
@click.argument(
    "field",
    type=click.STRING,
    required=True,
    metavar="<field>",
    help="The configuration field to be read.",
)
@click.pass_context
def get(ctx: click.Context, pager: bool, field: str):
    """Get the value of a configuration field in a pretty tree format."""
    if field not in settings and not hasattr(settings, field):
        ctx.fail(f"Invalid field: '{field}'")

    obj = settings.get(field) or {field: getattr(settings, field)}
    print_outputs(obj, pager=pager, title=field)


@command(parent=cli)
@click.option(
    "--indent-guides",
    "--guides",
    "-i",
    "guides",
    is_flag=True,
    default=False,
    show_default=True,
    help="Show indentation guides in the output.",
)
@click.option(
    "--pager",
    "-p",
    is_flag=True,
    default=False,
    show_default=True,
    help="Display the output in a pager.",
)
@click.option(
    "--format",
    "-f",
    "format_",
    nargs=1,
    type=click.Choice(["yaml", "toml", "json"]),
    help="Specify a format for dumping configrations.",
    default="yaml",
    show_default=True,
)
@click.argument(
    "field",
    default=None,
    type=click.STRING,
    metavar="[field]",
    help="An optional name of the configuration field to be shown",
    required=False,
)
@click.pass_context
def dump(
    ctx: click.Context,
    pager: bool,
    guides: bool,
    format_: str,
    field: str | None,
) -> None:
    """Dump the current settings configurations in the specified format."""

    def noop(*args, **kwargs):
        return ""

    if field and field not in settings:
        ctx.fail(f"No such field: {field}")

    text = getattr(settings, f"to_{format_}", noop)(field)

    if format_ == "json":
        text = JSON(text).text.plain

    syntax = Syntax(
        code=text,
        lexer=format_,
        theme="ansi_dark",
        tab_size=2,
        indent_guides=guides,
    )

    print_outputs(syntax, pager=pager, title=field)
