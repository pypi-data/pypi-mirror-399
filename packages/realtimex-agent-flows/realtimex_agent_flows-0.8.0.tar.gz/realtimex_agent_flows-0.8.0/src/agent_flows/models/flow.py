"""Flow-related Pydantic models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FlowStep(BaseModel):
    """Individual flow step configuration."""

    model_config = ConfigDict(extra="allow")

    id: str | None = Field(None, description="Optional step identifier")
    type: str = Field(..., description="Step type identifier")
    config: dict[str, Any] = Field(..., description="Step-specific configuration")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate step type is not empty."""
        if not v or not v.strip():
            raise ValueError("Step type cannot be empty")
        return v.strip()


class FlowConfig(BaseModel):
    """Complete flow configuration."""

    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Flow name")
    description: str = Field(..., description="Flow description")
    uuid: str = Field(..., description="Unique flow identifier")
    active: bool = Field(True, description="Whether flow is active")
    steps: list[FlowStep] = Field(..., description="List of flow steps")
    ui_components: list[dict[str, Any]] | None = Field(
        None,
        alias="ui-components",
        description="UI component configuration for frontend display",
    )
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate flow name is not empty."""
        if not v or not v.strip():
            raise ValueError("Flow name cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate flow description is not empty."""
        if not v or not v.strip():
            raise ValueError("Flow description cannot be empty")
        return v.strip()

    @field_validator("uuid")
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate UUID format."""
        if not v or not v.strip():
            raise ValueError("Flow UUID cannot be empty")
        # Basic UUID format validation
        uuid_str = v.strip()
        if len(uuid_str) != 36 or uuid_str.count("-") != 4:
            raise ValueError("Invalid UUID format")
        return uuid_str

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: list[FlowStep]) -> list[FlowStep]:
        """Validate steps list is not empty."""
        if not v:
            raise ValueError("Flow must have at least one step")
        return v


class FlowSummary(BaseModel):
    """Summary information for a flow."""

    name: str = Field(..., description="Flow name")
    uuid: str = Field(..., description="Unique flow identifier")
    description: str = Field(..., description="Flow description")
    active: bool = Field(True, description="Whether flow is active")
    step_count: int = Field(..., description="Number of steps in flow")
    created_at: datetime | None = Field(None, description="Creation timestamp")

    @field_validator("step_count")
    @classmethod
    def validate_step_count(cls, v: int) -> int:
        """Validate step count is positive."""
        if v < 0:
            raise ValueError("Step count cannot be negative")
        return v
