"""Flow execution engine for orchestrating step-by-step execution."""

from typing import Any

from agent_flows.core.execution import ExecutionResult, ExecutionStateTracker, StepExecutionService
from agent_flows.models.execution import ExecutionContext
from agent_flows.models.flow import FlowConfig
from agent_flows.models.test import TestManifest
from agent_flows.streaming import StreamingHandler
from agent_flows.utils.logging import execution_context as log_context
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class FlowRunner:
    """Dedicated execution engine for running Agent Flow steps.

    Encapsulates the complexity of step-by-step execution while providing
    a simple, clean interface. Handles all execution state management,
    flow control, and coordination with external services.
    """

    def __init__(
        self,
        step_execution_service: StepExecutionService,
        streaming_handler: StreamingHandler,
    ) -> None:
        """Initialize FlowRunner with execution services.

        Args:
            step_execution_service: Service for executing individual steps
            streaming_handler: Handler for emitting real-time execution events
        """
        self._step_execution_service = step_execution_service
        self._streaming_handler = streaming_handler

    async def run(
        self,
        flow_config: FlowConfig,
        execution_context: ExecutionContext,
        test_manifest: TestManifest | None = None,
    ) -> ExecutionResult:
        """Execute a complete flow and return execution result.

        This is the main entry point for flow execution. Contains the complete
        execution loop with proper state management and error handling.

        Args:
            flow_config: Configuration defining the flow to execute
            execution_context: Execution context with variables and services
            test_manifest: Optional test configuration

        Returns:
            ExecutionResult containing complete execution state

        Raises:
            FlowExecutionError: If flow execution encounters critical errors
        """
        # Initialize execution state tracker (single source of truth)
        state_tracker = ExecutionStateTracker(execution_context.variables)

        # Emit flow started event
        self._streaming_handler.flow_started(flow_name=flow_config.name)

        log.info(
            "Starting flow execution",
            flow_id=flow_config.uuid,
            flow_name=flow_config.name,
            step_count=len(flow_config.steps),
        )

        # Main execution loop
        for step_index, step in enumerate(flow_config.steps):
            if (step.type or "").strip().lower() == "start":
                log.info("Skipping legacy 'start' step", step_id=step.id)
                continue

            # Execute single step with proper context
            should_continue = await self._execute_single_step(
                step=step,
                step_index=step_index,
                execution_context=execution_context,
                state_tracker=state_tracker,
                test_manifest=test_manifest,
            )

            if not should_continue:
                break

        # Finalize execution
        result = state_tracker.to_execution_result(execution_context.trace_log)

        log.info(
            "Flow execution completed",
            flow_id=flow_config.uuid,
            success=result.success,
            steps_executed=result.steps_executed,
            execution_time=result.execution_time,
        )

        # Emit flow completed event
        self._streaming_handler.flow_completed(result.success, result.execution_time)

        return result

    async def _execute_single_step(
        self,
        step: Any,  # FlowStep
        step_index: int,
        execution_context: ExecutionContext,
        state_tracker: ExecutionStateTracker,
        test_manifest: TestManifest | None,
    ) -> bool:
        """Execute a single flow step with proper context and error handling.

        Args:
            step: Flow step to execute
            step_index: Zero-based step index
            flow_id: Flow identifier for logging
            execution_context_obj: Shared execution context
            state_tracker: Mutable state tracker
            test_manifest: Optional test configuration

        Returns:
            True if execution should continue, False if should stop
        """
        # Establish logging context for this step
        with log_context(
            flow_id=execution_context.flow_id,
            step_id=step.id,
            step_index=step_index,
            step_type=step.type,
        ):
            try:
                log.info("Executing step")

                # Update execution context with current state
                execution_context.variables = state_tracker.get_current_variables()
                execution_context.step_index = step_index
                execution_context.step_id = step.id
                execution_context.step_type = step.type

                # Execute the step
                step_result = await self._step_execution_service.execute_step(
                    step, execution_context, test_manifest
                )

                # Handle test mode target step (direct or nested within composite)
                if test_manifest and (
                    test_manifest.target == step.id
                    or (step_result.metadata and step_result.metadata.get("target_step_reached"))
                ):
                    # For nested targets, extract the preserved target data
                    if test_manifest.target != step.id and step_result.metadata:
                        from types import SimpleNamespace

                        target_data = step_result.metadata.get("target_step_data", {})
                        target_step = SimpleNamespace(
                            id=test_manifest.target,
                            type=target_data.get("step_type", "composite_nested"),
                        )
                        # Create a new result with only the target's data
                        from agent_flows.models.execution import ExecutorResult

                        target_result = ExecutorResult(
                            success=step_result.success,
                            data=target_data.get("data", {}),
                            execution_time=target_data.get(
                                "execution_time", step_result.execution_time
                            ),
                            variables_updated=step_result.variables_updated or {},
                        )
                    else:
                        target_step = step
                        target_result = step_result

                    state_tracker.record_target_step_reached(target_step, target_result)
                    log.info("Test mode target step reached, stopping execution")
                    return False

                # Record successful execution
                state_tracker.record_step_completion(step_result)

                log.info("Step completed", execution_time=step_result.execution_time)

                # Check if we should stop execution
                return not state_tracker.should_stop_execution()

            except Exception as e:
                log.error(
                    "Step execution failed",
                    error=str(e),
                    exc_info=True,
                    variables=state_tracker.get_current_variables(),
                )

                # Record failure and stop execution
                state_tracker.record_step_failure(step, step_index, e)
                return False
