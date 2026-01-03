"""Flow Variables executor configuration model."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..shared import VariableDefinition


class FlowVariablesExecutorConfig(BaseModel):
    """Configuration for FlowVariablesExecutor."""

    model_config = ConfigDict(extra="allow")

    variables: list[VariableDefinition] = Field(
        default_factory=list, description="List of variables to initialize"
    )

    @field_validator("variables")
    @classmethod
    def validate_no_duplicates(cls, v: list[VariableDefinition]) -> list[VariableDefinition]:
        """Validate no duplicate variable names."""
        seen: set[str] = set()
        dups: list[str] = []
        for var in v:
            name = var.name
            if name in seen and name not in dups:
                dups.append(name)
            seen.add(name)
        if dups:
            raise ValueError(f"Duplicate variable names found: {dups}")
        return v
