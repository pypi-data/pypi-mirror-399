"""Serialization helpers used when bootstrapping configuration objects."""

from __future__ import annotations

from types import ModuleType
from typing import Any, override

from pydantic_core import to_jsonable_python
from dynaconf import LazySettings
from dynaconf.utils.boxing import DynaBox

from socx.core.serializer import Serializer


class ModuleSerializer(Serializer[ModuleType]):
    """Serialize module globals into a Dynaconf-ready mapping."""

    @classmethod
    @override
    def serialize(
        cls, obj: ModuleType, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        name = obj.__name__.rpartition(".")[-1]
        attr_names = getattr(obj, "__all__", ())
        attrs = {k: v for k, v in vars(obj).items() if k in attr_names}
        attrs = to_jsonable_python(attrs)
        return {name: attrs}


class SettingsSerializer(Serializer[LazySettings]):
    @classmethod
    @override
    def serialize(
        cls,
        obj: LazySettings,
        key: str | None = None,
        merge: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> DynaBox:
        """Serialize a ``LazySettings`` obj into a python ``dict``."""
        if key is None:
            return obj.to_dict()
        return obj.get(key, cast=False, fresh=True)
