"""Centralized step execution service with test support."""

import time
from typing import Any

from agent_flows.core.execution.registry import ExecutorRegistry
from agent_flows.core.resources import CredentialManager, VariableInterpolator
from agent_flows.exceptions import CredentialError
from agent_flows.models.credentials import CredentialBundle
from agent_flows.models.execution import ExecutionContext, ExecutorResult, TraceEntry
from agent_flows.models.flow import FlowStep
from agent_flows.models.test import TestManifest
from agent_flows.utils.dict_utils import deep_update
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class StepExecutionService:
    """Centralized service for executing flow steps with test support."""

    def __init__(
        self,
        executor_registry: ExecutorRegistry | None = None,
        streaming_handler=None,
        credential_manager: CredentialManager | None = None,
    ) -> None:
        """Initialize the step execution service.

        Args:
            executor_registry: Registry of executors (optional, will create if not provided)
            streaming_handler: Optional streaming handler for real-time progress updates
        """
        self.executor_registry = executor_registry or ExecutorRegistry()
        self.variable_interpolator = VariableInterpolator()
        self.streaming_handler = streaming_handler
        self.credential_manager = credential_manager

    def _add_to_trace(self, step: Any, result: ExecutorResult, context: ExecutionContext) -> None:
        """Add a step execution result to the trace log if tracing is active.

        Args:
            step: The executed step
            result: The execution result
            context: The execution context containing the trace log
        """
        if context.trace_log is not None:
            context.trace_log.append(
                TraceEntry(
                    step_id=step.id,
                    step_type=step.type,
                    success=result.success,
                    execution_time=result.execution_time,
                    data=result.data,
                    variables_updated=result.variables_updated,
                )
            )

    def _preserve_nested_blocks(
        self, step_type: str, config: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Preserve nested blocks from composite executors to enable deferred interpolation.

        For composite executors (switch, conditional, loop), nested block configs should not be
        interpolated when the parent executor's config is interpolated. Instead, blocks
        are interpolated individually when they execute, ensuring they see the latest
        variable state updated by sibling blocks.

        Args:
            step_type: Type of the executor step
            config: Step configuration dict

        Returns:
            Tuple of (config_without_nested_blocks, preserved_blocks)
        """
        if step_type not in ["switch", "conditional", "loop"]:
            return config, {}

        import copy

        preserved_blocks: dict[str, Any] = {}
        config_copy = copy.deepcopy(config)

        if step_type == "switch":
            if "cases" in config_copy:
                preserved_blocks["cases"] = []
                for case in config_copy["cases"]:
                    preserved_blocks["cases"].append({"blocks": case.get("blocks", [])})
                    case["blocks"] = []

            if "defaultBlocks" in config_copy:
                preserved_blocks["defaultBlocks"] = config_copy["defaultBlocks"]
                config_copy["defaultBlocks"] = []

        elif step_type == "conditional":
            if "truePath" in config_copy:
                preserved_blocks["truePath"] = config_copy["truePath"]
                config_copy["truePath"] = []

            if "falsePath" in config_copy:
                preserved_blocks["falsePath"] = config_copy["falsePath"]
                config_copy["falsePath"] = []

        elif step_type == "loop":
            if "loopBlocks" in config_copy:
                preserved_blocks["loopBlocks"] = config_copy["loopBlocks"]
                config_copy["loopBlocks"] = []

        return config_copy, preserved_blocks

    def _restore_nested_blocks(
        self, step_type: str, interpolated_config: dict[str, Any], preserved_blocks: dict[str, Any]
    ) -> dict[str, Any]:
        """Restore un-interpolated nested blocks to the interpolated config.

        Args:
            step_type: Type of the executor step
            interpolated_config: Config that has been interpolated
            preserved_blocks: Preserved un-interpolated nested blocks

        Returns:
            Config with restored nested blocks
        """
        if not preserved_blocks:
            return interpolated_config

        if step_type == "switch":
            if "cases" in preserved_blocks and "cases" in interpolated_config:
                for i, case in enumerate(interpolated_config["cases"]):
                    if i < len(preserved_blocks["cases"]):
                        case["blocks"] = preserved_blocks["cases"][i]["blocks"]

            if "defaultBlocks" in preserved_blocks:
                interpolated_config["defaultBlocks"] = preserved_blocks["defaultBlocks"]

        elif step_type == "conditional":
            if "truePath" in preserved_blocks:
                interpolated_config["truePath"] = preserved_blocks["truePath"]

            if "falsePath" in preserved_blocks:
                interpolated_config["falsePath"] = preserved_blocks["falsePath"]

        elif step_type == "loop":
            if "loopBlocks" in preserved_blocks:
                interpolated_config["loopBlocks"] = preserved_blocks["loopBlocks"]

        return interpolated_config

    async def execute_step(
        self,
        step: FlowStep,
        context: ExecutionContext,
        test_manifest: TestManifest | None = None,
    ) -> ExecutorResult:
        """Execute a single flow step with optional test manifest support.

        Args:
            step: Step configuration
            context: Execution context
            test_manifest: Optional test manifest for pinned results

        Returns:
            ExecutorResult with step results
        """
        step_start = time.time()

        try:
            # Start with a copy of the original config
            step_config = step.config.copy()
            context.resolved_credentials = {}

            # Check for pin and apply overrides or return mocked result
            if test_manifest and test_manifest.has_pin(step.id):
                pinned_result = test_manifest.get_pin(step.id)
                if pinned_result:
                    # Apply config override if it exists
                    if pinned_result.override_config:
                        log.info("Applying configuration override from test pin", step_id=step.id)
                        step_config = deep_update(step_config, pinned_result.override_config)

                    # If variables_updated is present, this is a traditional pin.
                    # Stop execution and return a mocked result.
                    if pinned_result.variables_updated is not None:
                        log.info("Using pinned result for step", step_id=step.id)
                        # Interpolate the potentially modified config to provide context
                        interpolated_config = self.variable_interpolator.interpolate_object(
                            step_config, context.variables
                        )
                        result = pinned_result.to_executor_result(interpolated_config)

                        # Add to trace if tracing is active
                        self._add_to_trace(step, result, context)
                        return result

            # If we reach here, it's either a normal execution or an override_config-only execution.
            # Get executor for step type
            executor = self.executor_registry.get_executor(step.type)

            # For composite executors, preserve nested blocks to enable deferred interpolation
            config_to_interpolate, preserved_blocks = self._preserve_nested_blocks(
                step.type, step_config
            )

            # Interpolate variables in the (potentially modified) step configuration
            interpolated_config = self.variable_interpolator.interpolate_object(
                config_to_interpolate, context.variables
            )

            # Restore un-interpolated nested blocks for composite executors
            interpolated_config = self._restore_nested_blocks(
                step.type, interpolated_config, preserved_blocks
            )

            resolved_credentials = await self._resolve_credentials(interpolated_config)
            if resolved_credentials:
                context.resolved_credentials = resolved_credentials

            # Check if this step is the target in test mode (for composite executors)
            is_target_step = test_manifest and test_manifest.target == step.id
            if is_target_step and step.type in ["conditional", "switch", "loop"]:
                interpolated_config["__target_step_mode__"] = True

            # Execute the step
            result = await executor.execute(interpolated_config, context)

            # Ensure execution time is set
            if not hasattr(result, "execution_time") or result.execution_time == 0:
                result.execution_time = time.time() - step_start

            # Handle result variable assignment
            result_var = interpolated_config.get("resultVariable") or interpolated_config.get(
                "responseVariable"
            )
            if result_var and result.data is not None:
                if not result.variables_updated:
                    result.variables_updated = {}
                result.variables_updated[result_var] = result.data

            # Handle direct output flag
            if interpolated_config.get("directOutput", False):
                result.direct_output = True

            # Mark target step reached for flow runner
            if is_target_step:
                log.info("Target step reached in test mode", step_id=step.id)
                if not result.metadata:
                    result.metadata = {}
                result.metadata["target_step_reached"] = True

            # Add to trace if tracing is active
            self._add_to_trace(step, result, context)

            return result

        except Exception as e:  # noqa: F841
            # Add failed step to trace if tracing is active
            if context.trace_log is not None:
                context.trace_log.append(
                    TraceEntry(
                        step_id=step.id,
                        step_type=step.type,
                        success=False,
                        execution_time=time.time() - step_start,
                        data=None,
                        variables_updated=None,
                    )
                )

            # Executors now wrap their own exceptions with context
            # Just re-raise to let the caller handle logging
            raise
        finally:
            context.resolved_credentials = {}

    async def _resolve_credentials(self, config: dict[str, Any]) -> dict[str, CredentialBundle]:
        """Resolve credential references defined in the step configuration."""
        if not self.credential_manager:
            return {}

        raw_credentials = config.get("credentials")
        if not isinstance(raw_credentials, dict):
            return {}

        resolved: dict[str, CredentialBundle] = {}
        for alias, reference in raw_credentials.items():
            if not isinstance(reference, dict):
                log.warning(
                    "Skipping credential reference with invalid structure",
                    alias=alias,
                    reference_type=type(reference).__name__,
                )
                continue

            credential_id = reference.get("id")
            if not credential_id:
                raise CredentialError("Credential reference missing id", details={"alias": alias})

            bundle = await self.credential_manager.get(str(credential_id))
            resolved[str(alias)] = bundle

        return resolved
