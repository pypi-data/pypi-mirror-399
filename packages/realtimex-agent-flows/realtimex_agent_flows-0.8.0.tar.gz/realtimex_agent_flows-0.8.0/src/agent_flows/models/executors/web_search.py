"""Web Search executor configuration model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..shared import (
    OutputMixin,
    SearchProvider,
    SearchProviderDefinition,
    SearchType,
    TimeoutRetryMixin,
)


class WebSearchProviderConfig(BaseModel):
    """Enhanced provider configuration supporting fallbacks."""

    model_config = ConfigDict(extra="allow")

    name: SearchProvider = Field(..., description="Primary search provider")
    config: dict[str, Any] = Field(
        default_factory=dict, description="Provider-specific configuration"
    )
    fallbacks: list[SearchProviderDefinition] = Field(
        default_factory=list, description="Fallback providers in priority order"
    )

    @field_validator("fallbacks")
    @classmethod
    def validate_fallbacks(
        cls, v: list[SearchProviderDefinition]
    ) -> list[SearchProviderDefinition]:
        """Validate fallback providers."""
        if len(v) > 5:  # Reasonable limit
            raise ValueError("Maximum of 5 fallback providers allowed")

        # Check for duplicate providers
        provider_names = [fallback.name for fallback in v]
        if len(provider_names) != len(set(provider_names)):
            raise ValueError("Duplicate providers in fallbacks list")

        return v

    @model_validator(mode="after")
    def validate_primary_not_in_fallbacks(self) -> "WebSearchProviderConfig":
        """Ensure primary provider is not in fallbacks list."""
        fallback_names = [fallback.name for fallback in self.fallbacks]
        if self.name.value in fallback_names:
            raise ValueError("Primary provider cannot be in fallbacks list")
        return self


class WebSearchExecutorConfig(OutputMixin, TimeoutRetryMixin, BaseModel):
    """Configuration for WebSearchExecutor."""

    model_config = ConfigDict(extra="allow")

    query: str = Field(..., description="Search query string")
    provider: WebSearchProviderConfig = Field(..., description="Search provider configuration")
    maxResults: int = Field(
        10, ge=1, le=100, description="Maximum number of search results to return"
    )
    searchType: SearchType = Field(SearchType.SEARCH, description="Type of search to perform")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query is not empty."""
        if not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()

    @model_validator(mode="after")
    def validate_provider_config_requirements(self) -> "WebSearchExecutorConfig":
        """Validate provider-specific configuration requirements."""
        # Validate primary provider configuration
        self._validate_provider_specific_config(self.provider.name, self.provider.config)

        # Validate fallback configurations
        for fallback in self.provider.fallbacks:
            fallback_provider = SearchProvider(fallback.name)
            self._validate_provider_specific_config(fallback_provider, fallback.config)

        return self

    def _validate_provider_specific_config(
        self, provider: SearchProvider, config: dict[str, Any]
    ) -> None:
        """Validate provider-specific configuration requirements."""
        if provider == SearchProvider.GOOGLE:
            required_fields = ["apiKey", "searchEngineId"]
            for field in required_fields:
                if field not in config or not config[field]:
                    raise ValueError(f"Google Search provider requires '{field}' in config")

        elif provider == SearchProvider.BING:
            if "apiKey" not in config or not config["apiKey"]:
                raise ValueError("Bing Search provider requires 'apiKey' in config")

        elif provider == SearchProvider.SERPAPI:
            if "apiKey" not in config or not config["apiKey"]:
                raise ValueError("SerpAPI provider requires 'apiKey' in config")

        elif provider == SearchProvider.SERPLY:
            if "apiKey" not in config or not config["apiKey"]:
                raise ValueError("Serply provider requires 'apiKey' in config")

        elif provider == SearchProvider.SEARXNG:
            if "baseUrl" not in config or not config["baseUrl"]:
                raise ValueError("SearXNG provider requires 'baseUrl' in config")

        elif provider == SearchProvider.TAVILY:
            if "apiKey" not in config or not config["apiKey"]:
                raise ValueError("Tavily provider requires 'apiKey' in config")

        # DuckDuckGo requires no configuration
