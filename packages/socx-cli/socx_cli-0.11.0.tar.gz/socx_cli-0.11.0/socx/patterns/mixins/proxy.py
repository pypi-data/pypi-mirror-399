from __future__ import annotations

from typing import Protocol, TypeVar


T = TypeVar("T", covariant=True)


class ProxyMixin(Protocol[T]):
    def _get_current_object(self) -> T: ...
