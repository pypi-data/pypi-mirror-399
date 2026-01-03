"""Reusable mixins for executor configurations."""

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from .validators import CommonValidators


class OutputMixin(BaseModel):
    """Mixin for executors that can store results in variables or return directly."""

    resultVariable: str | None = Field(None, description="Variable to store result")
    directOutput: bool = Field(False, description="Return result directly")

    @model_validator(mode="before")
    @classmethod
    def _normalise_response_variable(cls, data: Any) -> Any:
        """Normalize responseVariable into resultVariable for compatibility."""
        if isinstance(data, dict) and "responseVariable" in data and "resultVariable" not in data:
            response_value = data.pop("responseVariable")
            try:
                data["resultVariable"] = CommonValidators.validate_result_variable.__func__(
                    CommonValidators, response_value
                )
            except ValueError as exc:
                original_message = str(exc)
                if "result variable" in original_message.lower():
                    message = original_message.replace("Result", "Response").replace(
                        "result", "response"
                    )
                else:
                    message = original_message
                raise ValueError(message) from exc
        return data

    @field_validator("resultVariable", mode="before")
    @classmethod
    def _validate_result_variable(cls, value: str | None) -> str | None:
        """Validate the result variable field."""
        return CommonValidators.validate_result_variable.__func__(CommonValidators, value)

    @property
    def responseVariable(self) -> str | None:
        """Expose responseVariable alias for compatibility."""
        return self.resultVariable

    @responseVariable.setter
    def responseVariable(self, value: str | None) -> None:
        """Allow setting responseVariable alias post-initialisation."""
        try:
            validated = CommonValidators.validate_result_variable.__func__(CommonValidators, value)
        except ValueError as exc:
            original_message = str(exc)
            if "result variable" in original_message.lower():
                message = original_message.replace("Result", "Response").replace(
                    "result", "response"
                )
            else:
                message = original_message
            raise ValueError(message) from exc
        self.resultVariable = validated


class TimeoutMixin(BaseModel):
    """Mixin for executors that support timeout configuration."""

    timeout: int = Field(30, ge=1, le=300, description="Request timeout in seconds")


class RetryMixin(BaseModel):
    """Mixin for executors that support retry logic."""

    maxRetries: int = Field(0, ge=0, le=10, description="Maximum retry attempts")


class TimeoutRetryMixin(TimeoutMixin, RetryMixin):
    """Combined mixin for executors that support both timeout and retry."""

    pass


__all__ = [
    "OutputMixin",
    "TimeoutMixin",
    "RetryMixin",
    "TimeoutRetryMixin",
]
