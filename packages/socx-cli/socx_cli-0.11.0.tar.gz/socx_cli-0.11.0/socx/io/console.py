"""Preconfigured Rich console used throughout SoCX."""

from __future__ import annotations

import contextvars
from typing import Any
from collections import ChainMap
from collections.abc import Iterable

from sh import RunningCommand
import click
import dynaconf
import rich_click
from rich import traceback
from rich.console import Console, RenderableType
from werkzeug.local import LocalProxy

from socx.config._config import settings
from socx.config.formatters import TreeFormatter
from socx.patterns.mixins import ProxyMixin


__all__ = (
    "console",
    "get_console",
    "print_outputs",
    "print_command_outputs",
    "print_with_pager",
)


class ConsoleProxy(ProxyMixin[Console], Console): ...


def print_with_pager(
    *renderables: RenderableType | Iterable[RenderableType],
) -> None:
    """
    Print the given text using the console pager.

    Parameters
    ----------
    *renderables: RenderableType | Iterable[RenderableType]
        The text or renderable objects to display.
    """
    with console.pager(styles=True, links=True):
        console.print(*renderables)


def print_outputs(
    *outputs: str | RenderableType | dict[str, Any],
    pager: bool = False,
    title: str | None = None,
) -> None:
    """
    Print a dictionary of outputs, optionally using a pager.

    Parameters
    ----------
    outputs: dict[str, str]
        Mapping of names to output strings.
    pager: bool, optional
        Whether to use a pager for output. Defaults to True.
    title: str | None, optional
        Optional title for the output. Defaults to None.
    """
    title = title or ""
    formatter = TreeFormatter()
    for output in list(outputs):
        if isinstance(output, dict):
            output = formatter(output, title)

        if not pager:
            console.print(output)
        else:
            print_with_pager(output)


def print_command_outputs(
    outputs: dict[str, RunningCommand],
    pager: bool = True,
    title: str | None = None,
) -> None:
    """
    Print the stdout of a dictionary of RunningCommand objects.

    Parameters
    ----------
    outputs: dict[str, RunningCommand]
        Mapping of names to RunningCommand objects.
    pager: bool = True
        Whether to use a pager for output. Defaults to True.
    title: str | None
        Optional title for the output. Defaults to None.
    """
    cmd_outputs = {
        name: output.stdout.decode() for name, output in outputs.items()
    }
    print_outputs(cmd_outputs, pager=pager, title=title)


def get_console(*args: Any, **kwargs: Any) -> Console:
    """
    Create and configure a rich Console instance with custom settings.

    Parameters
    ----------
    **kwargs: dict[str, Any]
        Additional keyword arguments for Console.

    Returns
    -------
    Console:
        Configured Console instance.
    """
    kwargs = dict(ChainMap(kwargs, settings.console.init))
    console = Console(*args, **kwargs)
    traceback.install(
        console=console,
        suppress=[click, rich_click, dynaconf],
        **(settings.console.traceback),
    )
    return console


_console: Console = get_console()

_console_cv = contextvars.ContextVar[Console]("console")

_console_cv.set(_console)

console: ConsoleProxy = LocalProxy(  # type: ignore[assignment]
    _console_cv,
    unbound_message="""
    Working outside of application context.

    Attempted to use functionality that expected a current application to
    be set. To solve this, set up an app context.
    """,
)
