"""FlowVariablesExecutor for variable initialization."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors.flow_variables import FlowVariablesExecutorConfig
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class FlowVariablesExecutor(BaseExecutor):
    """Executor for flow variable initialization steps."""

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return []  # variables is optional, can be empty list

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return ["variables"]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate flow variables step configuration.

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
            FlowVariablesExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Flow variables executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Initialize flow variables.

        Args:
            config: Step configuration containing variables to initialize
            context: Execution context

        Returns:
            ExecutorResult with initialized variables

        Raises:
            ExecutorError: If variable initialization fails
        """
        start_time = time.time()

        try:
            # Parse and validate configuration
            validated_config = FlowVariablesExecutorConfig(**config)

            # Variable initialization starts - orchestrator already logs "Executing step"

            # Initialize variables dictionary with current context variables
            # This ensures we preserve runtime-overridden variables
            initialized_variables: dict[str, Any] = dict(context.variables)

            # Track only the variables that this step actually initializes (delta)
            variables_delta: dict[str, Any] = {}

            # Process each variable definition from the flow config
            # Skip system variables (loaded fresh from API by VariableManager)
            # Only set user_input variables that are not already in context
            for var_def in validated_config.variables:
                # Skip system variables - they are managed by VariableManager from API
                if var_def.source == "system":
                    log.debug(
                        "Skipping system variable (managed by VariableManager)",
                        variable_name=var_def.name,
                    )
                    continue

                # Only initialize if the variable is not already set in context
                # This preserves runtime variable overrides
                if var_def.name not in initialized_variables:
                    initialized_variables[var_def.name] = var_def.value
                    variables_delta[var_def.name] = var_def.value

                    log.debug(
                        "Variable initialized",
                        variable_name=var_def.name,
                        source=var_def.source,
                    )

            execution_time = time.time() - start_time

            # Variable initialization completed - orchestrator will log "Step completed"

            return ExecutorResult(
                success=True,
                data=initialized_variables,
                variables_updated=variables_delta,  # Only return the delta (newly initialized variables)
                direct_output=False,  # Flow variables executor never has direct output
                execution_time=execution_time,
                metadata={
                    "variables_initialized": len(variables_delta),
                    "variables_total": len(initialized_variables),
                    "newly_initialized": list(variables_delta.keys()),
                    "all_variables": list(initialized_variables.keys()),
                    "step_id": context.step_id,
                    "step_type": "flow_variables",
                },
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise
        except Exception as e:
            # Wrap with executor-specific context for better error messages
            raise ExecutorError(f"Flow variables executor failed: {str(e)}") from e

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "flow_variables"
