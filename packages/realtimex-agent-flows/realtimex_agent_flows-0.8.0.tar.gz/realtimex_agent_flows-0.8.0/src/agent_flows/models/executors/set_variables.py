"""Configuration models for the SetVariables executor."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agent_flows.models.shared import VariableType
from agent_flows.models.shared.validators import CommonValidators


class VariableAssignment(BaseModel):
    """Definition of a variable assignment."""

    model_config = ConfigDict(use_enum_values=True)

    name: str = Field(..., description="Variable name (supports dot notation for nested fields)")
    value: Any = Field(..., description="Value to assign to the variable")
    type: VariableType = Field(
        default=VariableType.AUTO, description="Target type to cast/validate the value against"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate variable name/path is not empty."""
        return CommonValidators.validate_variable_path(v)


class SetVariablesExecutorConfig(BaseModel):
    """Configuration for the SetVariables executor."""

    variables: list[VariableAssignment] = Field(
        ..., description="List of variables to set or update"
    )
