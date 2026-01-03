"""Dictionary-related utility functions."""

import collections.abc
from typing import Any


def deep_update(d: dict, u: dict) -> dict:
    """
    Recursively update a dictionary.
    The d dictionary is updated in-place, but the function returns it for convenience.
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            # Ensure we have a dict to merge into (handle None values)
            existing_value = d.get(k)
            if not isinstance(existing_value, dict):
                existing_value = {}
            d[k] = deep_update(existing_value, v)
        else:
            d[k] = v
    return d


def set_nested_value(target: dict[str, Any], dotted_key: str, value: Any) -> None:
    """Set a value in a nested dictionary using dotted key notation.

    Args:
        target: Dictionary to modify
        dotted_key: Key in dotted notation (e.g., 'user.email' or 'simple_key')
        value: Value to set

    Raises:
        ValueError: If a parent path exists as a non-mapping value

    Example:
        data = {}
        set_nested_value(data, 'user.email', 'test@example.com')
        # Result: {'user': {'email': 'test@example.com'}}
    """
    if "." not in dotted_key:
        target[dotted_key] = value
        return

    keys = dotted_key.split(".")
    current = target

    # Navigate/create nested structure
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            # Parent path exists as non-mapping value - this is a conflict
            parent_path = ".".join(keys[: i + 1])
            raise ValueError(
                f"Cannot set nested value '{dotted_key}': parent path '{parent_path}' "
                f"already exists as {type(current[key]).__name__} with value {current[key]!r}. "
                f"Nested paths require parent to be a mapping (dict)."
            )
        current = current[key]

    # Set the final value
    current[keys[-1]] = value
