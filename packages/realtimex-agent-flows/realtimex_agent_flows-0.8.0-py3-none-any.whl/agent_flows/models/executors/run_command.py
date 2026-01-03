"""Configuration model for the Run Command executor."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..shared import OutputMixin, TimeoutRetryMixin


class RunCommandExecutorConfig(OutputMixin, TimeoutRetryMixin, BaseModel):
    """Configuration for the Run Command executor.

    This executor runs CLI commands via subprocess without a shell (safer,
    more predictable). For commands requiring shell features (pipes, redirects,
    globs), use: command="sh", args=["-c", "your | shell | command"]
    """

    model_config = ConfigDict(extra="allow")

    command: str = Field(
        ...,
        description="The executable or command to run.",
    )
    args: list[str] = Field(
        default_factory=list,
        description="Arguments to pass to the command.",
    )
    cwd: str | None = Field(
        None,
        description="Working directory for execution. Uses system default if not specified.",
    )
    env: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables to add (merged with existing environment).",
    )

    @field_validator("command", mode="before")
    @classmethod
    def validate_command(cls, value: Any) -> str:
        """Validate that command is a non-empty string."""
        if not isinstance(value, str):
            raise TypeError("command must be a string")
        normalized = value.strip()
        if not normalized:
            raise ValueError("command cannot be empty")
        return normalized

    @field_validator("args", mode="before")
    @classmethod
    def validate_args(cls, value: list[str] | None) -> list[str]:
        """Validate and normalize command arguments."""
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("args must be a list of strings")
        cleaned: list[str] = []
        for i, arg in enumerate(value):
            if not isinstance(arg, str):
                raise TypeError(f"args[{i}] must be a string")
            cleaned.append(arg)
        return cleaned

    @field_validator("cwd", mode="before")
    @classmethod
    def validate_cwd(cls, value: str | None) -> str | None:
        """Validate working directory path."""
        if value is None:
            return None
        if not isinstance(value, str):
            raise TypeError("cwd must be a string")
        normalized = value.strip()
        return normalized if normalized else None

    @field_validator("env", mode="before")
    @classmethod
    def validate_env(cls, value: dict[str, str] | None) -> dict[str, str]:
        """Validate environment variables dictionary."""
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError("env must be a dictionary")
        validated: dict[str, str] = {}
        for key, val in value.items():
            if not isinstance(key, str):
                raise TypeError(f"env key {key!r} must be a string")
            if not isinstance(val, str):
                raise TypeError(f"env value for '{key}' must be a string")
            validated[key] = val
        return validated
