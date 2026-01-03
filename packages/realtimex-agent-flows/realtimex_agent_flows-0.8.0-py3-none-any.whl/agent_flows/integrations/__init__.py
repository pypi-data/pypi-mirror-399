"""External service integrations and adapters.

This package contains adapters for external services used by the agent flows system.
Each integration module provides a clean interface for interacting with external APIs
and services while abstracting implementation details from the core business logic.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .llm_providers import LLMProviderManager
    from .mcp_client import MCPClient


def __getattr__(name: str):
    """Lazy import for integration components."""
    if name == "LLMProviderManager":
        from .llm_providers import LLMProviderManager

        globals()[name] = LLMProviderManager
        return LLMProviderManager
    if name == "MCPClient":
        from .mcp_client import MCPClient

        globals()[name] = MCPClient
        return MCPClient
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "LLMProviderManager",
    "MCPClient",
]
