"""Validation utilities for flow configuration."""

from typing import Any

from pydantic import ValidationError


def format_validation_errors(error: ValidationError, step_type: str) -> list[str]:
    """Format Pydantic validation errors into readable messages.

    Args:
        error: The Pydantic ValidationError to format
        step_type: The type of step being validated

    Returns:
        List of formatted error messages
    """
    messages = []

    for error_detail in error.errors():
        location = error_detail.get("loc", ())
        message = error_detail.get("msg", "Unknown validation error")
        error_type = error_detail.get("type", "unknown")

        # Clean up common Pydantic message prefixes
        if message.startswith("Value error, "):
            message = message[13:]  # Remove "Value error, " prefix

        # Build a readable field path
        if location:
            field_path = ".".join(str(loc) for loc in location)
            if error_type == "missing":
                field_name = location[-1]
                formatted_msg = f"Missing required field '{field_name}' for step type '{step_type}'"
            else:
                formatted_msg = f"Field '{field_path}': {message}"
        else:
            formatted_msg = f"Configuration error for step type '{step_type}': {message}"

        messages.append(formatted_msg)

    return messages


class StepValidationResult:
    """Result of validating a single step."""

    def __init__(self, step_id: str, step_type: str):
        self.step_id = step_id
        self.step_type = step_type
        self.valid = True
        self.messages: list[str] = []

    def add_error(self, message: str) -> None:
        """Add an error message and mark as invalid."""
        self.valid = False
        self.messages.append(message)

    def add_errors(self, messages: list[str]) -> None:
        """Add multiple error messages and mark as invalid."""
        if messages:
            self.valid = False
            self.messages.extend(messages)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "valid": self.valid,
            "messages": self.messages,
        }
