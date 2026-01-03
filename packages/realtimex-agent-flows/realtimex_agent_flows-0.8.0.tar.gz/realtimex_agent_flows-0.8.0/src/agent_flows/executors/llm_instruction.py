"""LlmInstructionExecutor for LLM-based text processing."""

import json
import time
from typing import Any

import litellm
from pydantic import ValidationError

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import ConfigurationError, ExecutorError
from agent_flows.executors.base import BaseExecutor
from agent_flows.integrations import LLMProviderManager
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import LlmInstructionExecutorConfig
from agent_flows.models.shared import ResponseFormat
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class LlmInstructionExecutor(BaseExecutor):
    """Executor for LLM instruction steps."""

    def __init__(self) -> None:
        """Initialize the LLM instruction executor."""
        self.interpolator = VariableInterpolator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["instruction"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return [
            "provider",
            "model",
            "temperature",
            "maxTokens",
            "systemPrompt",
            "responseFormat",
            "jsonSchema",
            "widget",
            "apiBase",
            "resultVariable",
            "directOutput",
            "timeout",
            "maxRetries",
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate LLM instruction configuration.

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
            LlmInstructionExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"LLM instruction executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute LLM instruction.

        Args:
            config: Step configuration containing LLM instruction parameters
            context: Execution context

        Returns:
            ExecutorResult with LLM response data

        Raises:
            ExecutorError: If LLM instruction execution fails
        """
        start_time = time.time()

        try:
            # Parse and validate configuration
            validated_config = LlmInstructionExecutorConfig(**config)

            log.info(
                "Starting LLM instruction execution",
                provider=validated_config.provider,
                model=validated_config.model,
                temperature=validated_config.temperature,
                response_format=validated_config.responseFormat.value,
            )

            # Perform variable interpolation on instruction and system prompt
            interpolated_instruction = self.interpolator.interpolate(
                validated_config.instruction, context.variables
            )

            interpolated_system_prompt = None
            if validated_config.systemPrompt:
                interpolated_system_prompt = self.interpolator.interpolate(
                    validated_config.systemPrompt, context.variables
                )

            # Emit LLM instruction streaming update
            streaming_handler = getattr(context.step_execution_service, "streaming_handler", None)
            if streaming_handler:
                truncated_instruction = (
                    interpolated_instruction[:100] + "..."
                    if len(interpolated_instruction) > 100
                    else interpolated_instruction
                )
                content = f"Processing instruction with {validated_config.provider}/{validated_config.model}: {truncated_instruction}"
                streaming_handler.stream_step("LLM Instruction", "Brain", content, content)

            # Configure LiteLLM credentials based on provider
            if validated_config.provider:
                providers_config = {
                    name: config.credentials
                    for name, config in context.config.llm_providers.providers.items()
                }
                LLMProviderManager.configure(validated_config.provider, providers=providers_config)

            # Execute the LLM request (LiteLLM handles retries internally)
            response_result = await self._make_llm_request(
                validated_config,
                interpolated_instruction,
                interpolated_system_prompt,
                context,
            )

            # Extract clean response content and metadata
            clean_response_content = response_result["content"]
            usage_info = response_result.get("usage", {})
            model_info = response_result.get("model")
            raw_content = response_result.get("raw_content")

            # Determine variables to update
            variables_updated: dict[str, Any] = {}
            if validated_config.resultVariable:
                variables_updated[validated_config.resultVariable] = clean_response_content

            execution_time = time.time() - start_time

            log.info(
                "LLM instruction completed successfully",
                execution_time=execution_time,
                tokens_used=usage_info.get("total_tokens"),
            )

            return ExecutorResult(
                success=True,
                data=clean_response_content,
                variables_updated=variables_updated,
                direct_output=validated_config.directOutput,
                execution_time=execution_time,
                metadata={
                    "provider": validated_config.provider,
                    "model": model_info or validated_config.model,
                    "temperature": validated_config.temperature,
                    "response_format": validated_config.responseFormat.value,
                    "usage": usage_info,
                    "tokens_used": usage_info.get("total_tokens"),
                    "raw_content": raw_content,  # For JSON responses, keep the raw JSON string
                    "step_type": "llmInstruction",
                },
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise
        except Exception as e:
            raise ExecutorError(f"LLM instruction execution failed: {str(e)}") from e

    async def _make_llm_request(
        self,
        config: LlmInstructionExecutorConfig,
        instruction: str,
        system_prompt: str | None,
        context: ExecutionContext,
    ) -> Any:
        """Execute the actual LLM request.

        Args:
            config: Validated configuration
            instruction: Interpolated instruction text
            system_prompt: Interpolated system prompt (if any)
            context: Execution context

        Returns:
            Processed LLM response

        Raises:
            Various LiteLLM exceptions for different error scenarios
        """
        # Build messages for the LLM request
        messages = self._build_messages(instruction, system_prompt)

        # Prepare completion arguments, trimming unset optional values
        completion_kwargs = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "timeout": config.timeout,
            "max_retries": config.maxRetries or 0,
            "max_tokens": config.maxTokens or None,
        }

        # Add response format for structured outputs if requested
        if config.responseFormat == ResponseFormat.JSON:
            completion_kwargs["response_format"] = {"type": "json_object"}
        elif config.responseFormat in {ResponseFormat.JSON_SCHEMA, ResponseFormat.WIDGET}:
            if config.jsonSchema is None:
                raise ExecutorError(
                    "jsonSchema must be provided when responseFormat is 'json_schema' or 'widget'"
                )
            completion_kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": config.jsonSchema,
            }
            # LiteLLM exposes supports_response_schema for capability checks; modern models handle
            # json_schema reliably, so we skip the probe to keep the hot path lean.

        # Add custom API base URL if configured (legacy support)
        if config.apiBase and not config.provider:
            completion_kwargs["api_base"] = config.apiBase

        completion_kwargs = {k: v for k, v in completion_kwargs.items() if v is not None}

        log.debug(
            "Making LLM request",
            provider=config.provider,
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.maxTokens,
            response_format=config.responseFormat.value,
            message_count=len(messages),
        )

        try:
            response = await litellm.acompletion(**completion_kwargs)

            log.debug(
                "Received LLM response",
                model=response.model if hasattr(response, "model") else config.model,
                usage=response.usage.dict()
                if hasattr(response, "usage") and response.usage
                else None,
            )

            # Process the response
            return self._process_response(response, config.responseFormat)

        except litellm.Timeout as e:
            timeout_suffix = f" after {config.timeout} seconds" if config.timeout else ""
            raise ExecutorError(f"LLM provider timed out{timeout_suffix}") from e
        except litellm.RateLimitError as e:
            raise ExecutorError(f"LLM rate limit exceeded: {str(e)}") from e
        except litellm.ServiceUnavailableError as e:
            raise ExecutorError(f"LLM service unavailable: {str(e)}") from e
        except litellm.AuthenticationError as e:
            raise ExecutorError(f"LLM authentication failed: {str(e)}") from e
        except litellm.InvalidRequestError as e:
            raise ExecutorError(f"Invalid LLM request: {str(e)}") from e
        except Exception as e:
            raise ExecutorError(f"LLM request failed: {str(e)}") from e

    def _build_messages(self, instruction: str, system_prompt: str | None) -> list[dict[str, str]]:
        """Build message list for LLM request.

        Args:
            instruction: The main instruction/prompt
            system_prompt: Optional system prompt

        Returns:
            List of message dictionaries for LLM API
        """
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add the main instruction as user message
        messages.append({"role": "user", "content": instruction})

        return messages

    def _process_response(self, response: Any, response_format: ResponseFormat) -> Any:
        """Process LLM response based on expected format.

        Args:
            response: Raw LLM response from LiteLLM or mock
            response_format: Expected response format

        Returns:
            Processed response data

        Raises:
            ValueError: If response processing fails (will be caught by caller)
        """
        try:
            is_mock_response = isinstance(response, dict)

            if is_mock_response:
                content = response.get("content")
                usage = response.get("usage", {})
                model = response.get("model")
            else:
                if hasattr(response, "choices") and response.choices:
                    content = response.choices[0].message.content
                else:
                    raise ValueError("Invalid LLM response format: no choices found")
                usage = (
                    response.usage.dict() if hasattr(response, "usage") and response.usage else {}
                )
                model = response.model if hasattr(response, "model") else None

            if not content:
                raise ValueError("Empty response from LLM")

            if response_format in {
                ResponseFormat.JSON,
                ResponseFormat.JSON_SCHEMA,
                ResponseFormat.WIDGET,
            }:
                try:
                    parsed_content = json.loads(content) if isinstance(content, str) else content
                    return {
                        "content": parsed_content,
                        "raw_content": content,
                        "usage": usage,
                        "model": model,
                    }
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse JSON response: {str(e)}") from e
            else:  # TEXT format
                return {
                    "content": content,
                    "usage": usage,
                    "model": model,
                }

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to process LLM response: {str(e)}") from e

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "llmInstruction"
