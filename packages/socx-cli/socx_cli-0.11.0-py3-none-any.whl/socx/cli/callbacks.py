"""Rich-Click callbacks used by the SoCX CLI global options."""

from __future__ import annotations

import os
import logging
from typing import Any
from pathlib import Path

from rich_click import Context
from rich_click import Parameter
from rich_click import RichContext

import socx.io.log as log
from socx.io.console import console
from socx.io.decorators import log_it
from socx.config._config import settings


logger = logging.getLogger(__name__)


@log_it(logger=logger)
def param_cb(_: Context, param: Parameter, value: Any) -> Any:
    """Update settings to the value of a user-specified CLI parameter."""
    settings.cli.params[param.name] = value
    return value


@log_it(logger=logger)
def multi_param_cb(_: Context, param: Parameter, value: Any) -> Any:
    """Update settings to the value of a user-specified CLI parameter."""
    settings.cli.params[param.name].append(value)
    return value


@log_it(logger=logger)
def debug_cb(_: Context, param: Parameter, value: bool) -> bool:
    """Enable debug logging and persist the CLI switch to settings."""
    settings.cli.params[param.name] = value
    if value:
        log.set_level(log.Level.DEBUG)
        settings.cli.params["verbosity"] = log.get_level().name
    return value


@log_it(logger=logger)
def color_cb(ctx: RichContext, param: Parameter, value: bool) -> bool:
    """Enable color logging and persist the CLI switch to settings."""
    ctx.console = console
    console.no_color = not value
    ctx.console.no_color = not value
    settings.cli.params[param.name] = value
    if not value:
        os.environ["NO_COLOR"] = "true"
    return value


@log_it(logger=logger)
def configure_cb(_: Context, param: Parameter, value: str) -> str:
    """Toggle whether user overrides should be merged into settings."""
    from socx.config._config import (
        _settings_cv,
        get_settings,
    )

    settings.cli.params[param.name] = value

    if value:
        _settings_cv.set(
            get_settings(user_overrides=True, local_overrides=True)
        )
    else:
        _settings_cv.set(get_settings())

    settings.cli.params[param.name] = value
    return value


@log_it(logger=logger)
def verbosity_cb(_: Context, param: Parameter, value: str) -> str:
    """Update the global log level while respecting existing overrides."""
    level = log.Level[value.upper()]
    if not settings.cli.params.debug:
        log.set_level(level)
    settings.cli.params[param.name] = log.get_level().name
    return settings.cli.params[param.name]


@log_it(logger=logger)
def config_files_cb(
    _: Context,
    param: Parameter,
    value: tuple[Path, ...],
) -> tuple[Path, ...]:
    if value:
        settings.cli.params[param.name].extend(value)
        settings.settings_file.extend(value)
        settings.dynaconf_include.extend(value)
        settings.load_file(value)

    return value
