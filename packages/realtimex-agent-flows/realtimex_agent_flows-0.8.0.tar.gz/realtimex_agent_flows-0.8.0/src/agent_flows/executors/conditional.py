"""ConditionalExecutor for conditional flow execution."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors.conditional import ConditionalExecutorConfig
from agent_flows.models.flow import FlowStep
from agent_flows.models.shared import ConditionDefinition
from agent_flows.utils.condition_evaluator import ConditionEvaluator
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class ConditionalExecutor(BaseExecutor):
    """Executor for conditional flow execution."""

    def __init__(self) -> None:
        """Initialize the conditional executor."""
        self.interpolator = VariableInterpolator()
        self.condition_evaluator = ConditionEvaluator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["condition"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return ["truePath", "falsePath", "resultVariable", "directOutput"]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate conditional configuration.

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
            ConditionalExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Conditional executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute conditional logic.

        Args:
            config: Step configuration containing condition and blocks
            context: Execution context

        Returns:
            ExecutorResult with conditional execution results

        Raises:
            ExecutorError: If conditional execution fails
        """
        start_time = time.time()

        try:
            # Check if this is target step mode (test mode inspection)
            is_target_step_mode = config.get("__target_step_mode__", False)

            # Validate and parse configuration
            validated_config = ConditionalExecutorConfig(**config)

            log.info(
                "Starting conditional execution",
                condition_type=type(validated_config.condition).__name__,
                target_step_mode=is_target_step_mode,
            )

            # Emit conditional execution streaming update
            if context.step_execution_service.streaming_handler:
                task = "Evaluate condition"
                content = "Checking condition and executing appropriate path"
                context.step_execution_service.streaming_handler.stream_step(
                    "Conditional", "GitBranch", task, content
                )

            # Evaluate the condition
            condition_result = await self._evaluate_condition(validated_config.condition, context)

            # If target step mode, return early with simplified result
            if is_target_step_mode:
                execution_time = time.time() - start_time
                log.info(
                    "Target step mode: returning condition result only",
                    condition_result=condition_result,
                )
                return ExecutorResult(
                    success=True,
                    data={"condition_result": condition_result},
                    variables_updated={},
                    execution_time=execution_time,
                    metadata={"step_type": "conditional"},
                )

            log.debug(
                "Condition evaluated",
                condition_result=condition_result,
                condition_type=type(validated_config.condition).__name__,
            )

            # Determine which blocks to execute
            blocks_to_execute = (
                validated_config.truePath if condition_result else validated_config.falsePath
            )

            log.info(
                "Executing conditional blocks",
                condition_result=condition_result,
                blocks_count=len(blocks_to_execute),
                path_taken="true" if condition_result else "false",
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
                            "Block produced direct output, stopping conditional execution",
                            block_index=i,
                            block_type=block.type,
                        )
                        break

                    # Handle target step reached in test mode
                    if block_result.metadata and block_result.metadata.get("target_step_reached"):
                        log.info(
                            "Target step reached within conditional block",
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
                        "Block execution failed, terminating conditional execution",
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

            # Store condition result in variable if specified
            if validated_config.resultVariable:
                variables_updated[validated_config.resultVariable] = condition_result

            execution_time = time.time() - start_time

            # Simplified result data - only essential information
            result_data = {"condition_result": condition_result}

            log.info(
                "Conditional execution completed",
                execution_time=execution_time,
                condition_result=condition_result,
            )

            metadata = {"step_type": "conditional"}

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
            raise ExecutorError(f"Conditional execution failed: {str(e)}") from e

    async def _evaluate_condition(
        self, condition: ConditionDefinition, context: ExecutionContext
    ) -> bool:
        """Evaluate a condition against the current variables.

        Args:
            condition: Condition definition to evaluate
            context: Execution context with variables

        Returns:
            Boolean result of condition evaluation

        Raises:
            ExecutorError: If condition evaluation fails
        """
        try:
            return await self.condition_evaluator.evaluate(condition, context.variables)
        except Exception as e:
            raise ExecutorError(f"Failed to evaluate condition: {str(e)}") from e

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
                "Executing conditional block via step execution service",
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
        return "conditional"
