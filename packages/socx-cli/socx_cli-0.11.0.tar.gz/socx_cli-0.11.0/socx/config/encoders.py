"""Configuration settings encoders."""

from __future__ import annotations

import box
from typing import Any, Literal, override

from dynaconf import LazySettings

from socx.core.encoder import Encoder
from socx.config.serializers import SettingsSerializer

FormatType = Literal["yaml", "toml", "json"]


def noop_box(*args, **kwargs):
    return box.Box()


def noop_str(*args, **kwargs):
    return ""


class SettingsEncoder(Encoder[LazySettings]):
    @classmethod
    @override
    def encode(
        cls,
        obj: LazySettings,
        key: str | None = None,
        merge: bool = False,
        format_: FormatType | None = None,
        **kwargs: Any,
    ) -> str:
        format_ = format_ or "yaml"
        rv = SettingsSerializer.serialize(obj, key=key, merge=merge, **kwargs)
        return getattr(rv, f"to_{format_}", noop_str)()
