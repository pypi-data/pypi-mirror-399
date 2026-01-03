"""StreamUIExecutor for rendering UI components during execution."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import StreamUIExecutorConfig
from agent_flows.services import UIComponentProcessor
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class StreamUIExecutor(BaseExecutor):
    """Executor for streaming UI components to the chat interface."""

    def __init__(self) -> None:
        """Initialize the stream UI executor."""
        self.ui_processor = UIComponentProcessor()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["useLLM", "uiComponents"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return ["inputData"]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate stream UI configuration.

        Args:
            config: Step configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ValidationError: If configuration is invalid (Pydantic validation)
            ConfigurationError: If configuration is invalid (wrapped ValidationError)
        """
        try:
            StreamUIExecutorConfig(**config)
            return True

        except ValidationError as e:
            raise ConfigurationError(
                f"Stream UI executor configuration validation failed: {str(e)}"
            ) from e
        except Exception as e:
            raise ConfigurationError(
                f"Stream UI executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute stream UI component rendering.

        Args:
            config: Step configuration containing UI component parameters
            context: Execution context

        Returns:
            ExecutorResult with UI component data

        Raises:
            ExecutorError: If UI component streaming fails
        """
        start_time = time.time()

        try:
            validated_config = StreamUIExecutorConfig(**config)

            log.info(
                "Starting stream UI execution",
                use_llm=validated_config.useLLM,
                data_type=validated_config.uiComponents.dataType.value,
            )

            # Process UI component using shared service
            ui_component_data = await self.ui_processor.process(validated_config, context)
            llm_generated = validated_config.useLLM

            # Stream the UI component
            self._stream_ui_component(validated_config, ui_component_data, context)

            execution_time = time.time() - start_time

            log.info(
                "Stream UI completed successfully",
                execution_time=execution_time,
                data_type=validated_config.uiComponents.dataType.value,
                llm_generated=llm_generated,
            )

            return ExecutorResult(
                success=True,
                data=ui_component_data,
                variables_updated={},
                execution_time=execution_time,
                metadata={
                    "step_type": "streamUI",
                    "data_type": validated_config.uiComponents.dataType.value,
                    "llm_generated": llm_generated,
                    "streamed": True,
                },
            )

        except ValidationError as e:
            raise ConfigurationError(
                f"Stream UI executor configuration validation failed: {str(e)}"
            ) from e
        except ConfigurationError:
            raise
        except Exception as e:
            raise ExecutorError(f"Stream UI execution failed: {str(e)}") from e

    def _stream_ui_component(
        self,
        config: StreamUIExecutorConfig,
        ui_component_data: dict[str, Any],
        context: ExecutionContext,
    ) -> None:
        """Stream UI component via streaming handler.

        Args:
            config: Validated configuration
            ui_component_data: Processed UI component data
            context: Execution context
        """
        streaming_handler = getattr(context.step_execution_service, "streaming_handler", None)
        if not streaming_handler:
            log.debug("No streaming handler available, skipping UI component stream")
            return

        # Extract payload from the data structure
        payload = ui_component_data.get("data", {})

        streaming_handler.emit_ui_component(config.uiComponents.dataType.value, payload)

        log.debug(
            "UI component streamed",
            data_type=config.uiComponents.dataType.value,
        )
