"""Package-wide exception classes."""

from typing import Any


class AgentFlowsError(Exception):
    """Base exception for all Agent Flows errors."""

    def __init__(self, message: str = "") -> None:
        super().__init__(message)

    @property
    def message(self) -> str:
        return self.args[0] if self.args else ""

    def __str__(self) -> str:  # pragma: no cover - default formatting
        return self.message or super().__str__()


class FlowError(AgentFlowsError):
    """Base class for user flow related errors."""

    pass


class FlowExecutionError(FlowError):
    """Raised when flow execution fails."""

    pass


class ConfigurationError(FlowError):
    """Raised when flow configuration is invalid."""

    pass


class ExecutorError(FlowError):
    """Raised when an executor fails during flow execution."""

    pass


class ExecutorNotFoundError(AgentFlowsError):
    """Raised when the requested executor is not registered."""

    pass


class ApiError(AgentFlowsError):
    """Raised when API communication fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message)

    def __str__(self) -> str:
        message = self.message or "API error"
        if self.status_code is not None:
            return f"{message} | Status: {self.status_code}"
        return message


class ConnectionError(ApiError):
    """Raised when network connection fails."""

    pass


class ResourceNotFoundError(ApiError):
    """Raised when a requested resource cannot be located (HTTP 404).

    This is a generic 404 error for any resource type. Use specialized
    subclasses like FlowNotFoundError for domain-specific resources.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: int | None = 404,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_body=response_body)


class FlowNotFoundError(ResourceNotFoundError):
    """Raised when a requested flow cannot be located."""

    def __init__(
        self,
        flow_id: str | None = None,
        status_code: int | None = 404,
        response_body: str | None = None,
    ) -> None:
        self.flow_id = flow_id
        message = "Flow not found" if flow_id is None else f"Flow not found: {flow_id}"
        super().__init__(message, status_code=status_code, response_body=response_body)


class AuthenticationError(ApiError):
    """Raised when API authentication fails."""

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_body=response_body)


class RateLimitError(ApiError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int | None = None,
        response_body: str | None = None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_body=response_body)
        self.retry_after = retry_after


class ServerError(ApiError):
    """Raised when server returns 5xx error."""

    def __init__(
        self,
        message: str = "Server error",
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code, response_body=response_body)


class IntegrationError(AgentFlowsError):
    """Base class for integration-related errors."""

    pass


class MCPError(IntegrationError):
    """Base exception for MCP client errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class MCPConnectionError(MCPError):
    """Raised when MCP server connection fails."""

    pass


class MCPToolError(MCPError):
    """Raised when MCP tool execution fails."""

    def __init__(
        self,
        message: str,
        tool_name: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.tool_name = tool_name
        super().__init__(message, details=details)

    def __str__(self) -> str:
        parts = [self.message]
        if self.tool_name:
            parts.append(f"Tool: {self.tool_name}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


class MCPTimeoutError(MCPError):
    """Raised when MCP operations timeout."""

    pass


class CredentialError(IntegrationError):
    """Raised when credential retrieval or decryption fails."""

    def __init__(
        self,
        message: str,
        *,
        credential_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.credential_id = credential_id
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        base = self.message or "Credential error"
        extras: list[str] = []
        if self.credential_id:
            extras.append(f"id={self.credential_id}")
        if self.details:
            extras.append(f"details={self.details}")
        if extras:
            return f"{base} ({', '.join(extras)})"
        return base


class SystemVariableError(IntegrationError):
    """Raised when system variable retrieval fails."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


__all__ = [
    "AgentFlowsError",
    "FlowError",
    "FlowExecutionError",
    "ConfigurationError",
    "ExecutorError",
    "ExecutorNotFoundError",
    "ApiError",
    "ResourceNotFoundError",
    "FlowNotFoundError",
    "IntegrationError",
    "CredentialError",
    "SystemVariableError",
    "MCPError",
]
