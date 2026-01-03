"""LoopExecutor for iterative flow execution."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors.loop import LoopExecutorConfig
from agent_flows.models.flow import FlowStep
from agent_flows.models.shared import ConditionDefinition, LoopType
from agent_flows.utils.condition_evaluator import ConditionEvaluator
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class LoopExecutor(BaseExecutor):
    """Executor for iterative loop execution."""

    def __init__(self) -> None:
        """Initialize the loop executor."""
        self.interpolator = VariableInterpolator()
        self.condition_evaluator = ConditionEvaluator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["loopType", "loopBlocks"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return [
            "resultVariable",
            "maxIterations",
            "directOutput",
            "startValue",
            "endValue",
            "stepValue",
            "counterVariable",
            "condition",
            "iterableVariable",
            "itemVariable",
            "indexVariable",
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate loop configuration.

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
            LoopExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Loop executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute loop logic.

        Args:
            config: Step configuration containing loop type and blocks
            context: Execution context

        Returns:
            ExecutorResult with loop execution results

        Raises:
            ExecutorError: If loop execution fails
        """
        start_time = time.time()

        try:
            # Validate and parse configuration
            # Note: Config is already interpolated by StepExecutionService, with loopBlocks preserved
            validated_config = LoopExecutorConfig(**config)

            # Emit loop execution streaming update
            if context.step_execution_service.streaming_handler:
                task = f"Execute {validated_config.loopType.value.lower()} loop"
                content = (
                    f"Processing loop with {len(validated_config.loopBlocks)} steps per iteration"
                )
                context.step_execution_service.streaming_handler.stream_step(
                    "Loop", "RotateCw", task, content
                )

            log.info(
                "Starting loop execution",
                loop_type=validated_config.loopType.value,
                max_iterations=validated_config.maxIterations,
            )

            # Execute the appropriate loop type
            if validated_config.loopType == LoopType.FOR:
                result = await self._execute_for_loop(validated_config, context)
            elif validated_config.loopType == LoopType.WHILE:
                result = await self._execute_while_loop(validated_config, context)
            elif validated_config.loopType == LoopType.FOR_EACH:
                result = await self._execute_foreach_loop(validated_config, context)
            else:
                raise ExecutorError(f"Unsupported loop type: {validated_config.loopType}")

            execution_time = time.time() - start_time

            log.info(
                "Loop execution completed",
                iterations_completed=result["iterations_completed"],
                successful_iterations=result["successful_iterations"],
            )

            # Extract clean iteration results as main data
            clean_iteration_results = []
            for iteration_result in result.get("iteration_results", []):
                if iteration_result.get("success") and "variables_updated" in iteration_result:
                    # Extract only the variables updated in this iteration
                    clean_iteration_results.append(iteration_result["variables_updated"])
                else:
                    # For failed iterations, include minimal error info
                    clean_iteration_results.append(
                        {"success": False, "error": iteration_result.get("error", "Unknown error")}
                    )

            metadata = {
                "loop_type": validated_config.loopType.value,
                "iterations_completed": result["iterations_completed"],
                "successful_iterations": result["successful_iterations"],
                "step_type": "loop",
            }

            # Propagate target_step_reached flag and data if target was reached
            if result.get("target_step_data"):
                metadata["target_step_reached"] = True
                metadata["target_step_data"] = result["target_step_data"]

            return ExecutorResult(
                success=True,
                data=clean_iteration_results,  # Clean array of iteration variable updates
                variables_updated=result.get("variables_updated", {}),
                direct_output=validated_config.directOutput,
                execution_time=execution_time,
                metadata=metadata,
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise

        except Exception as e:
            raise ExecutorError(f"Loop execution failed: {str(e)}") from e

    async def _execute_for_loop(
        self, config: LoopExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Execute a for loop.

        Args:
            config: Validated loop configuration
            context: Execution context

        Returns:
            Dictionary with loop execution results
        """
        # Values are already interpolated in the main execute method
        start_val = self._resolve_value(config.startValue, context.variables)
        end_val = self._resolve_value(config.endValue, context.variables)
        step_val = self._resolve_value(config.stepValue, context.variables)

        iterations_completed = 0
        successful_iterations = 0
        iteration_results = []
        variables_updated = {}
        target_step_data = None

        # Execute loop iterations
        current_value = start_val
        while (
            (step_val > 0 and current_value <= end_val)
            or (step_val < 0 and current_value >= end_val)
        ) and iterations_completed < config.maxIterations:
            # Set counter variable
            context.variables[config.counterVariable] = current_value

            # Execute blocks for this iteration
            iteration_result = await self._execute_iteration_blocks(
                config.loopBlocks, context, iterations_completed
            )

            iteration_results.append(iteration_result)
            iterations_completed += 1

            if iteration_result["success"]:
                successful_iterations += 1
                # Merge variables from iteration
                if iteration_result.get("variables_updated"):
                    variables_updated.update(iteration_result["variables_updated"])

            # Check for early termination
            if iteration_result.get("direct_output") or iteration_result.get("target_step_reached"):
                if iteration_result.get("target_step_data"):
                    target_step_data = iteration_result["target_step_data"]
                break

            current_value += step_val

        # Store clean results in result variable if specified
        if config.resultVariable:
            # Extract clean iteration results for the result variable
            clean_results = []
            for iteration_result in iteration_results:
                if iteration_result.get("success") and "variables_updated" in iteration_result:
                    clean_results.append(iteration_result["variables_updated"])
                else:
                    clean_results.append(
                        {"success": False, "error": iteration_result.get("error", "Unknown error")}
                    )
            variables_updated[config.resultVariable] = clean_results

        return {
            "loop_type": "for",
            "iterations_completed": iterations_completed,
            "successful_iterations": successful_iterations,
            "iteration_results": iteration_results,
            "variables_updated": variables_updated,
            "final_counter_value": current_value - step_val,
            "target_step_data": target_step_data,
        }

    async def _execute_while_loop(
        self, config: LoopExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Execute a while loop.

        Args:
            config: Validated loop configuration
            context: Execution context

        Returns:
            Dictionary with loop execution results
        """
        iterations_completed = 0
        successful_iterations = 0
        iteration_results = []
        variables_updated = {}
        target_step_data = None

        # Execute while loop
        while iterations_completed < config.maxIterations:
            # Evaluate condition
            condition_result = await self._evaluate_condition(config.condition, context.variables)

            if not condition_result:
                break

            # Execute blocks for this iteration
            iteration_result = await self._execute_iteration_blocks(
                config.loopBlocks, context, iterations_completed
            )

            iteration_results.append(iteration_result)
            iterations_completed += 1

            if iteration_result["success"]:
                successful_iterations += 1
                # Merge variables from iteration
                if iteration_result.get("variables_updated"):
                    variables_updated.update(iteration_result["variables_updated"])

            # Check for early termination
            if iteration_result.get("direct_output") or iteration_result.get("target_step_reached"):
                if iteration_result.get("target_step_data"):
                    target_step_data = iteration_result["target_step_data"]
                break

        # Store clean results in result variable if specified
        if config.resultVariable:
            # Extract clean iteration results for the result variable
            clean_results = []
            for iteration_result in iteration_results:
                if iteration_result.get("success") and "variables_updated" in iteration_result:
                    clean_results.append(iteration_result["variables_updated"])
                else:
                    clean_results.append(
                        {"success": False, "error": iteration_result.get("error", "Unknown error")}
                    )
            variables_updated[config.resultVariable] = clean_results

        return {
            "loop_type": "while",
            "iterations_completed": iterations_completed,
            "successful_iterations": successful_iterations,
            "iteration_results": iteration_results,
            "variables_updated": variables_updated,
            "target_step_data": target_step_data,
        }

    async def _execute_foreach_loop(
        self, config: LoopExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Execute a forEach loop.

        Args:
            config: Validated loop configuration
            context: Execution context

        Returns:
            Dictionary with loop execution results
        """
        # The iterable is already resolved through interpolation
        iterable = config.iterableVariable

        if not hasattr(iterable, "__iter__") or isinstance(iterable, str | bytes):
            raise ExecutorError(f"Iterable variable is not iterable: {type(iterable)}")

        iterations_completed = 0
        successful_iterations = 0
        iteration_results = []
        variables_updated = {}
        target_step_data = None

        # Execute forEach loop
        for index, item in enumerate(iterable):
            if iterations_completed >= config.maxIterations:
                break

            # Set item and index variables
            context.variables[config.itemVariable] = item
            if config.indexVariable:
                context.variables[config.indexVariable] = index

            # Execute blocks for this iteration
            iteration_result = await self._execute_iteration_blocks(
                config.loopBlocks, context, iterations_completed
            )

            iteration_results.append(iteration_result)
            iterations_completed += 1

            if iteration_result["success"]:
                successful_iterations += 1
                # Merge variables from iteration
                if iteration_result.get("variables_updated"):
                    variables_updated.update(iteration_result["variables_updated"])

            # Check for early termination
            if iteration_result.get("direct_output") or iteration_result.get("target_step_reached"):
                if iteration_result.get("target_step_data"):
                    target_step_data = iteration_result["target_step_data"]
                break

        # Store clean results in result variable if specified
        if config.resultVariable:
            # Extract clean iteration results for the result variable
            clean_results = []
            for iteration_result in iteration_results:
                if iteration_result.get("success") and "variables_updated" in iteration_result:
                    clean_results.append(iteration_result["variables_updated"])
                else:
                    clean_results.append(
                        {"success": False, "error": iteration_result.get("error", "Unknown error")}
                    )
            variables_updated[config.resultVariable] = clean_results

        return {
            "loop_type": "forEach",
            "iterations_completed": iterations_completed,
            "successful_iterations": successful_iterations,
            "iteration_results": iteration_results,
            "variables_updated": variables_updated,
            "target_step_data": target_step_data,
        }

    async def _execute_iteration_blocks(
        self, blocks: list[FlowStep], context: ExecutionContext, iteration: int
    ) -> dict[str, Any]:
        """Execute blocks for a single iteration.

        Args:
            blocks: List of blocks to execute
            context: Execution context
            iteration: Current iteration number

        Returns:
            Dictionary with iteration execution results
        """
        block_results = []
        variables_updated = {}
        success = True
        error = None

        for i, block in enumerate(blocks):
            try:
                block_result = await self._execute_block(block, context)
                block_results.append(
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
                        "Block produced direct output, stopping iteration",
                        iteration=iteration + 1,
                        block_index=i,
                        block_type=block.type,
                    )
                    return {
                        "success": True,
                        "block_results": block_results,
                        "variables_updated": variables_updated,
                        "direct_output": True,
                    }

                # Handle target step reached in test mode
                if block_result.metadata and block_result.metadata.get("target_step_reached"):
                    log.info(
                        "Target step reached within loop iteration",
                        iteration=iteration + 1,
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
                    return {
                        "success": True,
                        "block_results": block_results,
                        "variables_updated": variables_updated,
                        "target_step_reached": True,
                        "target_step_data": target_step_data,
                    }

            except Exception as e:
                log.warning(
                    "Block execution failed in loop iteration",
                    iteration=iteration + 1,
                    block_index=i,
                    block_type=block.type,
                    error=str(e),
                )
                block_results.append(
                    {
                        "block_index": i,
                        "block_type": block.type,
                        "success": False,
                        "error": str(e),
                    }
                )
                success = False
                error = str(e)
                # Continue with next block instead of terminating iteration
                continue

        return {
            "success": success,
            "block_results": block_results,
            "variables_updated": variables_updated,
            "error": error,
        }

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
                "Executing loop block via step execution service",
                block_type=block.type,
                block_id=block.id,
            )
            return await context.step_execution_service.execute_step(
                block, context, context.test_manifest
            )

        except Exception as e:
            raise ExecutorError(f"Failed to execute block of type '{block.type}': {str(e)}") from e

    def _resolve_value(self, value: Any, variables: dict[str, Any]) -> int:
        """Resolve a value to integer (already interpolated).

        Args:
            value: Value to resolve (already interpolated)
            variables: Available variables (unused, kept for compatibility)

        Returns:
            Resolved integer value

        Raises:
            ValueError: If value cannot be resolved to an integer
        """
        if isinstance(value, int):
            return value

        if isinstance(value, str):
            try:
                return int(value)
            except ValueError as e:
                raise ValueError(f"Cannot convert '{value}' to integer") from e

        raise ValueError(f"Unsupported value type: {type(value)}")

    async def _evaluate_condition(
        self, condition: ConditionDefinition, variables: dict[str, Any]
    ) -> bool:
        """Evaluate a condition definition.

        Args:
            condition: Condition definition to evaluate
            variables: Available variables

        Returns:
            Boolean result of condition evaluation

        Raises:
            ValueError: If condition cannot be evaluated
        """
        try:
            return await self.condition_evaluator.evaluate(condition, variables)
        except Exception as e:
            raise ValueError(f"Failed to evaluate condition: {str(e)}") from e

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "loop"
