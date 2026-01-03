"""Core execution engine components."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .execution import ExecutorRegistry, FlowExecutor
    from .flows import FlowLoader, FlowRegistry
    from .resources import VariableInterpolator


def __getattr__(name: str) -> type:
    """Lazy import for execution, flows, and resources submodule classes."""
    if name == "FlowExecutor":
        from .execution import FlowExecutor

        return FlowExecutor
    if name == "ExecutorRegistry":
        from .execution import ExecutorRegistry

        return ExecutorRegistry
    if name == "FlowRegistry":
        from .flows import FlowRegistry

        return FlowRegistry
    if name == "FlowLoader":
        from .flows import FlowLoader

        return FlowLoader
    if name == "VariableInterpolator":
        from .resources import VariableInterpolator

        return VariableInterpolator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["FlowExecutor", "ExecutorRegistry", "VariableInterpolator", "FlowRegistry", "FlowLoader"]
