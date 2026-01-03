"""WebSearchExecutor for web search operations."""

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
from agent_flows.integrations import MCPClient
from agent_flows.models.execution import ExecutionContext, ExecutorResult
from agent_flows.models.executors.web_search import (
    WebSearchExecutorConfig,
    WebSearchProviderConfig,
)
from agent_flows.models.shared import SearchProvider
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class WebSearchExecutor(BaseExecutor):
    """Executor for web search operations."""

    def __init__(self) -> None:
        """Initialize the web search executor."""
        self.interpolator = VariableInterpolator()

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields."""
        return ["query", "provider"]

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields."""
        return [
            "maxResults",
            "searchType",
            "timeout",
            "maxRetries",
            "resultVariable",
            "directOutput",
        ]

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate web search configuration.

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
            WebSearchExecutorConfig(**config)
            return True

        except ValidationError:
            # Let ValidationError bubble up for better error formatting
            raise
        except Exception as e:
            raise ConfigurationError(
                f"Web search executor configuration validation failed: {str(e)}"
            ) from e

    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute web search.

        Retries and fallback providers are handled internally by _execute_mcp_search,
        which leverages the MCP server's built-in fallback mechanism.

        Args:
            config: Step configuration containing search parameters
            context: Execution context

        Returns:
            ExecutorResult with search results array (metadata excluded)

        Raises:
            ExecutorError: If search execution fails
        """
        start_time = time.time()

        try:
            # Perform variable interpolation on configuration
            interpolated_config = self.interpolator.interpolate_object(config, context.variables)

            # Validate the final interpolated configuration
            validated_config = WebSearchExecutorConfig(**interpolated_config)

            log.info(
                "Starting web search execution",
                query=self._mask_sensitive_query(validated_config.query),
                search_type=validated_config.searchType.value,
                max_results=validated_config.maxResults,
                provider=self._get_primary_provider_name(validated_config.provider),
            )

            if context.step_execution_service and context.step_execution_service.streaming_handler:
                masked_query = self._mask_sensitive_query(validated_config.query)
                provider_name = self._get_primary_provider_name(validated_config.provider)
                content = f'Searching for "{masked_query}" via {provider_name}'
                context.step_execution_service.streaming_handler.stream_step(
                    "Web Search", "Search", content, content
                )

            # Execute search directly - retries/fallback handled by MCP server
            search_result = await self._execute_mcp_search(validated_config, context)

            # Determine variables to update
            variables_updated: dict[str, Any] = {}
            if validated_config.resultVariable:
                variables_updated[validated_config.resultVariable] = search_result

            execution_time = time.time() - start_time

            log.info(
                "Web search completed successfully",
                execution_time=execution_time,
                results_count=search_result.get("results_returned", 0),
                total_available=search_result.get("total_results", 0),
                provider_used=search_result.get("provider", "unknown"),
            )

            return ExecutorResult(
                success=True,
                data=search_result,  # Complete search response with lean results
                variables_updated=variables_updated,
                direct_output=validated_config.directOutput,
                execution_time=execution_time,
                metadata={
                    "provider_used": search_result.get("provider", "unknown"),
                    "query": self._mask_sensitive_query(validated_config.query),
                    "search_type": validated_config.searchType.value,
                    "results_count": search_result.get("results_returned", 0),
                    "total_available": search_result.get("total_results", 0),
                    "search_time": search_result.get("search_time", 0),
                    "step_id": context.step_id,
                    "step_type": "webSearch",
                },
            )

        except ConfigurationError:
            # Re-raise configuration errors as-is
            raise

        except Exception as e:
            raise ExecutorError(f"Web search execution failed: {str(e)}") from e

    async def _execute_mcp_search(
        self, config: WebSearchExecutorConfig, context: ExecutionContext
    ) -> dict[str, Any]:
        """Execute web search using the MCP server.

        Args:
            config: Validated search configuration
            context: Execution context

        Returns:
            Search results dictionary

        Raises:
            ExecutorError: If MCP search fails
        """
        mcp_client = None
        try:
            # Create MCP client
            mcp_client = MCPClient()

            # Connect to the web-search-mcp-server using uvx
            await mcp_client.connect_to_server(
                command="web-search-mcp-server",  # Temporary change to package name
                args=[
                    # "run",
                    # "web-search-mcp-server"
                ],
                env=self._build_mcp_environment(config.provider),
                timeout=config.timeout,
            )

            # Determine which MCP tool to use based on fallback configuration
            if config.provider.fallbacks:
                # Use search_with_fallback tool for configurations with fallbacks
                tool_name = "search_with_fallback"
                arguments = self._build_fallback_arguments(config)
            else:
                # Use basic web_search tool for single provider
                tool_name = "web_search"
                arguments = self._build_search_arguments(config)

            log.debug(
                "Calling MCP tool",
                tool_name=tool_name,
                query=self._mask_sensitive_query(config.query),
                provider=config.provider.name.value,
            )

            # Execute the MCP tool
            result = await mcp_client.call_tool(
                tool_name=tool_name,
                arguments=arguments,
                timeout=config.timeout,
            )

            # Process and return the MCP response
            return self._process_mcp_response(result, config)

        except (MCPConnectionError, MCPTimeoutError, MCPToolError, MCPError) as e:
            raise ExecutorError(f"MCP web search failed: {str(e)}") from e
        except Exception as e:
            raise ExecutorError(f"Unexpected error during MCP web search: {str(e)}") from e
        finally:
            # Always clean up the MCP client
            if mcp_client:
                await mcp_client.disconnect()

    def _build_mcp_environment(self, provider_config: WebSearchProviderConfig) -> dict[str, str]:
        """Build environment variables for the MCP server based on provider configuration.

        Args:
            provider_config: Provider configuration

        Returns:
            Environment variables dictionary
        """
        env = {}

        # Add environment variables for the primary provider
        self._add_provider_env_vars(env, provider_config.name.value, provider_config.config)

        # Add environment variables for fallback providers
        for fallback in provider_config.fallbacks:
            self._add_provider_env_vars(env, fallback.name, fallback.config)

        return env

    def _add_provider_env_vars(
        self, env: dict[str, str], provider_name: str, provider_config: dict[str, Any]
    ) -> None:
        """Add provider-specific environment variables.

        Args:
            env: Environment variables dictionary to update
            provider_name: Provider name
            provider_config: Provider configuration
        """
        if provider_name == SearchProvider.GOOGLE.value:
            if "apiKey" in provider_config:
                env["GOOGLE_SEARCH_API_KEY"] = provider_config["apiKey"]
            if "searchEngineId" in provider_config:
                env["GOOGLE_CSE_ID"] = provider_config["searchEngineId"]
        elif provider_name == SearchProvider.BING.value:
            if "apiKey" in provider_config:
                env["BING_SEARCH_API_KEY"] = provider_config["apiKey"]
        elif provider_name == SearchProvider.SERPAPI.value:
            if "apiKey" in provider_config:
                env["SERPAPI_API_KEY"] = provider_config["apiKey"]
        elif provider_name == SearchProvider.SERPLY.value:
            if "apiKey" in provider_config:
                env["SERPLY_API_KEY"] = provider_config["apiKey"]
        elif provider_name == SearchProvider.SEARXNG.value:
            if "baseUrl" in provider_config:
                env["SEARXNG_BASE_URL"] = provider_config["baseUrl"]
        elif provider_name == SearchProvider.TAVILY.value:
            if "apiKey" in provider_config:
                env["TAVILY_API_KEY"] = provider_config["apiKey"]
        # DuckDuckGo requires no environment variables

    def _build_search_arguments(self, config: WebSearchExecutorConfig) -> dict[str, Any]:
        """Build arguments for the basic web_search MCP tool.

        Args:
            config: Search configuration

        Returns:
            Arguments dictionary for MCP tool
        """
        return {
            "query": config.query,
            "provider": config.provider.name.value,
            "max_results": config.maxResults,
            "search_type": config.searchType.value,
            "timeout": config.timeout,
        }

    def _build_fallback_arguments(self, config: WebSearchExecutorConfig) -> dict[str, Any]:
        """Build arguments for the search_with_fallback MCP tool.

        Args:
            config: Search configuration

        Returns:
            Arguments dictionary for MCP tool
        """
        fallback_providers = [fallback.name for fallback in config.provider.fallbacks]

        return {
            "query": config.query,
            "primary_provider": config.provider.name.value,
            "fallback_providers": fallback_providers,
            "max_results": config.maxResults,
        }

    def _process_mcp_response(
        self, mcp_result: dict[str, Any], config: WebSearchExecutorConfig
    ) -> dict[str, Any]:
        """Process the MCP tool response into the expected format.

        Preserves the complete search response structure while making individual
        search results lean by removing their metadata fields.

        Args:
            mcp_result: Raw MCP tool result
            config: Search configuration

        Returns:
            Complete search response with lean individual results
        """
        # Extract the content from MCP result
        content = mcp_result.get("content", mcp_result)

        # If content is a string (error case), handle it
        if isinstance(content, str):
            # Try to parse as JSON if it looks like JSON
            import json

            try:
                content = json.loads(content)
            except (json.JSONDecodeError, TypeError) as e:
                # If not JSON, treat as error
                raise ExecutorError(f"MCP server returned error: {content}") from e

        # Ensure we have the expected structure
        if not isinstance(content, dict):
            raise ExecutorError(f"Unexpected MCP response format: {type(content)}")

        # Process results to exclude metadata from individual results
        results = content.get("results", [])
        lean_results = []

        for result in results:
            if isinstance(result, dict):
                # Strip metadata field from individual results for lean processing
                lean_result = {k: v for k, v in result.items() if k != "metadata"}
                lean_results.append(lean_result)
            else:
                # If result is not a dict, keep it as is
                lean_results.append(result)

        # Return complete response with lean results
        processed_response = dict(content)  # Copy all top-level fields
        processed_response["results"] = lean_results  # Replace with lean results

        # Ensure provider field is set
        if "provider" not in processed_response:
            processed_response["provider"] = config.provider.name.value

        return processed_response

    def _get_primary_provider_name(self, provider_config: WebSearchProviderConfig) -> str:
        """Get the primary provider name for logging.

        Args:
            provider_config: Provider configuration

        Returns:
            Primary provider name
        """
        return provider_config.name.value

    def _mask_sensitive_query(self, query: str) -> str:
        """Mask potentially sensitive information in search query for logging.

        Args:
            query: Original search query

        Returns:
            Query with sensitive parts masked
        """
        # Simple masking - could be enhanced based on specific needs
        sensitive_patterns = ["password", "secret", "token", "key", "api_key"]

        masked_query = query
        for pattern in sensitive_patterns:
            if pattern.lower() in query.lower():
                # If query contains sensitive terms, mask the entire query
                return "[MASKED_SENSITIVE_QUERY]"

        # For very long queries, truncate for logging
        if len(query) > 100:
            return query[:97] + "..."

        return masked_query

    def get_step_type(self) -> str:
        """Return the step type identifier for this executor."""
        return "webSearch"
