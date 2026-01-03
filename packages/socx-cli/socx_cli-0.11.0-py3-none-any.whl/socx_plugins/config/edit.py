"""Interactive configuration editing helpers for the CLI plugin."""

import os
from typing import Literal
from pathlib import Path
from prompt_toolkit import choice
from logging import Logger

import box
import rich_click as click

from socx import console, settings, get_logger
from socx.config.paths import LOCAL_CONFIG_FILENAME


logger: Logger = get_logger(__name__)

FormatType = Literal["yaml", "json", "toml"]


def edit(target_path: Path | None = None, format_: FormatType | None = None):
    """Launch the user's editor with the selected configuration snapshot."""
    format_ = format_ or "yaml"
    includes = [Path(str(p)) for p in settings.includes]
    editor_choices = ["vim", "gvim", "nano"]
    default_editor = settings.get_environ("EDITOR", "vim")

    if default_editor not in editor_choices:
        editor_choices.append(default_editor)

    file_choice = choice(
        message="Which configuration would you like to edit?",
        options=[
            (str(v), v.name if v.name != ".socx.yaml" else str(v))
            for v in includes
        ],
    )
    editor_choice = choice(
        message="Which editor would you like to use?",
        options=[(v, v) for v in editor_choices],
    )

    if str(settings.paths.app_config_dir) in file_choice:
        target_path = target_path or Path.cwd() / LOCAL_CONFIG_FILENAME
    else:
        target_path = target_path or Path(file_choice)

    file_choice = Path(file_choice)
    obj = box.Box.from_yaml(filename=file_choice)

    if target_path.exists() and target_path != file_choice:
        obj.merge_update(obj.from_yaml(filename=target_path))
        text = getattr(
            obj,
            f"to_{format_}",
            file_choice.read_text,
        )()
    else:
        text = file_choice.read_text()

    modified_text = click.edit(
        env=os.environ,
        text=text,
        editor=editor_choice,
        extension=".yaml",
        require_save=True,
    )

    if modified_text:
        target_path.write_text(modified_text)
        console.log(f"settings file written to: '{target_path}'")
        logger.info(f"settings file written to: '{target_path}'")
    else:
        console.log("File was not saved/modified - operation aborted.")
        logger.info("File was not saved/modified - operation aborted.")
