"""Flow execution orchestration."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .executor import FlowExecutor
    from .registry import ExecutorRegistry
    from .runner import FlowRunner
    from .state import ExecutionResult, ExecutionStateTracker
    from .step_executor import StepExecutionService

__all__ = [
    "FlowExecutor",
    "ExecutorRegistry",
    "FlowRunner",
    "StepExecutionService",
    "ExecutionResult",
    "ExecutionStateTracker",
]


def __getattr__(name: str) -> type:
    """Lazy import for execution module classes."""
    if name == "FlowExecutor":
        from .executor import FlowExecutor

        return FlowExecutor
    if name == "ExecutorRegistry":
        from .registry import ExecutorRegistry

        return ExecutorRegistry
    if name == "FlowRunner":
        from .runner import FlowRunner

        return FlowRunner
    if name == "StepExecutionService":
        from .step_executor import StepExecutionService

        return StepExecutionService
    if name == "ExecutionResult":
        from .state import ExecutionResult

        return ExecutionResult
    if name == "ExecutionStateTracker":
        from .state import ExecutionStateTracker

        return ExecutionStateTracker
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
