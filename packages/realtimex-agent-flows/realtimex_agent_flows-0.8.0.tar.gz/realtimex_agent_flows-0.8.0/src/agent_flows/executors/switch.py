"""SwitchExecutor for switch-case flow execution."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import SwitchExecutorConfig
from agent_flows.models.flow import FlowStep
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class SwitchExecutor(BaseExecutor):
    """Executor for switch-case flow execution."""

    def __init__(self) -> None:
        """Initialize the switch executor."""
        self.interpolator = VariableInterpolator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["variable", "cases"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return ["defaultBlocks", "resultVariable", "directOutput"]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate switch configuration.

        Args:
            config: Step configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid (Pydantic validation)
            ConfigurationError: If configuration is invalid (other errors)
        """
        try:
            # Use Pydantic model for comprehensive validation
            SwitchExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Switch executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute switch logic.

        Args:
            config: Step configuration containing switch variable and cases
            context: Execution context

        Returns:
            ExecutorResult with switch execution results

        Raises:
            ExecutorError: If switch execution fails
        """
        start_time = time.time()

        try:
            # Check if this is target step mode (test mode inspection)
            is_target_step_mode = config.get("__target_step_mode__", False)

            # Validate and parse configuration
            validated_config = SwitchExecutorConfig(**config)

            log.info(
                "Starting switch execution",
                cases_count=len(validated_config.cases),
                has_default=bool(validated_config.defaultBlocks),
                target_step_mode=is_target_step_mode,
            )

            # The config is already interpolated by the StepExecutionService.
            # The 'variable' field contains the actual value to switch on.
            switch_value = validated_config.variable

            log.debug(
                "Switch variable evaluated",
                variable=validated_config.variable,
                value=switch_value,
                value_type=type(switch_value).__name__,
            )

            # Find matching case
            matched_case, case_index = self._find_matching_case(
                validated_config.cases, switch_value
            )

            condition_result_output: str | int
            matched_case_output: str

            # Determine which blocks to execute
            if matched_case is not None and case_index is not None:
                blocks_to_execute = matched_case.blocks
                condition_result_output = case_index
                matched_case_output = f"case_{matched_case.value}"
                log.info(
                    "Executing matched case blocks",
                    matched_value=matched_case.value,
                    blocks_count=len(blocks_to_execute),
                )
            else:
                blocks_to_execute = validated_config.defaultBlocks
                condition_result_output = "default"
                matched_case_output = "default"
                log.info(
                    "No case matched, executing default blocks",
                    switch_value=switch_value,
                    blocks_count=len(blocks_to_execute),
                )

            # If target step mode, return early with simplified result
            if is_target_step_mode:
                execution_time = time.time() - start_time
                log.info(
                    "Target step mode: returning switch path only", matched_case=matched_case_output
                )
                return ExecutorResult(
                    success=True,
                    data={
                        "condition_result": condition_result_output,
                        "matched_case": matched_case_output,
                    },
                    variables_updated={},
                    execution_time=execution_time,
                    metadata={"step_type": "switch"},
                )

            if context.step_execution_service and context.step_execution_service.streaming_handler:
                if matched_case is not None:
                    content = (
                        f"Switch matched case {matched_case.value} and will execute its blocks"
                    )
                else:
                    content = f"Switch using default blocks for value {switch_value}"
                context.step_execution_service.streaming_handler.stream_step(
                    "Switch", "ToggleLeft", content, content
                )

            # Execute the selected blocks
            execution_results = []
            variables_updated = {}
            target_step_data = None

            for i, block in enumerate(blocks_to_execute):
                try:
                    block_result = await self._execute_block(block, context)
                    execution_results.append(
                        {
                            "block_index": i,
                            "block_type": block.type,
                            "success": block_result.success,
                            "execution_time": block_result.execution_time,
                        }
                    )

                    # Merge variables from block execution
                    if block_result.variables_updated:
                        variables_updated.update(block_result.variables_updated)
                        # Update context variables for subsequent blocks
                        context.variables.update(block_result.variables_updated)

                    # Handle direct output from blocks
                    if block_result.direct_output:
                        log.info(
                            "Block produced direct output, stopping switch execution",
                            block_index=i,
                            block_type=block.type,
                        )
                        break

                    # Handle target step reached in test mode
                    if block_result.metadata and block_result.metadata.get("target_step_reached"):
                        log.info(
                            "Target step reached within switch block",
                            block_index=i,
                            block_type=block.type,
                        )
                        # Propagate existing target data from nested composites, or create from direct target
                        if "target_step_data" in block_result.metadata:
                            target_step_data = block_result.metadata["target_step_data"]
                        else:
                            target_step_data = {
                                "data": block_result.data,
                                "execution_time": block_result.execution_time,
                                "step_type": block_result.metadata.get("step_type", block.type),
                            }
                        break

                except Exception as e:
                    log.warning(
                        "Block execution failed, terminating switch execution",
                        block_index=i,
                        block_type=block.type,
                        error=str(e),
                    )
                    execution_results.append(
                        {
                            "block_index": i,
                            "block_type": block.type,
                            "success": False,
                            "error": str(e),
                        }
                    )
                    # Terminate execution on block failure
                    break

            # Store switch result in variable if specified
            if validated_config.resultVariable:
                variables_updated[validated_config.resultVariable] = matched_case_output

            execution_time = time.time() - start_time

            # Simplified result data - unified with conditional using condition_result
            result_data = {
                "condition_result": condition_result_output,
                "matched_case": matched_case_output,
            }

            log.info(
                "Switch execution completed successfully",
                execution_time=execution_time,
                matched_case=matched_case_output,
            )

            metadata = {"step_type": "switch"}

            # Propagate target_step_reached flag and data if target was reached
            if target_step_data:
                metadata["target_step_reached"] = True
                metadata["target_step_data"] = target_step_data

            return ExecutorResult(
                success=True,
                data=result_data,
                variables_updated=variables_updated,
                direct_output=validated_config.directOutput,
                execution_time=execution_time,
                metadata=metadata,
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise

        except Exception as e:
            raise ExecutorError(f"Switch execution failed: {str(e)}") from e

    def _find_matching_case(self, cases: list, switch_value: Any) -> tuple[Any | None, int | None]:
        """Find the case that matches the switch value.

        Args:
            cases: List of switch cases
            switch_value: Value to match against

        Returns:
            A tuple containing the matching case and its index, or (None, None) if no match found
        """
        for i, case in enumerate(cases):
            if self._values_match(case.value, switch_value):
                return case, i
        return None, None

    def _values_match(self, case_value: Any, switch_value: Any) -> bool:
        """Check if case value matches switch value.

        Args:
            case_value: Value from the case definition
            switch_value: Actual switch variable value

        Returns:
            True if values match
        """
        # Direct equality check
        if case_value == switch_value:
            return True

        # String comparison (case-insensitive for strings)
        if isinstance(case_value, str) and isinstance(switch_value, str):
            return case_value.lower() == switch_value.lower()

        # Type conversion attempts for common cases
        try:
            # Try converting both to strings for comparison
            if str(case_value) == str(switch_value):
                return True
        except Exception:
            pass

        return False

    async def _execute_block(self, block: FlowStep, context: ExecutionContext) -> ExecutorResult:
        """Execute a single block (step).

        Args:
            block: Block definition to execute
            context: Execution context

        Returns:
            ExecutorResult from block execution

        Raises:
            ExecutorError: If block execution fails
        """
        try:
            if not context.step_execution_service:
                raise ExecutorError("Step execution service not available in execution context")

            log.debug(
                "Executing switch block via step execution service",
                block_type=block.type,
                block_id=block.id,
            )
            return await context.step_execution_service.execute_step(
                block, context, context.test_manifest
            )

        except Exception as e:
            raise ExecutorError(f"Failed to execute block of type '{block.type}': {str(e)}") from e

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "switch"
