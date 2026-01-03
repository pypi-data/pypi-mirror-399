"""API Call executor configuration model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from ..shared import (
    BodyType,
    CommonValidators,
    FormDataDefinition,
    HeaderDefinition,
    HttpMethod,
    OutputMixin,
    TimeoutRetryMixin,
    validate_json_body,
)


class ApiCallExecutorConfig(OutputMixin, TimeoutRetryMixin, BaseModel):
    """Configuration for ApiCallExecutor."""

    model_config = ConfigDict(extra="allow")

    url: str = Field(..., description="Request URL")
    method: HttpMethod = Field(HttpMethod.GET, description="HTTP method")
    headers: list[HeaderDefinition] = Field(default_factory=list, description="Request headers")
    bodyType: BodyType | None = Field(None, description="Request body type")
    body: Any = Field(None, description="Request body content")
    formData: list[FormDataDefinition] = Field(default_factory=list, description="Form data fields")
    followRedirects: bool = Field(True, description="Follow HTTP redirects")

    # Apply common validators
    @field_validator("url", mode="before")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        """Validate URL field."""
        return CommonValidators.validate_url.__func__(CommonValidators, value)

    @field_validator("body")
    @classmethod
    def validate_body_with_type(cls, v: Any, info: ValidationInfo) -> Any:
        """Validate body content matches body type."""
        body_type: BodyType | None = info.data.get("bodyType")
        return validate_json_body(v, body_type)
