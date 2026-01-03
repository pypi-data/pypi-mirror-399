"""Reusable field validators for executor configurations."""

import json

from pydantic import field_validator

from .enums import BodyType


class CommonValidators:
    """Collection of reusable field validators for executor configurations."""

    @staticmethod
    def contains_template(value: str) -> bool:
        """Check if a string contains a template expression for interpolation."""
        return isinstance(value, str) and "{{" in value and "}}" in value

    @field_validator("resultVariable")
    @classmethod
    def validate_result_variable(cls, v: str | None) -> str | None:
        """Validate result variable name if provided."""
        if v is None:
            return v

        if not isinstance(v, str) or not v.strip():
            return None  # Convertt empty or non-string to None for frontend compatibility

        var_name = v.strip()
        if not var_name.isidentifier():
            raise ValueError(
                f"Invalid result variable name '{var_name}': must be a valid identifier"
            )

        return var_name

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format."""
        if not v.strip():
            raise ValueError("URL cannot be empty")

        url = v.strip()
        if cls.contains_template(url):
            return url

        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        return url

    @field_validator("name")
    @classmethod
    def validate_variable_name(cls, v: str) -> str:
        """Validate variable name is a valid identifier."""
        if not v:
            raise ValueError("Variable name cannot be empty")

        # Check if it's a valid Python identifier
        if not v.isidentifier():
            raise ValueError(f"Invalid variable name '{v}': must be a valid identifier")

        return v

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, v: str) -> str:
        """Validate instruction is not empty."""
        if not v.strip():
            raise ValueError("Instruction cannot be empty")
        return v.strip()

    @field_validator("variable")
    @classmethod
    def validate_variable_path(cls, v: str) -> str:
        """Validate variable path is not empty."""
        if not v.strip():
            raise ValueError("Variable path cannot be empty")
        return v.strip()

    @field_validator("type")
    @classmethod
    def validate_step_type(cls, v: str) -> str:
        """Validate step type is not empty."""
        if not v.strip():
            raise ValueError("Step type cannot be empty")
        return v.strip()

    @field_validator("serverId")
    @classmethod
    def validate_server_id(cls, v: str) -> str:
        """Validate server ID is not empty."""
        if not v.strip():
            raise ValueError("Server ID cannot be empty")
        return v.strip()

    @field_validator("action")
    @classmethod
    def validate_action_name(cls, v: str) -> str:
        """Validate action/tool name is not empty."""
        if not v.strip():
            raise ValueError("Action/tool name cannot be empty")
        return v.strip()

    @field_validator("counterVariable")
    @classmethod
    def validate_counter_variable(cls, v: str | None) -> str | None:
        """Validate counter variable name if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Counter variable name cannot be empty")

        var_name = v.strip()
        if not var_name.isidentifier():
            raise ValueError(
                f"Invalid counter variable name '{var_name}': must be a valid identifier"
            )

        return var_name

    @field_validator("itemVariable")
    @classmethod
    def validate_item_variable(cls, v: str | None) -> str | None:
        """Validate item variable name if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Item variable name cannot be empty")

        var_name = v.strip()
        if not var_name.isidentifier():
            raise ValueError(f"Invalid item variable name '{var_name}': must be a valid identifier")

        return var_name

    @field_validator("indexVariable")
    @classmethod
    def validate_index_variable(cls, v: str | None) -> str | None:
        """Validate index variable name if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Index variable name cannot be empty")

        var_name = v.strip()
        if not var_name.isidentifier():
            raise ValueError(
                f"Invalid index variable name '{var_name}': must be a valid identifier"
            )

        return var_name

    @field_validator("systemPrompt")
    @classmethod
    def validate_system_prompt(cls, v: str | None) -> str | None:
        """Validate system prompt if provided."""
        if v is None:
            return v
        return v.strip() if v.strip() else None


class HeaderKeyValidators:
    """Validators specific to HTTP header fields."""

    @field_validator("key")
    @classmethod
    def validate_header_key(cls, v: str) -> str:
        """Validate header key is not empty."""
        if not v.strip():
            raise ValueError("Header key cannot be empty")
        return v.strip()


class FormKeyValidators:
    """Validators specific to form data fields."""

    @field_validator("key")
    @classmethod
    def validate_form_key(cls, v: str) -> str:
        """Validate form field key is not empty."""
        if not v.strip():
            raise ValueError("Form field key cannot be empty")
        return v.strip()


def validate_json_body(body: str | dict | None, body_type: BodyType | None) -> str | dict | None:
    """Validate body content matches JSON body type."""
    if body is None or body_type != BodyType.JSON:
        return body

    # Handle empty string as None
    if isinstance(body, str) and not body.strip():
        return None

    # If it's already a dict, it's valid JSON structure
    if isinstance(body, dict):
        return body

    # If it's a string, validate JSON format
    if isinstance(body, str):
        try:
            json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Body must be valid JSON when bodyType is 'json': {str(e)}") from e

    return body


__all__ = [
    "CommonValidators",
    "HeaderKeyValidators",
    "FormKeyValidators",
    "validate_json_body",
]
