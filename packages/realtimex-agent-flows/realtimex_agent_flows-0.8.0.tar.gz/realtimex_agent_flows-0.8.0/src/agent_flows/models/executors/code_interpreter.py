"""Configuration model for the Code Interpreter executor."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..shared import OutputMixin


class CodeInterpreterLanguage(str, Enum):
    """Supported runtime languages for the Code Interpreter executor."""

    PYTHON = "python"


class CodeInterpreterRuntime(BaseModel):
    """Runtime configuration describing how the interpreter should execute the script."""

    model_config = ConfigDict(extra="forbid")

    language: CodeInterpreterLanguage = Field(
        default=CodeInterpreterLanguage.PYTHON,
        description="Target runtime language.",
    )
    version: str | None = Field(
        default=None,
        description="Optional language version hint for the interpreter service.",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Package requirements to install before running the script.",
    )

    @field_validator("version")
    @classmethod
    def normalize_version(cls, value: str | None) -> str | None:
        """Normalize the version string, returning None when empty."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @field_validator("dependencies", mode="before")
    @classmethod
    def validate_dependencies(cls, value: list[str] | None) -> list[str]:
        """Validate and normalize package dependency declarations."""
        if value is None:
            return []

        if not isinstance(value, list):
            raise TypeError("dependencies must be provided as a list of strings")

        cleaned: list[str] = []
        for entry in value:
            if not isinstance(entry, str):
                raise TypeError("dependency entries must be strings")

            normalized = entry.strip()
            if not normalized:
                raise ValueError("dependency entries cannot be empty strings")

            cleaned.append(normalized)

        return cleaned


class InlineScriptDefinition(BaseModel):
    """Definition of the script when provided inline within the flow configuration."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["inline"] = Field(
        default="inline",
        description="Denotes that the script is embedded directly in the configuration.",
    )
    code: str = Field(..., description="Python source code to execute.")

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        """Ensure the inline script is not empty."""
        if not value or not value.strip():
            raise ValueError("script code cannot be empty")
        return value


class CodeInterpreterExecutorConfig(OutputMixin, BaseModel):
    """Top-level configuration for the Code Interpreter executor."""

    model_config = ConfigDict(extra="allow")

    runtime: CodeInterpreterRuntime = Field(
        default_factory=CodeInterpreterRuntime,
        description="Runtime configuration describing the interpreter environment.",
    )
    script: InlineScriptDefinition = Field(
        ...,
        description="Script definition that will be executed by the interpreter service.",
    )
    timeout: int = Field(
        default=0,
        ge=0,
        le=300,
        description="Request timeout in seconds (0 disables the timeout).",
    )
    maxRetries: int = Field(
        default=0,
        ge=0,
        le=10,
        description="Maximum retry attempts (0 disables retries).",
    )
