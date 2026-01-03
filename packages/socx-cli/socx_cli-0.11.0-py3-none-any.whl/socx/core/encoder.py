from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Encoder[T](ABC):
    """Generic protocol for converting values into configuration payloads."""

    @classmethod
    @abstractmethod
    def encode(cls, obj: T, *args: Any, **kwargs: Any) -> str:
        """Encode obj to ``str`` of the specified format_."""
        ...
