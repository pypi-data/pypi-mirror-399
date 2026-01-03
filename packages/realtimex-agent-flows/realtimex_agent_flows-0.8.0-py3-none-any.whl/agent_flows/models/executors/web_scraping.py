"""Web Scraping executor configuration model using Crawl4AI."""

from __future__ import annotations

from typing import Any, Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..shared import CommonValidators, OutputMixin, TimeoutMixin, UserAgentMode

# ============================================================================
# Content Selection Models
# ============================================================================


class ContentSelectionConfig(BaseModel):
    """Configuration for selecting specific page content."""

    cssSelector: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
        description="Single CSS selector for content scope",
    )
    targetElements: list[str] | None = Field(
        default=None,
        min_length=1,
        max_length=20,
        description="Multiple CSS selectors for targeted extraction",
    )

    @field_validator("targetElements")
    @classmethod
    def validate_target_elements(cls, v: list[str] | None) -> list[str] | None:
        """Validate target elements are non-empty."""
        if v is not None:
            for elem in v:
                if not elem.strip():
                    raise ValueError("Target elements cannot be empty strings")
        return v

    @model_validator(mode="after")
    def validate_mutual_exclusivity(self) -> ContentSelectionConfig:
        """Ensure cssSelector and targetElements are mutually exclusive."""
        if self.cssSelector and self.targetElements:
            raise ValueError("Cannot specify both cssSelector and targetElements")
        return self


# ============================================================================
# Content Filtering Models
# ============================================================================


class LinkFilteringConfig(BaseModel):
    """Configuration for link filtering."""

    excludeExternal: bool = Field(default=False, description="Exclude external links")
    excludeSocialMedia: bool = Field(default=False, description="Exclude social media links")
    excludeDomains: list[str] | None = Field(
        default=None, max_length=50, description="Custom domain blocklist"
    )

    @field_validator("excludeDomains")
    @classmethod
    def validate_domains(cls, v: list[str] | None) -> list[str] | None:
        """Validate domain format."""
        if v is not None:
            for domain in v:
                if not domain.strip():
                    raise ValueError("Domain cannot be empty")
        return v


class MediaFilteringConfig(BaseModel):
    """Configuration for media filtering."""

    excludeExternalImages: bool = Field(default=False, description="Exclude external images")


class ContentFilteringConfig(BaseModel):
    """Configuration for filtering page content."""

    excludedTags: list[str] | None = Field(
        default=None, max_length=30, description="HTML tags to exclude"
    )
    wordCountThreshold: int | None = Field(
        default=None, ge=0, le=1000, description="Minimum words per text block"
    )
    links: LinkFilteringConfig | None = Field(default=None, description="Link filtering options")
    media: MediaFilteringConfig | None = Field(default=None, description="Media filtering options")
    processIframes: bool = Field(default=False, description="Merge iframe content")
    removeOverlays: bool = Field(default=False, description="Remove overlay elements")

    @field_validator("excludedTags")
    @classmethod
    def validate_excluded_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate excluded tags are non-empty."""
        if v is not None:
            for tag in v:
                if not tag.strip():
                    raise ValueError("Excluded tags cannot be empty strings")
        return v


# ============================================================================
# Output Format Models
# ============================================================================


class MarkdownOutputOptions(BaseModel):
    """Options for markdown output."""

    includeCitations: bool = Field(default=False, description="Include inline citations")
    includeReferences: bool = Field(default=False, description="Include reference list")
    bodyWidth: int = Field(default=0, ge=0, le=200, description="Markdown body width (0=no wrap)")


class HtmlOutputOptions(BaseModel):
    """Options for HTML output."""

    variant: Literal["raw", "cleaned", "fit"] = Field(
        default="cleaned", description="HTML output variant"
    )


class CssFieldConfig(BaseModel):
    """CSS selector field configuration."""

    name: str = Field(..., min_length=1, max_length=100, description="Field name")
    selector: str = Field(..., min_length=1, max_length=500, description="CSS selector")
    type: Literal["text", "attribute", "html", "nested"] = Field(..., description="Extraction type")
    attribute: str | None = Field(default=None, max_length=100, description="HTML attribute name")
    fields: list[CssFieldConfig] | None = Field(default=None, description="Nested fields")

    @model_validator(mode="after")
    def validate_attribute_requirement(self) -> CssFieldConfig:
        """Validate attribute field requirements."""
        if self.type == "attribute" and not self.attribute:
            raise ValueError("attribute field is required when type='attribute'")
        if self.type != "attribute" and self.attribute:
            raise ValueError("attribute field should only be set when type='attribute'")
        if self.type == "nested" and not self.fields:
            raise ValueError("fields are required when type='nested'")
        if self.type != "nested" and self.fields:
            raise ValueError("fields should only be set when type='nested'")
        return self


class CssExtractionConfig(BaseModel):
    """CSS-based structured extraction configuration."""

    baseSelector: str = Field(..., min_length=1, max_length=500, description="Base CSS selector")
    fields: list[CssFieldConfig] = Field(
        ..., min_length=1, max_length=50, description="Fields to extract"
    )

    @field_validator("fields")
    @classmethod
    def validate_unique_field_names(cls, v: list[CssFieldConfig]) -> list[CssFieldConfig]:
        """Ensure field names are unique."""
        field_names = [field.name for field in v]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Field names must be unique")
        return v


class LlmSchemaConfig(BaseModel):
    """JSON Schema configuration for LLM extraction."""

    type: Literal["object"] = Field(default="object", description="Schema type")
    properties: dict[str, Any] = Field(..., min_length=1, description="Schema properties")
    required: list[str] | None = Field(default=None, description="Required fields")

    @field_validator("properties")
    @classmethod
    def validate_properties(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate properties are non-empty."""
        if not v:
            raise ValueError("Schema properties cannot be empty")
        return v


