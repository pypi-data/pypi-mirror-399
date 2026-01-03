"""FinishExecutor for graceful flow termination."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import FinishExecutorConfig, StreamUIExecutorConfig
from agent_flows.services import UIComponentProcessor
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class FinishExecutor(BaseExecutor):
    """Executor for graceful flow termination."""

    def __init__(self) -> None:
        """Initialize the finish executor."""
        self.ui_processor = UIComponentProcessor()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return []  # All fields are optional

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return [
            "message",
            "data",
            "resultVariable",
            "flowAsOutput",
            "useLLM",
            "inputData",
            "uiComponents",
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate finish step configuration.

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
            FinishExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Finish executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute finish step to gracefully terminate flow.

        Args:
            config: Step configuration containing optional message and data
            context: Execution context

        Returns:
            ExecutorResult with special finish signal

        Raises:
            ExecutorError: If finish execution fails
        """
        start_time = time.time()

        try:
            # Parse and validate configuration
            validated_config = FinishExecutorConfig(**config)

            # Prepare finish data
            finish_data = {
                "message": validated_config.message,
                "terminated_at_step": context.step_index,
                "flow_id": context.flow_id,
            }

            # Include custom data if provided
            if validated_config.data is not None:
                finish_data["custom_data"] = validated_config.data

            # Determine variables to update
            variables_updated: dict[str, Any] = {}
            if validated_config.resultVariable:
                variables_updated[validated_config.resultVariable] = finish_data

            # Process UI components if configured
            ui_component_data = None
            if validated_config.uiComponents is not None:
                # Create a StreamUIExecutorConfig to reuse the shared processor
                stream_ui_config = StreamUIExecutorConfig(
                    useLLM=validated_config.useLLM or False,
                    inputData=validated_config.inputData,
                    uiComponents=validated_config.uiComponents,
                )
                ui_component_data = await self.ui_processor.process(stream_ui_config, context)

                log.debug(
                    "Finish executor processed UI components",
                    use_llm=validated_config.useLLM,
                    data_type=validated_config.uiComponents.dataType.value,
                )

                streaming_handler = getattr(
                    context.step_execution_service, "streaming_handler", None
                )
                if streaming_handler:
                    streaming_handler.emit_ui_component(
                        validated_config.uiComponents.dataType.value,
                        ui_component_data.get("data", {}),
                    )
                else:
                    log.debug("No streaming handler available, skipping finish UI stream")

            execution_time = time.time() - start_time

            # Build metadata with flow_as_output flag
            metadata: dict[str, Any] = {
                "step_type": "finish",
                "flow_termination_signal": True,  # Special signal for FlowExecutor
                "termination_reason": "finish_step_executed",
                "message": validated_config.message,
                "flow_as_output": validated_config.flowAsOutput,
            }

            # Return special result that signals flow should finish
            return ExecutorResult(
                success=True,
                data=finish_data,
                variables_updated=variables_updated,
                direct_output=False,
                execution_time=execution_time,
                metadata=metadata,
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise

        except Exception as e:
            raise ExecutorError(f"Finish executor execution failed: {str(e)}") from e

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "finish"
