"""Configuration models for the package."""

import os
import sys
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator


class LoggingConfig(BaseModel):
    """Configuration for structured logging."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Minimum log level emitted by the package"
    )
    json_format: bool = Field(
        default=True,
        description="Emit logs as JSON (True) or human-readable console output (False)",
    )

    @field_validator("json_format", mode="before")
    @classmethod
    def validate_json_format(cls, v: Any) -> bool:
        """Validate and coerce json_format field to boolean."""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        if isinstance(v, int):
            return bool(v)
        raise ValueError("json_format must be a boolean or string representation of boolean")


class LiteLLMConfig(BaseModel):
    """Configuration for LiteLLM integration."""

    api_key: str = Field(default="", description="API key for LiteLLM")
    api_base: str = Field(default="", description="Base URL for LiteLLM API")

    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        """Validate API base URL format - only if not empty."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("LiteLLM API base must start with http:// or https://")
        return v.rstrip("/") if v else v


class LLMProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""

    credentials: dict[str, str] = Field(
        default_factory=dict, description="Provider credentials (API keys, endpoints, etc.)"
    )

    @field_validator("credentials")
    @classmethod
    def validate_credentials(cls, v: dict[str, str]) -> dict[str, str]:
        """Validate credentials is a dictionary of strings."""
        if not isinstance(v, dict):
            raise ValueError("Credentials must be a dictionary")
        for key, value in v.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("All credential keys and values must be strings")
        return v


class LLMProvidersConfig(BaseModel):
    """Configuration for all LLM providers."""

    providers: dict[str, LLMProviderConfig] = Field(
        default_factory=dict, description="Provider configurations keyed by provider name"
    )
    default_provider: str | None = Field(None, description="Default provider name")

    @field_validator("providers")
    @classmethod
    def validate_providers(cls, v: dict[str, LLMProviderConfig]) -> dict[str, LLMProviderConfig]:
        """Validate providers dictionary."""
        if not isinstance(v, dict):
            raise ValueError("Providers must be a dictionary")
        return v

    @field_validator("default_provider")
    @classmethod
    def validate_default_provider(cls, v: str | None, info) -> str | None:
        """Validate default provider exists in providers."""
        if v is not None and "providers" in info.data:
            providers = info.data["providers"]
            if v not in providers:
                raise ValueError(f"Default provider '{v}' not found in providers")
        return v


class MCPConfig(BaseModel):
    """Configuration for MCP (Model Context Protocol) integration."""

    aci_api_key: str = Field(default="", description="API key for ACI MCP integration")
    aci_linked_account_owner_id: str = Field(
        default="", description="Linked account owner ID for ACI MCP"
    )


