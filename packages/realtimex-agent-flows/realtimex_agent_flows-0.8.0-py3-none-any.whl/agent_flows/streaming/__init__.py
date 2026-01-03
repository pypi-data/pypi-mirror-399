"""Streaming module for real-time flow execution feedback."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .handler import StreamingHandler  # noqa: F401


def __getattr__(name: str):
    """Lazily resolve streaming components to avoid heavyweight imports."""
    if name == "StreamingHandler":
        from .handler import StreamingHandler as _StreamingHandler

        globals()[name] = _StreamingHandler
        return _StreamingHandler
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = ["StreamingHandler"]
