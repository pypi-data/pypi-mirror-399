"""Type casting utilities for enforcing strict types."""

from datetime import datetime
from typing import Any

import dateutil.parser  # type: ignore

from agent_flows.models.shared import ConditionType, VariableType


def to_datetime(value: Any) -> datetime:
    """Convert a value to a datetime object.

    Args:
        value: Value to convert (string, datetime, or timestamp)

    Returns:
        datetime object

    Raises:
        ValueError: If value cannot be converted to datetime
    """
    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            # Try to parse as ISO format first, then flexible parsing
            return dateutil.parser.parse(value)
        except (ValueError, TypeError) as e:
            raise ValueError(f"String '{value}' cannot be converted to datetime") from e

    if isinstance(value, int | float):
        try:
            # Assume it's a Unix timestamp
            return datetime.fromtimestamp(value)
        except (ValueError, OSError) as e:
            raise ValueError(f"Number '{value}' cannot be converted to datetime") from e

    raise ValueError(f"Value of type {type(value)} cannot be converted to datetime")


def to_number(value: Any) -> float:
    """Convert a value to a number (int or float).

    Args:
        value: Value to convert

    Returns:
        Numeric value

    Raises:
        ValueError: If value cannot be converted to a number
    """
    if isinstance(value, int | float):
        return float(value)

    if isinstance(value, str):
        # Try to convert string to number
        value = value.strip()

        # Handle empty strings
        if not value:
            raise ValueError("Empty string cannot be converted to number")

        # Try integer first, then float
        try:
            if "." in value or "e" in value.lower():
                return float(value)
            else:
                return float(int(value))
        except ValueError as e:
            raise ValueError(f"String '{value}' cannot be converted to number") from e

    # Try to convert other types
    try:
        return float(value)
    except (ValueError, TypeError) as e:
        raise ValueError(f"Value of type {type(value)} cannot be converted to number") from e


def cast_value(  # noqa: PLR0911
    value: Any,
    target_type: str | ConditionType | VariableType,
    strict: bool = True,
) -> Any:
    """Validate and cast value to the target type.

    Args:
        value: Value to validate/cast
        target_type: Target type (Enum or string value)
        strict: If True, enforces strict type checking (no implicit conversion).
                If False, allows safe conversions (e.g., string "123" -> number 123).

    Returns:
        Value if valid (or casted)

    Raises:
        ValueError: If value does not match target type
    """
    if value is None:
        return None

    # Get string value if it's an Enum
    type_str = target_type.value if hasattr(target_type, "value") else target_type

    # Handle AUTO type
    if type_str == "auto":
        return value

    # Handle STRING type
    if type_str == "string":
        if not isinstance(value, str):
            raise ValueError(f"Value '{value}' is of type {type(value).__name__}, expected string")
        return value

    # Handle NUMBER type
    elif type_str == "number":
        if strict:
            # STRICT: Only allow int/float (excluding bool)
            if not isinstance(value, int | float) or isinstance(value, bool):
                raise ValueError(
                    f"Value '{value}' is of type {type(value).__name__}, expected number"
                )
            return value
        else:
            # RELAXED: Allow string-to-number parsing
            try:
                return to_number(value)
            except ValueError as e:
                raise ValueError(f"Value '{value}' cannot be cast to number: {str(e)}") from e

    # Handle BOOLEAN type
    elif type_str == "boolean":
        if not isinstance(value, bool):
            raise ValueError(f"Value '{value}' is of type {type(value).__name__}, expected boolean")
        return value

    # Handle DATETIME type
    elif type_str == "datetime":
        return to_datetime(value)

    # Handle ARRAY type
    elif type_str == "array":
        if not isinstance(value, list | tuple | set):
            raise ValueError(f"Value is of type {type(value).__name__}, expected array")
        return list(value)

    # Handle OBJECT type
    elif type_str == "object":
        if not isinstance(value, dict):
            raise ValueError(f"Value is of type {type(value).__name__}, expected object")
        return value

    return value