class LlmExtractionConfig(BaseModel):
    """LLM-based structured extraction configuration."""

    model_config = ConfigDict(populate_by_name=True)

    provider: str | None = Field(None, description="LLM provider (e.g., 'openai', 'anthropic')")
    model: str = Field(default="auto", max_length=100, description="LLM model identifier")
    instruction: str = Field(..., min_length=1, description="Extraction instruction for LLM")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Model temperature")
    extractionType: Literal["schema", "block"] = Field(
        ..., description="Extraction mode: schema=structured JSON, block=freeform text"
    )
    schema_config: LlmSchemaConfig | None = Field(
        default=None,
        alias="schema",
        serialization_alias="schema",
        description="JSON schema (for schema mode)",
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str | None) -> str | None:
        """Normalize provider name."""
        if v is not None:
            if not v.strip():
                raise ValueError("Provider name cannot be empty")
            return v.strip().lower()
        return v

    @model_validator(mode="after")
    def validate_schema_requirement(self) -> LlmExtractionConfig:
        """Validate schema requirements based on extraction type."""
        if self.extractionType == "schema" and not self.schema_config:
            raise ValueError("schema is required when extractionType='schema'")
        if self.extractionType == "block" and self.schema_config:
            raise ValueError("schema should not be provided when extractionType='block'")
        return self


class StructuredOutputOptions(BaseModel):
    """Options for structured data output."""

    method: Literal["css", "llm"] = Field(..., description="Extraction method")
    css: CssExtractionConfig | None = Field(default=None, description="CSS extraction config")
    llm: LlmExtractionConfig | None = Field(default=None, description="LLM extraction config")

    @model_validator(mode="after")
    def validate_method_config(self) -> StructuredOutputOptions:
        """Validate method-specific configuration."""
        if self.method == "css" and not self.css:
            raise ValueError("css config is required when method='css'")
        if self.method == "llm" and not self.llm:
            raise ValueError("llm config is required when method='llm'")
        if self.method == "css" and self.llm:
            raise ValueError("llm config should not be provided when method='css'")
        if self.method == "llm" and self.css:
            raise ValueError("css config should not be provided when method='llm'")
        return self


class OutputOptionsConfig(BaseModel):
    """Output format options."""

    markdown: MarkdownOutputOptions | None = Field(default=None, description="Markdown options")
    html: HtmlOutputOptions | None = Field(default=None, description="HTML options")
    structured: StructuredOutputOptions | None = Field(
        default=None, description="Structured data extraction options"
    )


# ============================================================================
# Browser & Page Configuration Models
# ============================================================================


class ProxyConfig(BaseModel):
    """Proxy server configuration."""

    server: str = Field(..., min_length=1, max_length=500, description="Proxy server URL")
    username: str | None = Field(default=None, max_length=100, description="Proxy username")
    password: str | None = Field(default=None, max_length=100, description="Proxy password")

    @field_validator("server")
    @classmethod
    def validate_proxy_server(cls, v: str) -> str:
        """Validate proxy server URL format."""
        try:
            parsed = urlparse(v.strip())
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Proxy server must be a valid URL")
            if parsed.scheme not in ["http", "https", "socks4", "socks5"]:
                raise ValueError("Proxy scheme must be http, https, socks4, or socks5")
        except Exception as e:
            raise ValueError(f"Invalid proxy server URL: {str(e)}") from e
        return v.strip()


