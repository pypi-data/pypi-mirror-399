"""HTTP error mapping strategies for API client."""

from __future__ import annotations

from typing import Protocol

from agent_flows.exceptions import (
    ApiError,
    AuthenticationError,
    FlowNotFoundError,
    RateLimitError,
    ResourceNotFoundError,
    ServerError,
)


class ErrorMapper(Protocol):
    """Protocol for mapping HTTP errors to domain exceptions."""

    def map_error(self, status: int, response_text: str) -> ApiError:
        """Map HTTP status code and response to appropriate exception.

        Args:
            status: HTTP status code
            response_text: Raw response body text

        Returns:
            Appropriate ApiError subclass instance
        """
        ...


class DefaultErrorMapper:
    """Default HTTP error mapping for generic API operations."""

    def map_error(self, status: int, response_text: str) -> ApiError:
        """Map common HTTP errors to exceptions."""
        if status == 401:
            return AuthenticationError(
                "Invalid API key or authentication failed",
                status_code=status,
                response_body=response_text,
            )
        if status == 403:
            return AuthenticationError(
                "Access forbidden - insufficient permissions",
                status_code=status,
                response_body=response_text,
            )
        if status == 404:
            return ResourceNotFoundError(
                message="Resource not found",
                status_code=status,
                response_body=response_text,
            )
        if status == 429:
            return RateLimitError(
                "Rate limit exceeded",
                status_code=status,
                response_body=response_text,
            )
        if status >= 500:
            return ServerError(
                f"Server error: {status}",
                status_code=status,
                response_body=response_text,
            )
        return ApiError(
            f"HTTP {status}: {response_text}",
            status_code=status,
            response_body=response_text,
        )


class FlowApiErrorMapper(DefaultErrorMapper):
    """Error mapper for Flow Registry operations that raises FlowNotFoundError for 404s."""

    def map_error(self, status: int, response_text: str) -> ApiError:
        """Map 404 errors to FlowNotFoundError, delegate others to default mapping."""
        if status == 404:
            return FlowNotFoundError(
                status_code=status,
                response_body=response_text,
            )
        return super().map_error(status, response_text)
