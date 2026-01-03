"""Stream UI executor configuration model."""

from enum import Enum
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator


class UIComponentDataType(str, Enum):
    """Supported UI component data types."""

    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    CODE = "code"
    JSON = "json"
    TABLE = "table"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILES = "files"
    CHART = "chart"
    MERMAID = "mermaid"
    MAP = "map"
    SEARCH = "search"
    TOOL_USE = "toolUse"
    OPEN_TAB = "openTab"
    MCP_UI = "mcpUi"
    WIDGET = "widget"


class UIComponentsConfig(BaseModel):
    """Configuration for UI component structure."""

    model_config = ConfigDict(extra="allow")

    dataType: UIComponentDataType = Field(..., description="Type of UI component to render")
    data: dict[str, Any] | str = Field(
        ..., description="Component data payload or JSON schema for LLM mode"
    )


class StreamUIExecutorConfig(BaseModel):
    """Configuration for StreamUIExecutor."""

    model_config = ConfigDict(extra="allow")
    _llm_schema: dict[str, Any] | None = PrivateAttr(default=None)

    useLLM: bool = Field(..., description="Whether to use LLM to generate UI component data")
    inputData: Any | None = Field(
        None,
        description=(
            "Input payload or prompt for LLM (required when useLLM is true). "
            "Supports strings, dicts, and other structured data."
        ),
    )
    uiComponents: UIComponentsConfig = Field(..., description="UI component configuration")

    @model_validator(mode="after")
    def validate_input_data(self) -> "StreamUIExecutorConfig":
        """Validate inputData based on useLLM flag."""
        if self.useLLM:
            if self.inputData is None:
                raise ValueError("inputData is required when useLLM is true")

            if isinstance(self.inputData, str):
                stripped_input = self.inputData.strip()
                if not stripped_input:
                    raise ValueError("inputData cannot be empty string when useLLM is true")
                object.__setattr__(self, "inputData", stripped_input)
        elif isinstance(self.inputData, str):
            # Treat empty/whitespace-only strings as absence of input in static mode.
            stripped_input = self.inputData.strip()
            object.__setattr__(self, "inputData", stripped_input or None)

        return self

    @model_validator(mode="after")
    def validate_llm_mode_schema(self) -> "StreamUIExecutorConfig":
        """Validate that data contains a JSON schema when useLLM is true."""
        if not self.useLLM:
            self._llm_schema = None
            return self

        schema: dict[str, Any] | None = None

        if self.uiComponents.dataType == UIComponentDataType.WIDGET:
            schema = self._extract_widget_schema()
        else:
            if not isinstance(self.uiComponents.data, dict):
                raise ValueError(
                    "uiComponents.data must be a JSON schema object when useLLM is true"
                )
            schema = self.uiComponents.data

        if not schema.get("type") and not schema.get("properties"):
            raise ValueError("uiComponents.data must be a valid JSON schema when useLLM is true")

        self._llm_schema = schema
        return self

    def get_llm_schema(self) -> dict[str, Any]:
        """Return the normalized JSON schema used for LLM generation."""
        if self._llm_schema is None:
            raise ValueError("LLM schema is only available when useLLM is true")
        return self._llm_schema

    def get_widget_content_template(self) -> dict[str, Any] | None:
        """Return the widget content template (content block) if applicable."""
        if self.uiComponents.dataType == UIComponentDataType.WIDGET and isinstance(
            self.uiComponents.data, dict
        ):
            content = self.uiComponents.data.get("content")
            if isinstance(content, dict):
                return content
        return None

    def _extract_widget_schema(self) -> dict[str, Any]:
        """Extract JSON schema for widget data from nested structure."""
        content = self.get_widget_content_template()
        if content is None:
            raise ValueError(
                "uiComponents.data.content must be provided as an object when dataType is 'widget'"
            )

        schema = content.get("data")
        if not isinstance(schema, dict):
            raise ValueError(
                "uiComponents.data.content.data must be a JSON schema object when dataType is 'widget' "
                "and useLLM is true"
            )

        return cast("dict[str, Any]", schema)