class BrowserConfig(BaseModel):
    """Browser configuration."""

    headless: bool = Field(default=True, description="Run in headless mode")
    userAgentMode: UserAgentMode = Field(
        default=UserAgentMode.RANDOM, description="User agent mode"
    )
    userAgent: str | None = Field(
        default=None, max_length=500, description="Custom user agent string"
    )
    textMode: bool = Field(default=True, description="Disable images for faster crawling")
    proxy: ProxyConfig | None = Field(default=None, description="Proxy configuration")

    @model_validator(mode="after")
    def validate_user_agent_config(self) -> BrowserConfig:
        """Validate user agent configuration."""
        if self.userAgentMode == UserAgentMode.DEFAULT and self.userAgent is None:
            raise ValueError("userAgent must be provided when userAgentMode is 'default'")
        if self.userAgentMode == UserAgentMode.RANDOM and self.userAgent is not None:
            raise ValueError("userAgent should not be provided when userAgentMode is 'random'")
        return self


class PageConfig(BaseModel):
    """Page interaction configuration."""

    waitFor: str | None = Field(default=None, max_length=1000, description="Wait condition")
    timeoutMs: int = Field(
        default=60000, ge=1000, le=300000, description="Page timeout in milliseconds"
    )
    delayBeforeReturnHtml: float = Field(
        default=0.1, ge=0.0, description="Pause (seconds) before final HTML is captured"
    )

    @field_validator("waitFor")
    @classmethod
    def validate_wait_condition(cls, v: str | None) -> str | None:
        """Validate wait condition format."""
        if v is None:
            return v

        wait_condition = v.strip()
        if not wait_condition:
            return None

        if not (wait_condition.startswith("css:") or wait_condition.startswith("js:")):
            raise ValueError("waitFor must start with 'css:' or 'js:' prefix")

        condition_content = wait_condition[4:].strip()
        if not condition_content:
            raise ValueError("waitFor condition cannot be empty after prefix")

        return wait_condition


class RetryConfig(BaseModel):
    """Retry configuration."""

    attempts: int = Field(default=2, ge=0, le=10, description="Maximum retry attempts")


class AdvancedConfig(BaseModel):
    """Advanced scraping features."""

    tableScoreThreshold: int = Field(
        default=7, ge=0, le=20, description="Minimum score for table detection"
    )
    captureScreenshot: bool = Field(default=False, description="Capture page screenshot")
    capturePdf: bool = Field(default=False, description="Capture page as PDF")
    captureMhtml: bool = Field(default=False, description="Capture page as MHTML")


# ============================================================================
# Main Configuration Model
# ============================================================================


class WebScrapingExecutorConfig(OutputMixin, TimeoutMixin, BaseModel):
    """Configuration for WebScrapingExecutor using Crawl4AI."""

    model_config = ConfigDict(extra="allow", use_enum_values=True)

    urls: list[str] = Field(..., min_length=1, max_length=100, description="URLs to scrape")

    # Content selection and filtering
    contentSelection: ContentSelectionConfig | None = Field(
        default=None, description="Content selection configuration"
    )
    contentFiltering: ContentFilteringConfig | None = Field(
        default=None, description="Content filtering configuration"
    )

    # Output format
    outputFormat: Literal["markdown", "html", "structured"] = Field(
        default="markdown", description="Output format"
    )
    outputOptions: OutputOptionsConfig | None = Field(
        default=None, description="Output format options"
    )

    # Browser and page configuration
    browser: BrowserConfig | None = Field(default=None, description="Browser configuration")
    page: PageConfig | None = Field(default=None, description="Page configuration")
    retry: RetryConfig | None = Field(default=None, description="Retry configuration")

    # Advanced features
    advanced: AdvancedConfig | None = Field(default=None, description="Advanced features")

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[str]) -> list[str]:
        """Validate URLs format and uniqueness."""
        validated_urls = []

        for url in v:
            validated_url = CommonValidators.validate_url.__func__(CommonValidators, url)
            validated_urls.append(validated_url)

        if len(validated_urls) != len(set(validated_urls)):
            raise ValueError("Duplicate URLs are not allowed")

        return validated_urls

    @model_validator(mode="after")
    def validate_output_format_requirements(self) -> WebScrapingExecutorConfig:
        """Validate output format requirements."""
        if self.outputFormat == "structured" and (
            not self.outputOptions or not self.outputOptions.structured
        ):
            raise ValueError("outputOptions.structured is required when outputFormat='structured'")
        return self

    def get_browser_config(self) -> BrowserConfig:
        """Get browser configuration with defaults."""
        return self.browser or BrowserConfig()

    def get_page_config(self) -> PageConfig:
        """Get page configuration with defaults."""
        return self.page or PageConfig()

    def get_retry_config(self) -> RetryConfig:
        """Get retry configuration with defaults."""
        return self.retry or RetryConfig()

    def get_advanced_config(self) -> AdvancedConfig:
        """Get advanced configuration with defaults."""
        return self.advanced or AdvancedConfig()
