"""Loop executor configuration model."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..flow import FlowStep
from ..shared import CommonValidators, ConditionDefinition, LoopType, OutputMixin


class LoopExecutorConfig(OutputMixin, BaseModel):
    """Configuration for LoopExecutor."""

    model_config = ConfigDict(extra="allow")

    loopType: LoopType = Field(..., description="Type of loop to execute")
    loopBlocks: list[FlowStep] = Field(
        default_factory=list, description="Steps to execute in each iteration"
    )
    maxIterations: int = Field(100, ge=1, le=10_000, description="Maximum number of iterations")

    # For loop specific fields
    startValue: int | str | None = Field(None, description="Starting value for 'for' loop")
    endValue: int | str | None = Field(None, description="Ending value for 'for' loop")
    stepValue: int | str = Field(1, description="Step value for 'for' loop")
    counterVariable: str | None = Field(None, description="Variable name for loop counter")

    # While loop specific fields
    condition: ConditionDefinition | None = Field(
        None, description="Condition definition for 'while' loop"
    )

    # ForEach loop specific fields
    iterableVariable: str | list | None = Field(
        None, description="Variable containing iterable for 'forEach' loop"
    )
    itemVariable: str | None = Field(
        None, description="Variable name for current item in 'forEach' loop"
    )
    indexVariable: str | None = Field(
        None, description="Variable name for current index in 'forEach' loop"
    )

    # Apply common validators
    _validate_counter_variable = CommonValidators.validate_counter_variable
    _validate_item_variable = CommonValidators.validate_item_variable
    _validate_index_variable = CommonValidators.validate_index_variable
    _validate_iterable_variable = CommonValidators.validate_variable_path

    @field_validator("stepValue")
    @classmethod
    def _validate_step_non_zero(cls, v: int | str) -> int | str:
        # Only enforce when user passed a concrete integer
        if isinstance(v, int) and v == 0:
            raise ValueError("stepValue must not be 0")
        return v

    @model_validator(mode="after")
    def validate_loop_type_requirements(self) -> LoopExecutorConfig:
        """Validate that required fields are present for each loop type."""
        if self.loopType == LoopType.FOR:
            if self.startValue is None:
                raise ValueError("For loop requires 'startValue'")
            if self.endValue is None:
                raise ValueError("For loop requires 'endValue'")
            if self.counterVariable is None:
                raise ValueError("For loop requires 'counterVariable'")

        elif self.loopType == LoopType.WHILE:
            if self.condition is None:
                raise ValueError("While loop requires 'condition'")

        elif self.loopType == LoopType.FOR_EACH:
            if self.iterableVariable is None:
                raise ValueError("ForEach loop requires 'iterableVariable'")
            if self.itemVariable is None:
                raise ValueError("ForEach loop requires 'itemVariable'")

        return self
