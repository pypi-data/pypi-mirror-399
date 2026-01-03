"""Shared flag definitions and helpers for the SoCX CLI."""

from __future__ import annotations

import logging
from typing import Any, cast
from pathlib import Path
from collections import ChainMap
from collections.abc import Callable

from pydantic import ValidationError
import rich_click as click

from socx.config import settings
from socx.config.schema.plugin import PluginModel
from socx.cli.types import Decorator, GroupType, CommandType, AnyCallable
from socx.cli.callbacks import (
    debug_cb,
    color_cb,
    verbosity_cb,
    configure_cb,
    config_files_cb,
)
from socx.utils.decorators import join_decorators


def command(
    name: str | AnyCallable | None = None,
    cls: type[CommandType] | None = None,
    parent: click.Group | None = None,
    **kwargs: Any,
) -> CommandType | Callable[[AnyCallable], CommandType | click.Command]:
    cls = cls or cast(type[CommandType], click.Command)
    kwargs = dict(ChainMap(kwargs, settings.cli.command))

    def decorator(func: AnyCallable) -> CommandType:
        cmd = click.command(
            name=name if not callable(name) else name.__name__,
            cls=cls,
            **kwargs,
        )(func)

        if parent is not None:
            parent.add_command(cmd)

        return cmd

    return decorator if not callable(name) else decorator(name)


def group(
    name: str | AnyCallable | None = None,
    cls: type[GroupType] | None = None,
    parent: GroupType | None = None,
    **kwargs: Any,
) -> GroupType | Callable[[AnyCallable], GroupType | click.Group]:
    kwargs = dict(ChainMap(kwargs, settings.cli.group))

    def decorator(func: AnyCallable) -> GroupType | click.Group:
        cmd = click.group(
            name=name if not callable(name) else name.__name__,
            cls=cls,
            **kwargs,
        )(func)

        if parent is not None:
            parent.add_command(cmd)

        return cmd

    if callable(name):
        return decorator(name)

    return decorator


color: Decorator = click.option(
    "--color/--no-color",
    "color",
    help="Disable colored output.",
    envvar="SOCX_COLOR",
    default=settings.cli.params.color,
    is_flag=True,
    is_eager=False,
    show_envvar=True,
    show_default=False,
    expose_value=False,
    callback=color_cb,
)


debug: Decorator = click.option(
    "--debug",
    "-d",
    "debug",
    help="Enable debug mode and logging.",
    envvar="SOCX_DEBUG",
    default=settings.cli.params.debug,
    is_flag=True,
    is_eager=False,
    show_envvar=True,
    show_default=True,
    expose_value=False,
    callback=debug_cb,
)


verbosity: Decorator = click.option(
    "--verbosity",
    "-v",
    "verbosity",
    nargs=1,
    help="set the logging verbosity to the specified level.",
    envvar="SOCX_VERBOSITY",
    default=settings.cli.params.verbosity,
    is_eager=False,
    show_envvar=True,
    show_choices=True,
    show_default=True,
    expose_value=False,
    type=click.Choice(
        choices=tuple(logging.getLevelNamesMapping()),
        case_sensitive=False,
    ),
    callback=verbosity_cb,
)

configure: Decorator = click.option(
    "--configure/--no-configure",
    "configure",
    help="Enable/disable loading of user and local configuration files.",
    envvar="SOCX_CONFIGURE",
    default=settings.cli.params.configure,
    is_flag=True,
    is_eager=True,
    show_envvar=True,
    expose_value=False,
    callback=configure_cb,
)

config_files: Decorator = click.option(
    "--config-file",
    "-f",
    "config_files",
    help="""
    Additional configuration file(s) to load.

    Supported file formats are:
    - INI: ".ini"
    - JSON: ".json"
    - YAML: ".yml", ".yaml"
    - TOML: ".toml"
    - Python: ".py"
    """,
    nargs=1,
    default=settings.cli.params.config_files,
    type=click.Path(
        exists=True,
        writable=True,
        readable=True,
        dir_okay=False,
        file_okay=True,
        resolve_path=True,
        path_type=Path,
    ),
    is_eager=False,
    multiple=True,
    metavar="<path>",
    callback=config_files_cb,
    expose_value=False,
)


def opts() -> Decorator:
    """Apply the standard set of global SoCX CLI options."""
    return join_decorators(configure, verbosity, debug, color, config_files)


def panels():
    if settings.rich_click.commands_before_options:
        return join_decorators(*_command_panels(), *_option_panels())
    else:
        return join_decorators(*_option_panels(), *_command_panels())


def option_panels():
    return join_decorators(*_option_panels())


def command_panels():
    return join_decorators(*_command_panels())


def _option_panels():
    return [
        click.option_panel(
            name=panel.name,
            options=panel.options,
        )
        for panel in settings.cli.option_panels
    ]


def _command_panels():
    panel_commands = {}

    for name, plugin in settings.plugins.items():
        try:
            plugin = PluginModel(name=name, **plugin)
        except ValidationError:
            continue

        if not plugin.enabled:
            continue

        panel_commands[plugin.panel] = [
            *panel_commands.get(plugin.panel, []),
            plugin.name,
        ]

    return [
        click.command_panel(name=name, commands=commands)
        for name, commands in panel_commands.items()
    ]