class AgentFlowsConfig(BaseModel):
    """Configuration for Agent Flows package."""

    # RealTimeX API Configuration
    api_key: str = Field(default="", description="API key for RealTimeX instance")
    base_url: str = Field(
        default="https://marketplace-api.realtimex.ai", description="Base URL of RealTimeX instance"
    )
    app_base_url: str = Field(
        default="http://localhost:3001",
        description="Base URL of the RealTimeX app backend",
    )
    load_system_variables: bool = Field(
        default=True,
        description="Fetch system prompt variables from the app backend during initialization",
    )
    timeout: int = Field(30, description="Request timeout in seconds")
    max_retries: int = Field(3, description="Maximum retry attempts")

    # Caching Configuration
    cache_enabled: bool = Field(True, description="Enable flow configuration caching")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")

    # Logging Configuration
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig,
        description="Structured logging configuration for Agent Flows",
    )

    # LLM Providers Configuration
    llm_providers: LLMProvidersConfig = Field(
        default_factory=LLMProvidersConfig, description="LLM providers configuration"
    )

    # LiteLLM Configuration (legacy)
    litellm: LiteLLMConfig = Field(
        default_factory=LiteLLMConfig, description="LiteLLM configuration (legacy)"
    )

    # MCP Configuration
    mcp: MCPConfig = Field(default_factory=MCPConfig, description="MCP configuration")

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout is positive."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @field_validator("max_retries")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries is non-negative."""
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v

    @field_validator("cache_ttl")
    @classmethod
    def validate_cache_ttl(cls, v: int) -> int:
        """Validate cache TTL is positive."""
        if v <= 0:
            raise ValueError("Cache TTL must be positive")
        return v

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format - only if not empty."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return v.rstrip("/") if v else v

    @field_validator("app_base_url")
    @classmethod
    def validate_app_base_url(cls, v: str) -> str:
        """Validate app base URL format - only if not empty."""
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("App base URL must start with http:// or https://")
        return v.rstrip("/") if v else v

    @classmethod
    def from_env(cls, require_api_key: bool = True) -> "AgentFlowsConfig":
        """
        Create configuration from environment variables.

        This method centralizes environment variable parsing and leverages Pydantic for
        robust, centralized validation.

        Args:
            require_api_key: If True, AGENT_FLOWS_API_KEY must be set.

        Returns:
            An instance of AgentFlowsConfig.

        Raises:
            SystemExit: If configuration is invalid.
        """
        try:
            # Gather all configuration data from environment variables
            config_data = cls._gather_env_vars()

            # Enforce the API key requirement if specified
            if require_api_key and not config_data.get("api_key"):
                raise ValueError("AGENT_FLOWS_API_KEY is required.")

            # Let Pydantic parse, validate, and create the config object
            return cls.model_validate(config_data)

        except (ValidationError, ValueError) as e:
            cls._handle_config_error(e, require_api_key)

    @staticmethod
    def _gather_env_vars() -> dict[str, Any]:
        """Collect all configuration values from environment variables into a dict."""
        return {
            "api_key": os.getenv("AGENT_FLOWS_API_KEY", ""),
            "base_url": os.getenv("AGENT_FLOWS_BASE_URL", "https://marketplace-api.realtimex.ai"),
            "app_base_url": os.getenv("AGENT_FLOWS_APP_BASE_URL", "http://localhost:3001"),
            "load_system_variables": os.getenv("AGENT_FLOWS_LOAD_SYSTEM_VARIABLES", "true").lower() == "true",
            "timeout": os.getenv("AGENT_FLOWS_TIMEOUT", "30"),
            "max_retries": os.getenv("AGENT_FLOWS_MAX_RETRIES", "3"),
            "cache_enabled": os.getenv("AGENT_FLOWS_CACHE_ENABLED", "true").lower() == "true",
            "cache_ttl": os.getenv("AGENT_FLOWS_CACHE_TTL", "3600"),
            "logging": {
                "level": os.getenv("AGENT_FLOWS_LOG_LEVEL", "INFO"),
                "json_format": os.getenv("AGENT_FLOWS_LOG_JSON", "true"),
            },
            "litellm": {
                "api_key": os.getenv("LITELLM_API_KEY", ""),
                "api_base": os.getenv("LITELLM_API_BASE", ""),
            },
            "mcp": {
                "aci_api_key": os.getenv("MCP_ACI_API_KEY", ""),
                "aci_linked_account_owner_id": os.getenv("MCP_ACI_LINKED_ACCOUNT_OWNER_ID", ""),
            },
        }  # fmt: skip

    @staticmethod
    def _handle_config_error(error: Exception, require_api_key: bool):
        """Print formatted error messages and exit."""
        print("❌ Configuration Error: Invalid environment variables detected", file=sys.stderr)
        print("", file=sys.stderr)

        if isinstance(error, ValidationError):
            for err in error.errors():
                # Provides cleaner error messages like "log_level: Input should be..."
                field_name = ".".join(map(str, err["loc"]))
                print(f"  • {field_name}: {err['msg']}", file=sys.stderr)
        else:
            # For direct ValueErrors like the missing API key
            print(f"  • {error}", file=sys.stderr)

        print("", file=sys.stderr)
        print("💡 Setup Guide:", file=sys.stderr)
        print("", file=sys.stderr)
        if require_api_key:
            print("  Required environment variables:", file=sys.stderr)
            print("    export AGENT_FLOWS_API_KEY='your-realtimex-api-key'", file=sys.stderr)
            print("", file=sys.stderr)
        print("  Optional environment variables:", file=sys.stderr)
        print(
            "    export AGENT_FLOWS_BASE_URL='https://your-realtimex-instance.com'", file=sys.stderr
        )
        print(
            "    export AGENT_FLOWS_APP_BASE_URL='http://localhost:3001'",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print("  Optional LLM configuration:", file=sys.stderr)
        print("    export LITELLM_API_KEY='your-llm-api-key'", file=sys.stderr)
        print("    export LITELLM_API_BASE='https://api.openai.com/v1'", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Optional MCP configuration:", file=sys.stderr)
        print("    export MCP_ACI_API_KEY='your-aci-api-key'", file=sys.stderr)
        print(
            "    export MCP_ACI_LINKED_ACCOUNT_OWNER_ID='your-linked-account-owner-id'",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        sys.exit(1)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()
