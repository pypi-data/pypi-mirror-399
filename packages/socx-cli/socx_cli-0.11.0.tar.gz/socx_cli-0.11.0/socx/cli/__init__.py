"""Expose primary CLI entry points and shared helpers."""

__all__ = (
    "cfg",
    "cli",
    "opts",
    "debug",
    "color",
    "configure",
    "verbosity",
    "config_files",
    "param_cb",
    "debug_cb",
    "color_cb",
    "verbosity_cb",
    "configure_cb",
    "multi_param_cb",
    "config_files_cb",
    "Decorator",
    "AnyCallable",
)


import socx.cli.cfg as cfg

from socx.cli.cli import cli as cli

from socx.cli.types import Decorator as Decorator
from socx.cli.types import AnyCallable as AnyCallable

from socx.cli.params import opts as opts
from socx.cli.params import debug as debug
from socx.cli.params import color as color
from socx.cli.params import group as group
from socx.cli.params import command as command
from socx.cli.params import configure as configure
from socx.cli.params import verbosity as verbosity
from socx.cli.params import config_files as config_files

from socx.cli.callbacks import debug_cb as debug_cb
from socx.cli.callbacks import param_cb as param_cb
from socx.cli.callbacks import color_cb as color_cb
from socx.cli.callbacks import verbosity_cb as verbosity_cb
from socx.cli.callbacks import configure_cb as configure_cb
from socx.cli.callbacks import multi_param_cb as multi_param_cb
from socx.cli.callbacks import config_files_cb as config_files_cb
