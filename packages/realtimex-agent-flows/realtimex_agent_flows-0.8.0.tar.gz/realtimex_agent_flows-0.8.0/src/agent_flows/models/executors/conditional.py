"""Conditional executor configuration model."""

from pydantic import BaseModel, ConfigDict, Field

from ..flow import FlowStep
from ..shared import ConditionDefinition, OutputMixin


class ConditionalExecutorConfig(OutputMixin, BaseModel):
    """Configuration for ConditionalExecutor."""

    model_config = ConfigDict(extra="allow")

    condition: ConditionDefinition = Field(..., description="Condition to evaluate")
    truePath: list[FlowStep] = Field(
        default_factory=list, description="Steps to execute if condition is true"
    )
    falsePath: list[FlowStep] = Field(
        default_factory=list, description="Steps to execute if condition is false"
    )
