"""Finish executor configuration model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..shared import CommonValidators
from .stream_ui import UIComponentsConfig


class FinishExecutorConfig(BaseModel):
    """Configuration for FinishExecutor."""

    model_config = ConfigDict(extra="allow")

    message: str = Field(
        "Flow execution finished", description="Optional message to include with flow termination"
    )
    data: Any = Field(None, description="Optional custom data to include with termination")
    resultVariable: str | None = Field(
        None,
        description=(
            "Variable to store finish information (deprecated; will be removed in a future release)"
        ),
    )

    # UI streaming fields
    flowAsOutput: bool = Field(False, description="Whether to use flow result as the output")
    useLLM: bool | None = Field(
        None, description="Whether to use LLM to generate UI component data"
    )
    inputData: str | dict[str, Any] | list[Any] | None = Field(
        None, description="Input data for LLM or static mode (required when useLLM is true)"
    )
    uiComponents: UIComponentsConfig | None = Field(
        None, description="UI component configuration for finish step"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str | None) -> str | None:
        """Ensure message is non-empty when provided."""
        if v is None:
            return v
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Message cannot be empty string")
        return v

    @field_validator("resultVariable")
    @classmethod
    def validate_result_variable(cls, v: str | None) -> str | None:
        """Validate result variable (deprecated, kept for backward compatibility)."""
        return CommonValidators.validate_result_variable.__func__(CommonValidators, v)

    @model_validator(mode="after")
    def validate_ui_components(self) -> "FinishExecutorConfig":
        """Validate UI component requirements based on useLLM."""
        if self.useLLM is True:
            if self.uiComponents is None:
                raise ValueError("uiComponents is required when useLLM is true")

            if self.inputData is None:
                raise ValueError("inputData is required when useLLM is true")

            if isinstance(self.inputData, str) and not self.inputData.strip():
                raise ValueError("inputData cannot be empty string when useLLM is true")
        elif isinstance(self.inputData, str):
            # Normalize empty strings to None when not using LLM.
            stripped = self.inputData.strip()
            object.__setattr__(self, "inputData", stripped or None)

        return self
