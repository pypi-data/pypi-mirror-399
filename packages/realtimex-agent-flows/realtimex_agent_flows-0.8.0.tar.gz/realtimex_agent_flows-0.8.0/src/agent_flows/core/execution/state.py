"""Execution state management for flow runs."""

import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from agent_flows.models.execution import ExecutionError, TargetStepResult, TraceEntry


@dataclass(frozen=True)
class ExecutionResult:
    """Immutable result of flow execution.

    Contains all information about a completed flow execution including
    success status, execution metrics, final state, and any errors encountered.
    """

    success: bool
    steps_executed: int
    execution_time: float
    final_variables: dict[str, Any]
    errors: list[ExecutionError]
    direct_output: Any | None
    target_step_result: TargetStepResult | None
    trace: list[TraceEntry] | None
    termination_reason: str | None
    finish_metadata: dict[str, Any] | None


class ExecutionStateTracker:
    """Tracks mutable execution state during flow run.

    Single source of truth for all execution state. Provides clear
    methods for recording execution events and querying current state.

    This class maintains consistency by being the only place where
    execution state is modified during flow execution.
    """

    def __init__(self, initial_variables: dict[str, Any]) -> None:
        """Initialize execution state tracker.

        Args:
            initial_variables: Starting variables for the flow
        """
        self._variables = initial_variables.copy()
        self._start_time = time.monotonic()
        self._steps_executed = 0
        self._errors: list[ExecutionError] = []
        self._direct_output: Any | None = None
        self._target_step_result: TargetStepResult | None = None
        self._termination_reason: str | None = None
        self._finish_metadata: dict[str, Any] | None = None

    # --- State Query Methods ---

    def get_current_variables(self) -> dict[str, Any]:
        """Get current flow variables.

        Returns:
            Copy of current variable state
        """
        return self._variables.copy()

    def get_execution_time(self) -> float:
        """Get elapsed execution time in seconds.

        Returns:
            Elapsed time since execution started
        """
        return time.monotonic() - self._start_time

    def should_stop_execution(self) -> bool:
        """Check if execution should stop due to errors or signals.

        Returns:
            True if execution should stop, False otherwise
        """
        return (
            len(self._errors) > 0
            or self._direct_output is not None
            or self._termination_reason is not None
            or self._target_step_result is not None
        )

    @property
    def success(self) -> bool:
        """Whether execution completed successfully.

        Returns:
            True if no errors occurred, False otherwise
        """
        return len(self._errors) == 0

    @property
    def steps_executed(self) -> int:
        """Number of steps successfully executed.

        Returns:
            Count of completed steps
        """
        return self._steps_executed

    # --- State Update Methods ---

    def record_step_completion(self, step_result: Any) -> None:
        """Record successful step execution.

        Updates execution state with step results including variable updates,
        direct output detection, and termination signals.

        Args:
            step_result: Result from step execution
        """
        self._steps_executed += 1

        # Update variables if provided
        if hasattr(step_result, "variables_updated") and step_result.variables_updated:
            self._variables.update(step_result.variables_updated)

        # Check for direct output
        if hasattr(step_result, "direct_output") and step_result.direct_output:
            self._direct_output = step_result.data

        # Check for termination signal
        if (
            hasattr(step_result, "metadata")
            and step_result.metadata
            and step_result.metadata.get("flow_termination_signal")
        ):
            self._termination_reason = step_result.metadata.get(
                "termination_reason", "Flow termination signal"
            )
            # Store finish metadata for later use in FlowResult
            self._finish_metadata = step_result.metadata

    def record_step_failure(self, step: Any, step_index: int, error: Exception) -> None:
        """Record step execution failure.

        Creates an ExecutionError with full context and adds it to the error list.
        This immediately marks the execution as failed.

        Args:
            step: The failed flow step
            step_index: Index of the failed step
            error: The exception that occurred
        """
        execution_error = ExecutionError(
            message=str(error),
            step_id=step.id,
            step_index=step_index,
            step_type=step.type,
            error_type=type(error).__name__,
            context_variables=self._variables.copy(),
            timestamp=datetime.now(UTC),
        )
        self._errors.append(execution_error)

    def record_target_step_reached(self, step: Any, step_result: Any) -> None:
        """Record that test mode target step was reached.

        Captures the target step result for test mode execution.
        This marks the execution for early termination.

        Args:
            step: The target step
            step_result: Result from target step execution
        """
        self._target_step_result = TargetStepResult(
            step_id=step.id,
            step_type=step.type,
            success=step_result.success,
            execution_time=step_result.execution_time,
            data=step_result.data,
            variables_updated=step_result.variables_updated or {},
        )

    def set_direct_output(self, output: Any) -> None:
        """Set direct output result.

        Marks the execution for termination with direct output.

        Args:
            output: Direct output data from step
        """
        self._direct_output = output

    def set_termination_signal(self, reason: str) -> None:
        """Set flow termination signal.

        Marks the execution for termination with a specific reason.

        Args:
            reason: Human-readable termination reason
        """
        self._termination_reason = reason

    # --- Result Generation ---

    def to_execution_result(self, trace_log: list[TraceEntry] | None = None) -> ExecutionResult:
        """Convert to immutable ExecutionResult.

        Creates a final immutable result containing all execution state.
        This should be called once execution is complete.

        Args:
            trace_log: Optional trace log from ExecutionContext

        Returns:
            Immutable ExecutionResult with final state
        """
        return ExecutionResult(
            success=self.success,
            steps_executed=self._steps_executed,
            execution_time=self.get_execution_time(),
            final_variables=self._variables.copy(),
            errors=self._errors.copy(),
            direct_output=self._direct_output,
            target_step_result=self._target_step_result,
            trace=trace_log.copy() if trace_log else None,
            termination_reason=self._termination_reason,
            finish_metadata=self._finish_metadata.copy() if self._finish_metadata else None,
        )
