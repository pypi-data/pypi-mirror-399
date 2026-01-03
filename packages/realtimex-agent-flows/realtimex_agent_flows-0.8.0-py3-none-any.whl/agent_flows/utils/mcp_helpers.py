"""MCP connection utilities for local and remote server configuration."""

from typing import Any

import aiohttp

from agent_flows.exceptions import ExecutorError
from agent_flows.models.shared import MCPProvider
from agent_flows.utils.logging import get_logger
from agent_flows.utils.path_utils import get_uvx_executable, resolve_bundled_executable

log = get_logger(__name__)


class MCPConnectionHelper:
    """Simple helper for resolving MCP connection parameters."""

    @staticmethod
    async def get_connection_params(
        provider: MCPProvider,
        server_id: str,
        api_key: str,
        aci_api_key: str | None = None,
        aci_owner_id: str | None = None,
        timeout: int = 30,
    ) -> dict[str, Any]:
        """Get connection parameters for MCP server.

        Args:
            provider: MCP provider type (local or remote)
            server_id: Server identifier
            api_key: API key for local registry lookup
            aci_api_key: ACI API key for remote connections
            aci_owner_id: ACI linked account owner ID for remote connections
            timeout: Request timeout in seconds

        Returns:
            Dictionary with keys: command, args, env

        Raises:
            ExecutorError: If connection parameters cannot be resolved
        """
        if provider == MCPProvider.REMOTE:
            return MCPConnectionHelper._get_remote_connection_params(
                server_id, aci_api_key, aci_owner_id
            )
        elif provider == MCPProvider.LOCAL:
            config = await MCPConnectionHelper._get_local_server_config(server_id, api_key, timeout)
            if not config:
                raise ExecutorError(f"Local MCP server '{server_id}' not found in registry")
            return config
        else:
            raise ExecutorError(f"Unsupported MCP provider: {provider}")

    @staticmethod
    async def _get_local_server_config(
        server_id: str, api_key: str, timeout: int
    ) -> dict[str, Any] | None:
        """Fetch local server config from registry API.

        Args:
            server_id: Server identifier
            api_key: API key for authentication
            timeout: Request timeout in seconds

        Returns:
            Server configuration with command, args, env or None if not found
        """
        url = f"http://localhost:3001/api/mcp-servers/local/{server_id}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-App-Offline": "true",
        }

        try:
            async with (
                aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session,
                session.get(url, headers=headers) as response,
            ):
                if response.status == 404:
                    log.warning("Local MCP server not found", server_id=server_id)
                    return None

                if response.status != 200:
                    raise ExecutorError(
                        f"Failed to fetch local MCP server config: HTTP {response.status}"
                    )

                response_data = await response.json()

                # Check for API error response
                if not response_data.get("success"):
                    error_msg = response_data.get("error", "Unknown error")
                    raise ExecutorError(
                        f"Local MCP server registry error for '{server_id}': {error_msg}"
                    )

                # Extract server config
                server_data = response_data.get("server")
                if not server_data or "config" not in server_data:
                    raise ExecutorError(
                        f"Invalid response format from local MCP registry for '{server_id}'"
                    )

                config = server_data["config"]

                # Validate required fields
                if not isinstance(config, dict) or "command" not in config:
                    raise ExecutorError(
                        f"Invalid local MCP server config for '{server_id}': missing 'command' field"
                    )

                # Resolve bundled executable path
                config["command"] = resolve_bundled_executable(config["command"])

                # Ensure args and env have defaults
                config.setdefault("args", [])
                config.setdefault("env", {})

                log.info("Local MCP server config retrieved", server_id=server_id)
                return config

        except aiohttp.ClientError as e:
            raise ExecutorError(f"Failed to connect to local MCP registry: {str(e)}") from e
        except Exception as e:
            raise ExecutorError(f"Error retrieving local MCP server config: {str(e)}") from e

    @staticmethod
    def _get_remote_connection_params(
        server_id: str, aci_api_key: str | None, aci_owner_id: str | None
    ) -> dict[str, Any]:
        """Get remote MCP connection parameters.

        Args:
            server_id: Server identifier
            aci_api_key: ACI API key
            aci_owner_id: ACI linked account owner ID

        Returns:
            Connection parameters for remote MCP server

        Raises:
            ExecutorError: If required configuration is missing
        """
        if not aci_api_key:
            raise ExecutorError(
                "ACI API key is required for remote MCP connections. "
                "Please provide it in the executor context configuration."
            )
        if not aci_owner_id:
            raise ExecutorError(
                "ACI linked account owner ID is required for remote MCP connections. "
                "Please provide it in the executor context configuration."
            )

        mcp_command = get_uvx_executable()
        aci_server_url = "https://mcp.realtimex.ai"

        return {
            "command": mcp_command,
            "args": [
                "aci-mcp",
                "apps-server",
                "--apps",
                server_id,
                "--linked-account-owner-id",
                aci_owner_id,
            ],
            "env": {
                "ACI_SERVER_URL": f"{aci_server_url}/v1",
                "ACI_API_KEY": aci_api_key,
            },
        }
