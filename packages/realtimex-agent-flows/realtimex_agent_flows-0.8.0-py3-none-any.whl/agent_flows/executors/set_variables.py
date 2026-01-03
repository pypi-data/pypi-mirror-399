"""SetVariablesExecutor for defining and updating variables."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.core.resources import VariableInterpolator
from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors.set_variables import SetVariablesExecutorConfig
from agent_flows.utils.dict_utils import set_nested_value
from agent_flows.utils.logging import get_logger
from agent_flows.utils.type_casting import cast_value

log = get_logger(__name__)


class SetVariablesExecutor(BaseExecutor):
    """Executor for setting and updating flow variables."""

    def __init__(self):
        """Initialize the executor."""
        self.interpolator = VariableInterpolator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["variables"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return []

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate configuration.

        Args:
            config: Step configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid (Pydantic validation)
            ConfigurationError: If configuration is invalid (other errors)
        """
        try:
            SetVariablesExecutorConfig(**config)
            return True
        except ValidationError:
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Set variables executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute variable assignment.

        Args:
            config: Step configuration
            context: Execution context

        Returns:
            ExecutorResult with updated variables

        Raises:
            ExecutorError: If execution fails
        """
        start_time = time.time()

        try:
            # Parse configuration
            validated_config = SetVariablesExecutorConfig(**config)

            # Initialize variables dictionary with current context variables
            # We work on a copy to track changes
            updated_variables: dict[str, Any] = dict(context.variables)
            variables_delta: dict[str, Any] = {}

            for assignment in validated_config.variables:
                # 1. Interpolate value if it's a string
                raw_value = assignment.value
                interpolated_value = self.interpolator.interpolate_object(
                    raw_value, updated_variables
                )

                # 2. Cast value to target type
                try:
                    final_value = cast_value(interpolated_value, assignment.type, strict=False)
                except ValueError as e:
                    raise ExecutorError(
                        f"Failed to set variable '{assignment.name}': {str(e)}"
                    ) from e

                # 3. Set value (handling nested paths)
                try:
                    set_nested_value(updated_variables, assignment.name, final_value)

                    # For variables_updated, we want to return the ROOT key that was modified
                    # so that the state tracker can correctly merge it (overwrite the top-level object).
                    # If we return "user.profile.name", state tracker adds it as a literal key.
                    # Instead, we return "user": <complete user object>.
                    root_key = assignment.name.split(".")[0]
                    variables_delta[root_key] = updated_variables[root_key]
                except ValueError as e:
                    raise ExecutorError(
                        f"Failed to set nested variable '{assignment.name}': {str(e)}"
                    ) from e

                log.debug(
                    "Variable set",
                    variable=assignment.name,
                    type=assignment.type,
                    value_preview=str(final_value)[:50],
                )

            execution_time = time.time() - start_time

            return ExecutorResult(
                success=True,
                data=updated_variables,
                variables_updated=variables_delta,
                execution_time=execution_time,
                metadata={
                    "variables_set": len(variables_delta),
                    "step_type": "set_variables",
                },
            )

        except (ValidationError, ConfigurationError):
            raise
        except Exception as e:
            raise ExecutorError(f"Set variables executor failed: {str(e)}") from e

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "setVariables"
