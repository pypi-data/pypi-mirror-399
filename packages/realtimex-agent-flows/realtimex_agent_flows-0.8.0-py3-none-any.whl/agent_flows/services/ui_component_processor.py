"""Shared service for processing UI components in static and LLM modes."""

import json
from typing import Any

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import ExecutorError
from agent_flows.integrations import LLMProviderManager
from agent_flows.models.execution import ExecutionContext
from agent_flows.models.executors.stream_ui import StreamUIExecutorConfig, UIComponentDataType
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class UIComponentProcessor:
    """Service for processing UI components with static or LLM-based generation."""

    def __init__(self) -> None:
        """Initialize the UI component processor."""
        self.interpolator = VariableInterpolator()

    async def process(
        self,
        config: StreamUIExecutorConfig,
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """Process UI component data based on configuration mode.

        Args:
            config: Validated UI component configuration
            context: Execution context with variables

        Returns:
            Processed UI component data with dataType and data keys
        """
        if config.useLLM:
            return await self._process_llm_mode(config, context)
        else:
            return self._process_static_mode(config, context)

    def _process_static_mode(
        self, config: StreamUIExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Process UI component in static mode with variable interpolation.

        Args:
            config: Validated configuration
            context: Execution context

        Returns:
            Processed UI component data
        """
        if self._is_widget_data_type(config.uiComponents.dataType):
            interpolated_data = self._process_widget_static_payload(config, context)
        else:
            interpolated_data = self.interpolator.interpolate_object(
                config.uiComponents.data, context.variables
            )

        return {
            "dataType": config.uiComponents.dataType.value,
            "data": interpolated_data,
        }

    async def _process_llm_mode(
        self, config: StreamUIExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Process UI component in LLM mode with dynamic generation.

        Args:
            config: Validated configuration
            context: Execution context

        Returns:
            Processed UI component data with LLM-generated content
        """
        # Interpolate variables in the input prompt
        interpolated_input = self.interpolator.interpolate(
            config.inputData,
            context.variables,  # type: ignore
        )

        log.debug(
            "Generating UI component with LLM",
            data_type=config.uiComponents.dataType.value,
            input_length=len(interpolated_input),
        )

        # Configure LLM provider
        providers_config = {
            name: provider_config.credentials
            for name, provider_config in context.config.llm_providers.providers.items()
        }
        LLMProviderManager.configure("realtimexai", providers=providers_config)

        # Generate UI component data with LLM
        generated_data = await self._make_llm_request(config, interpolated_input)

        return {
            "dataType": config.uiComponents.dataType.value,
            "data": self._format_llm_output(config, generated_data),
        }

    async def _make_llm_request(
        self,
        config: StreamUIExecutorConfig,
        input_prompt: str,
    ) -> Any:
        """Execute LLM request to generate UI component data.

        Args:
            config: Validated configuration
            input_prompt: Interpolated input prompt

        Returns:
            Generated UI component data matching the schema
        """
        import litellm  # delayed import to avoid startup overhead

        # Build system prompt for UI generation
        system_prompt = (
            f"You are a UI data generator. Generate data for a {config.uiComponents.dataType.value} "
            "component that matches the provided JSON schema. Return only valid JSON that conforms "
            "to the schema structure. Do not include any explanations or additional text."
        )

        # Construct user message with input data
        user_message = (
            f"Here is the input data to use for generating the UI component:\n\n{input_prompt}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]

        # Build JSON schema structure for LiteLLM using the normalized schema
        schema = config.get_llm_schema()
        json_schema_def = {
            "schema": schema,
            "name": f"{config.uiComponents.dataType.value}_component",
            "strict": False,
        }

        # Prepare LLM request with json_schema response format
        completion_kwargs = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
            "response_format": {
                "type": "json_schema",
                "json_schema": json_schema_def,
            },
        }

        log.debug(
            "Making LLM request for UI generation",
            model=completion_kwargs["model"],
            data_type=config.uiComponents.dataType.value,
        )

        try:
            response = await litellm.acompletion(**completion_kwargs)

            if not hasattr(response, "choices") or not response.choices:
                raise ExecutorError("Invalid LLM response: no choices found")

            content = response.choices[0].message.content

            if not content:
                raise ExecutorError("Empty response from LLM")

            # Parse and validate JSON response
            try:
                parsed_content = json.loads(content) if isinstance(content, str) else content
            except json.JSONDecodeError as e:
                raise ExecutorError(f"Failed to parse LLM JSON response: {str(e)}") from e

            log.debug(
                "LLM UI generation successful",
                data_type=config.uiComponents.dataType.value,
            )

            return parsed_content

        except litellm.Timeout as e:
            raise ExecutorError("LLM provider timed out during UI generation") from e
        except litellm.RateLimitError as e:
            raise ExecutorError(f"LLM rate limit exceeded: {str(e)}") from e
        except litellm.ServiceUnavailableError as e:
            raise ExecutorError(f"LLM service unavailable: {str(e)}") from e
        except litellm.AuthenticationError as e:
            raise ExecutorError(f"LLM authentication failed: {str(e)}") from e
        except litellm.InvalidRequestError as e:
            raise ExecutorError(f"Invalid LLM request: {str(e)}") from e
        except ExecutorError:
            raise
        except Exception as e:
            raise ExecutorError(f"LLM request failed: {str(e)}") from e

    def _format_llm_output(self, config: StreamUIExecutorConfig, generated_data: Any) -> Any:
        """Normalize LLM output across component types."""
        if self._is_widget_data_type(config.uiComponents.dataType):
            return self._build_widget_payload(config, generated_data)
        return generated_data

    def _build_widget_payload(
        self, config: StreamUIExecutorConfig, generated_data: Any
    ) -> dict[str, Any]:
        """Attach generated data to the widget payload while preserving configuration."""
        from copy import deepcopy

        content_template = config.get_widget_content_template()
        if content_template is None:
            raise ExecutorError(
                "Widget components must define uiComponents.data.content with widget metadata"
            )

        content_payload = deepcopy(content_template)
        content_payload["data"] = generated_data
        return {"content": content_payload}

    def _is_widget_data_type(self, data_type: UIComponentDataType) -> bool:
        """Check if the supplied UI data type represents a widget."""
        return data_type == UIComponentDataType.WIDGET

    def _process_widget_static_payload(
        self, config: StreamUIExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Interpolate widget payload safely, preserving template metadata."""
        from copy import deepcopy

        content_template = config.get_widget_content_template()
        if content_template is None:
            raise ExecutorError(
                "Widget components must define uiComponents.data.content with widget metadata"
            )

        content_payload = deepcopy(content_template)
        data_section = content_payload.get("data")
        if data_section is None:
            raise ExecutorError("Widget components must provide data schema or payload")

        content_payload["data"] = self.interpolator.interpolate_object(
            data_section, context.variables
        )
        return {"content": content_payload}
