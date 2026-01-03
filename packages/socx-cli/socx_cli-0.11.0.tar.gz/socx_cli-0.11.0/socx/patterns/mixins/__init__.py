"""Expose mixins supporting visitor traversal and pointer semantics."""

__all__ = (
    "UIDMixin",
    "PtrMixin",
    "ProxyMixin",
)

from socx.patterns.mixins.uid import UIDMixin as UIDMixin
from socx.patterns.mixins.uid import PtrMixin as PtrMixin

from socx.patterns.mixins.proxy import ProxyMixin as ProxyMixin
