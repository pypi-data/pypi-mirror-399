"""McpServerActionExecutor for MCP server action execution."""

import time
from typing import Any

from pydantic import ValidationError

from agent_flows.core.resources.interpolation import VariableInterpolator
from agent_flows.exceptions import (
    ConfigurationError,
    ExecutorError,
    MCPConnectionError,
    MCPError,
    MCPTimeoutError,
    MCPToolError,
)
from agent_flows.executors.base import BaseExecutor
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors import McpServerActionExecutorConfig
from agent_flows.models.shared import MCPProvider
from agent_flows.utils.logging import get_logger
from agent_flows.utils.mcp_helpers import MCPConnectionHelper

log = get_logger(__name__)


class McpServerActionExecutor(BaseExecutor):
    """Executor for MCP server action steps."""

    def __init__(self) -> None:
        """Initialize the MCP server action executor."""
        self.interpolator = VariableInterpolator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["provider", "serverId", "action"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return [
            "params",
            "resultVariable",
            "directOutput",
            "timeout",
            "maxRetries",
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate MCP server action configuration.

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
            McpServerActionExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"MCP server action executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute MCP server action.

        Args:
            config: Step configuration containing MCP action parameters
            context: Execution context

        Returns:
            ExecutorResult with MCP action response data

        Raises:
            ExecutorError: If MCP action execution fails
        """
        start_time = time.time()

        try:
            # Parse and validate configuration
            validated_config = McpServerActionExecutorConfig(**config)

            log.info(
                "Starting MCP server action execution",
                provider=validated_config.provider.value,
                server_id=validated_config.serverId,
                action=validated_config.action,
            )

            # Perform variable interpolation on parameters
            interpolated_params = self._interpolate_params(
                validated_config.params, context.variables
            )

            # Emit streaming update for MCP action
            if context.step_execution_service and context.step_execution_service.streaming_handler:
                content = (
                    f"Executing MCP action {validated_config.action} on {validated_config.serverId}"
                )
                context.step_execution_service.streaming_handler.stream_step(
                    "MCP Server", "Server", content, content
                )

            # Execute the MCP action with retry logic
            response_result = await self._execute_with_retries(
                validated_config, interpolated_params, context
            )

            # Extract clean response content and metadata
            clean_response_content = response_result["content"]
            mcp_metadata = response_result.get("metadata", {})

            # Determine variables to update - use clean response content
            variables_updated: dict[str, Any] = {}
            if validated_config.resultVariable:
                variables_updated[validated_config.resultVariable] = clean_response_content

            execution_time = time.time() - start_time

            log.info(
                "MCP server action completed",
                execution_time=round(execution_time, 2),
                server_id=validated_config.serverId,
                action=validated_config.action,
            )

            return ExecutorResult(
                success=True,
                data=clean_response_content,  # Pure MCP response content only
                variables_updated=variables_updated,
                direct_output=validated_config.directOutput,
                execution_time=execution_time,
                metadata={
                    "provider": validated_config.provider.value,
                    "server_id": validated_config.serverId,
                    "action": validated_config.action,
                    "step_id": context.step_id,
                    "mcp_metadata": mcp_metadata,
                    "step_type": "mcpServerAction",
                },
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise

        except Exception as e:
            raise ExecutorError(f"MCP server action execution failed: {str(e)}") from e

    def _interpolate_params(
        self, params: dict[str, Any], variables: dict[str, Any]
    ) -> dict[str, Any]:
        """Perform variable interpolation on MCP action parameters.

        Args:
            params: MCP action parameters
            variables: Variables for interpolation

        Returns:
            Parameters dictionary with interpolated values
        """
        return self.interpolator.interpolate_object(params, variables)

    async def _execute_with_retries(
        self,
        config: McpServerActionExecutorConfig,
        params: dict[str, Any],
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """Execute MCP action with retry logic.

        Args:
            config: Validated configuration
            params: Interpolated parameters
            context: Execution context

        Returns:
            MCP action response data

        Raises:
            ExecutorError: If all retry attempts fail
        """
        if config.maxRetries == 0:
            # No retries, execute directly
            return await self._make_mcp_request(config, params, context)

        last_error = None
        for attempt in range(config.maxRetries + 1):
            try:
                if attempt > 0:
                    log.info(
                        "Retrying MCP action",
                        attempt=attempt + 1,
                        max_attempts=config.maxRetries + 1,
                        server_id=config.serverId,
                        action=config.action,
                    )

                return await self._make_mcp_request(config, params, context)

            except Exception as e:
                last_error = e
                log.warning(
                    f"MCP action attempt {attempt + 1} failed: {str(e)}",
                    server_id=config.serverId,
                    action=config.action,
                )

                if attempt == config.maxRetries:
                    break

        raise ExecutorError(
            f"MCP action failed after {config.maxRetries + 1} attempts: {str(last_error)}"
        ) from last_error

    async def _make_mcp_request(
        self,
        config: McpServerActionExecutorConfig,
        params: dict[str, Any],
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """Execute the actual MCP server action request.

        Args:
            config: Validated configuration
            params: Interpolated parameters
            context: Execution context

        Returns:
            Processed MCP response

        Raises:
            ExecutorError: If MCP request fails
        """
        log.debug(
            "Making MCP server action request",
            provider=config.provider.value,
            server_id=config.serverId,
            action=config.action,
            params_count=len(params),
        )

        try:
            # Get connection parameters based on provider
            connection_params = await self._get_connection_params(config, context)

            # Get persistent MCP client from session pool
            if not context.mcp_session_pool:
                raise ExecutorError("MCP session pool not available in execution context")

            mcp_client = await context.mcp_session_pool.get_session(
                provider=config.provider,
                server_id=config.serverId,
                connection_params=connection_params,
                timeout=config.timeout,
            )

            # Execute the tool/action (no connect/disconnect needed)
            result = await mcp_client.call_tool(
                tool_name=config.action,
                arguments=params,
                timeout=config.timeout,
            )

            log.debug(
                "Received MCP server action response",
                server_id=config.serverId,
                action=config.action,
                response_size=len(str(result["content"])) if result.get("content") else 0,
            )

            return result

        except (MCPConnectionError, MCPTimeoutError, MCPToolError, MCPError) as e:
            # Convert MCP-specific errors to ExecutorError with proper context
            raise ExecutorError(f"MCP server action request failed: {str(e)}") from e
        except Exception as e:
            # Handle any other unexpected errors
            raise ExecutorError(
                f"Unexpected error during MCP server action request: {str(e)}"
            ) from e

    async def _get_connection_params(
        self,
        config: McpServerActionExecutorConfig,
        context: ExecutionContext,
    ) -> dict[str, Any]:
        """Get connection parameters for MCP server.

        Args:
            config: Validated configuration
            context: Execution context

        Returns:
            Connection parameters dictionary

        Raises:
            ExecutorError: If connection parameters cannot be determined
        """
        # Get API key from context config
        api_key = context.config.api_key if context.config else None
        if not api_key:
            raise ExecutorError("API key is required for MCP connections")

        # Get MCP configuration for remote connections
        aci_api_key = None
        aci_owner_id = None
        if context.config and hasattr(context.config, "mcp"):
            aci_api_key = context.config.mcp.aci_api_key
            aci_owner_id = context.config.mcp.aci_linked_account_owner_id

        # Validate remote provider requirements early
        if config.provider == MCPProvider.REMOTE and (not aci_api_key or not aci_owner_id):
            missing_fields = []
            if not aci_api_key:
                missing_fields.append("aci_api_key")
            if not aci_owner_id:
                missing_fields.append("aci_linked_account_owner_id")

            raise ExecutorError(
                f"Remote MCP connections require ACI configuration. Missing fields: {', '.join(missing_fields)}. "
                "Please configure these in the context MCP settings."
            )

        return await MCPConnectionHelper.get_connection_params(
            provider=config.provider,
            server_id=config.serverId,
            api_key=api_key,
            aci_api_key=aci_api_key,
            aci_owner_id=aci_owner_id,
            timeout=config.timeout,
        )

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "mcpServerAction"
