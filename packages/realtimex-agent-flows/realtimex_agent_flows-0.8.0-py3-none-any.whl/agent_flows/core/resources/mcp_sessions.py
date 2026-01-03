"""MCP session pool for managing persistent connections across flow execution."""

from typing import Any

from agent_flows.integrations import MCPClient
from agent_flows.models.shared import MCPProvider
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class MCPSessionPool:
    """Manages persistent MCP sessions per flow execution."""

    def __init__(self, flow_id: str) -> None:
        """Initialize session pool for a flow.

        Args:
            flow_id: Unique flow identifier
        """
        self.flow_id = flow_id
        self._sessions: dict[str, MCPClient] = {}

    async def get_session(
        self,
        provider: MCPProvider,
        server_id: str,
        connection_params: dict[str, Any],
        timeout: int = 30,
    ) -> MCPClient:
        """Get or create persistent session for MCP server.

        Args:
            provider: MCP provider type
            server_id: Server identifier
            connection_params: Connection parameters (command, args, env)
            timeout: Connection timeout

        Returns:
            Persistent MCPClient instance
        """
        session_key = f"{provider.value}:{server_id}"

        # Check if we have a healthy existing session
        if session_key in self._sessions:
            client = self._sessions[session_key]
            if client.is_connected():
                log.debug("Reusing existing MCP session", session_key=session_key)
                return client
            else:
                log.info("Removing unhealthy MCP session", session_key=session_key)
                await client.disconnect()
                del self._sessions[session_key]

        # Create new session
        log.info("Creating new MCP session", session_key=session_key, flow_id=self.flow_id)
        client = MCPClient()

        await client.connect_to_server(
            command=connection_params["command"],
            args=connection_params["args"],
            env=connection_params.get("env"),
            timeout=timeout,
        )

        self._sessions[session_key] = client
        return client

    async def close_all(self) -> None:
        """Close all sessions and clean up resources."""
        if not self._sessions:
            return

        log.info(
            "Closing MCP session pool", flow_id=self.flow_id, session_count=len(self._sessions)
        )

        for session_key, client in self._sessions.items():
            try:
                await client.disconnect()
            except Exception as e:
                log.warning("Error closing MCP session", session_key=session_key, error=str(e))

        self._sessions.clear()

    def get_active_sessions(self) -> list[str]:
        """Get list of active session keys for debugging."""
        return [key for key, client in self._sessions.items() if client.is_connected()]
