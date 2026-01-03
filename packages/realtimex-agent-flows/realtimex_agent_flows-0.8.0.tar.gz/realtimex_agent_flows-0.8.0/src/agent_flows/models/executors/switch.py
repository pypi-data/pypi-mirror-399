"""Switch executor configuration model."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..flow import FlowStep
from ..shared import OutputMixin, SwitchCase


def _normalize_case_value(v: Any) -> str:
    # Stable string for equality checks across primitives and simple structures
    try:
        return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)
    except Exception:
        return str(v)


class SwitchExecutorConfig(OutputMixin, BaseModel):
    """Configuration for SwitchExecutor."""

    model_config = ConfigDict(extra="allow")

    variable: Any = Field(..., description="Value to switch on")
    cases: list[SwitchCase] = Field(default_factory=list, description="List of switch cases")
    defaultBlocks: list[FlowStep] = Field(
        default_factory=list, description="Default blocks to execute if no case matches"
    )

    @field_validator("cases")
    @classmethod
    def validate_cases_unique(cls, v: list[SwitchCase]) -> list[SwitchCase]:
        """Validate that case values are unique (when provided)."""
        if not v:
            return v
        normalized = [_normalize_case_value(case.value) for case in v]
        if len(normalized) != len(set(normalized)):
            raise ValueError("Switch cases must have unique values")
        return v
