"""Flow discovery, loading, and caching."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cache import FlowCache
    from .loader import FlowLoader
    from .registry import FlowRegistry


def __getattr__(name: str) -> type:
    """Lazy import for public API classes."""
    if name == "FlowCache":
        from .cache import FlowCache

        return FlowCache
    if name == "FlowLoader":
        from .loader import FlowLoader

        return FlowLoader
    if name == "FlowRegistry":
        from .registry import FlowRegistry

        return FlowRegistry
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["FlowCache", "FlowLoader", "FlowRegistry"]
