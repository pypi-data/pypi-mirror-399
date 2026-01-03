"""MCP Client for connecting to and communicating with MCP servers."""

from __future__ import annotations

import asyncio
from contextlib import AsyncExitStack
from typing import Any

from agent_flows.exceptions import (
    MCPConnectionError,
    MCPError,
    MCPTimeoutError,
    MCPToolError,
)
from agent_flows.utils.logging import get_logger

try:  # Optional dependency; defer friendly error until runtime usage
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    _MCP_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency path
    ClientSession = None  # type: ignore[assignment]
    StdioServerParameters = None  # type: ignore[assignment]
    stdio_client = None  # type: ignore[assignment]
    _MCP_AVAILABLE = False

logger = get_logger(__name__)


class MCPClient:
    """Reusable MCP client for connecting to and communicating with MCP servers."""

    def __init__(self) -> None:
        """Initialize the MCP client."""
        self.session: ClientSession | None = None  # type: ignore
        self.exit_stack = AsyncExitStack()
        self._connected = False
        self._server_info: dict[str, Any] = {}

    async def connect_to_server(
        self,
        command: str,
        args: list[str],
        env: dict[str, str] | None = None,
        timeout: int = 30,
    ) -> None:
        """Connect to an MCP server.

        Args:
            command: Command to start the server
            args: Arguments for the server command
            env: Environment variables for the server
            timeout: Connection timeout in seconds

        Raises:
            ExecutorError: If connection fails
        """
        if not _MCP_AVAILABLE:
            raise MCPConnectionError("MCP SDK not available. Install with: pip install mcp")

        try:
            logger.info(
                "Connecting to MCP server",
                command=command,
                args=args,
                env_vars=list(env.keys()) if env else [],
            )

            # Create server parameters
            server_params = StdioServerParameters(
                command=command,
                args=args,
                env=env,
            )

            # Connect to the server with timeout
            stdio_transport = await asyncio.wait_for(
                self.exit_stack.enter_async_context(stdio_client(server_params)),
                timeout=timeout,
            )

            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            # Initialize the session
            await asyncio.wait_for(self.session.initialize(), timeout=timeout)

            # Get server info and available tools
            response = await self.session.list_tools()
            tools = response.tools

            self._server_info = {
                "tools": [{"name": tool.name, "description": tool.description} for tool in tools],
                "tool_count": len(tools),
            }

            self._connected = True

            logger.info(
                "Successfully connected to MCP server",
                tool_count=len(tools),
                tools=[tool.name for tool in tools],
            )

        except TimeoutError as e:
            raise MCPTimeoutError(f"MCP server connection timed out after {timeout}s") from e
        except Exception as e:
            raise MCPConnectionError(f"Failed to connect to MCP server: {str(e)}") from e

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        timeout: int = 60,
    ) -> dict[str, Any]:
        """Call a tool on the connected MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            timeout: Tool execution timeout in seconds

        Returns:
            Tool execution result

        Raises:
            ExecutorError: If tool call fails or client is not connected
        """
        if not self._connected or not self.session:
            raise MCPConnectionError("MCP client is not connected to a server")

        try:
            logger.debug(
                "Calling MCP tool",
                tool_name=tool_name,
                arguments=arguments,
            )

            # Execute the tool call with timeout
            result = await asyncio.wait_for(
                self.session.call_tool(tool_name, arguments),
                timeout=timeout,
            )

            logger.debug(
                "MCP tool call completed",
                tool_name=tool_name,
                result_type=type(result.content).__name__,
            )

            # Process the result
            return self._process_tool_result(result, tool_name)

        except TimeoutError as e:
            raise MCPTimeoutError(
                f"MCP tool '{tool_name}' timed out after {timeout}s", tool_name
            ) from e
        except Exception as e:
            raise MCPToolError(
                f"MCP tool '{tool_name}' execution failed: {str(e)}", tool_name
            ) from e

    def _process_tool_result(self, result: Any, tool_name: str) -> dict[str, Any]:
        """Process MCP tool result into a standardized format.

        Args:
            result: Raw MCP tool result
            tool_name: Name of the tool that was called

        Returns:
            Processed result with separated content and metadata
        """
        try:
            # Extract content from the result
            content = result.content if hasattr(result, "content") else result

            # Handle different content types
            if isinstance(content, list):
                processed_content = []
                for item in content:
                    if hasattr(item, "text"):
                        processed_content.append(item.text)
                    elif isinstance(item, dict) and "text" in item:
                        processed_content.append(item["text"])
                    else:
                        processed_content.append(str(item))
                clean_content = "\n".join(processed_content)
            elif hasattr(content, "text"):
                clean_content = content.text
            elif isinstance(content, dict) and "text" in content:
                clean_content = content["text"]
            else:
                clean_content = str(content)

            # Extract metadata
            metadata = {
                "tool_name": tool_name,
                "content_type": type(content).__name__,
                "raw_result": result,
            }

            # Add any additional metadata from the result
            if hasattr(result, "isError"):
                metadata["is_error"] = result.isError

            return {
                "content": clean_content,
                "metadata": metadata,
            }

        except Exception as e:  # pragma: no cover - defensive guard
            logger.warning(
                "Failed to process MCP tool result, returning raw result",
                tool_name=tool_name,
                error=str(e),
            )
            return {
                "content": str(result),
                "metadata": {
                    "tool_name": tool_name,
                    "processing_error": str(e),
                    "raw_result": result,
                },
            }

    async def list_tools(self) -> list[dict[str, Any]]:
        """List available tools on the connected server.

        Returns:
            List of available tools with their descriptions

        Raises:
            ExecutorError: If client is not connected
        """
        if not self._connected or not self.session:
            raise MCPConnectionError("MCP client is not connected to a server")

        try:
            response = await self.session.list_tools()
            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in response.tools
            ]
        except Exception as e:
            raise MCPError(f"Failed to list MCP tools: {str(e)}") from e

    def get_server_info(self) -> dict[str, Any]:
        """Get information about the connected server.

        Returns:
            Server information including available tools

        Raises:
            ExecutorError: If client is not connected
        """
        if not self._connected:
            raise MCPConnectionError("MCP client is not connected to a server")

        return self._server_info.copy()

    def is_connected(self) -> bool:
        """Check if the client is connected to a server.

        Returns:
            True if connected, False otherwise
        """
        return self._connected

    async def disconnect(self) -> None:
        """Disconnect from the MCP server and clean up resources."""
        if self._connected:
            logger.info("Disconnecting from MCP server")
            try:
                await self.exit_stack.aclose()
            except Exception as e:  # pragma: no cover - defensive guard
                logger.warning("Error during MCP client cleanup", error=str(e))
            finally:
                self._connected = False
                self.session = None
                self._server_info = {}

    async def __aenter__(self) -> MCPClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.disconnect()
