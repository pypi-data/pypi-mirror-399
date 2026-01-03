"""LLM Instruction executor configuration model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..shared import CommonValidators, OutputMixin, ResponseFormat, TimeoutRetryMixin


class LlmInstructionExecutorConfig(OutputMixin, TimeoutRetryMixin, BaseModel):
    """Configuration for LlmInstructionExecutor."""

    model_config = ConfigDict(extra="allow")

    instruction: str = Field(..., description="LLM instruction text")

    # Provider-based configuration
    provider: str | None = Field(
        "realtimexai", description="LLM provider name (e.g., 'openai', 'anthropic')"
    )
    model: str = Field("gpt-4o-mini", description="LLM model to use")

    # LLM parameters
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Response randomness")
    maxTokens: int | None = Field(None, ge=1, le=32000, description="Maximum response tokens")
    systemPrompt: str | None = Field(None, description="System prompt for LLM")
    timeout: int | None = Field(
        None,
        ge=1,
        description="Request timeout in seconds (None disables the timeout)",
    )
    responseFormat: ResponseFormat = Field(
        ResponseFormat.TEXT, description="Expected response format"
    )
    jsonSchema: dict[str, Any] | None = Field(
        None,
        description="JSON schema definition used for structured outputs",
    )

    # Widget configuration
    widget: dict[str, Any] | None = Field(
        None,
        description="Optional widget configuration for downstream streaming/visualization",
    )

    # Legacy configuration (deprecated)
    apiBase: str | None = Field(
        None, description="Custom API base URL (deprecated - use provider instead)"
    )

    @field_validator("instruction", mode="before")
    @classmethod
    def _validate_instruction(cls, value: str) -> str:
        """Delegate to shared instruction validator."""
        return CommonValidators.validate_instruction(value)

    @field_validator("systemPrompt", mode="before")
    @classmethod
    def _validate_system_prompt(cls, value: str | None) -> str | None:
        """Normalize system prompt using shared validator."""
        return CommonValidators.validate_system_prompt(value)

    @field_validator("resultVariable", mode="before")
    @classmethod
    def _validate_result_variable(cls, value: str | None) -> str | None:
        """Normalize result variable while enforcing identifier semantics."""
        return CommonValidators.validate_result_variable(value)

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str | None) -> str | None:
        """Validate provider name format."""
        if v is not None:
            if not v.strip():
                raise ValueError("Provider name cannot be empty")
            # Normalize provider name to lowercase
            return v.strip().lower()
        return v

    @model_validator(mode="after")
    def validate_configuration_approach(self) -> "LlmInstructionExecutorConfig":
        """Validate that either provider or legacy apiBase is used, but not both."""
        if self.provider and self.apiBase:
            raise ValueError(
                "Cannot specify both 'provider' and 'apiBase'. Use 'provider' for new configurations."
            )

        if self.responseFormat == ResponseFormat.WIDGET:
            normalized = self._normalize_schema_from_widget()
            object.__setattr__(self, "jsonSchema", normalized)
        elif self.responseFormat == ResponseFormat.JSON_SCHEMA:
            if not self.jsonSchema:
                raise ValueError(
                    "jsonSchema is required when responseFormat is set to 'json_schema'"
                )
            object.__setattr__(self, "jsonSchema", self._normalize_schema(self.jsonSchema))
        else:
            object.__setattr__(self, "jsonSchema", None)

        return self

    def _normalize_schema_from_widget(self) -> dict[str, Any]:
        if not isinstance(self.widget, dict):
            raise ValueError("widget configuration is required when responseFormat is 'widget'")

        widget_schema = self.widget.get("jsonSchema")
        if not isinstance(widget_schema, dict) or not widget_schema:
            raise ValueError("widget.jsonSchema is required when responseFormat is 'widget'")

        widget_name = self.widget.get("name") if isinstance(self.widget.get("name"), str) else None
        return self._normalize_schema(widget_schema, default_name=widget_name)

    @staticmethod
    def _normalize_schema(
        schema: dict[str, Any], default_name: str | None = None
    ) -> dict[str, Any]:
        if not isinstance(schema, dict) or not schema:
            raise ValueError("jsonSchema must be a non-empty object")

        schema_name = schema.get("name") if isinstance(schema.get("name"), str) else None
        strict_value = schema.get("strict") if isinstance(schema.get("strict"), bool) else None

        inner_schema = schema.get("schema")
        if isinstance(inner_schema, dict) and inner_schema:
            # Schema provided as {"name": ..., "schema": {...}}.
            core_schema = inner_schema
            extras = {k: v for k, v in schema.items() if k not in {"schema", "name", "strict"}}
        else:
            # Schema provided as a plain JSON schema object.
            core_schema = schema
            extras = {}

        normalized: dict[str, Any] = {"schema": core_schema}
        final_name = schema_name or default_name
        if final_name:
            normalized["name"] = final_name

        normalized.update(extras)
        normalized["strict"] = strict_value if strict_value is not None else False

        return normalized
