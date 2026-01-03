"""Runtime resource management services."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .credentials import CredentialManager
    from .interpolation import VariableInterpolator
    from .mcp_sessions import MCPSessionPool
    from .variables import VariableManager


def __getattr__(name: str) -> type:
    """Lazy import for resource services."""
    if name == "CredentialManager":
        from .credentials import CredentialManager

        return CredentialManager
    if name == "VariableInterpolator":
        from .interpolation import VariableInterpolator

        return VariableInterpolator
    if name == "MCPSessionPool":
        from .mcp_sessions import MCPSessionPool

        return MCPSessionPool
    if name == "VariableManager":
        from .variables import VariableManager

        return VariableManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["CredentialManager", "VariableInterpolator", "MCPSessionPool", "VariableManager"]
