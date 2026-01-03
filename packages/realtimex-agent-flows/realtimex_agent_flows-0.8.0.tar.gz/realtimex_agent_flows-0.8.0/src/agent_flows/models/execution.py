"""Execution-related Pydantic models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_serializer

from agent_flows.models.credentials import CredentialBundle


class FlowResultType(str, Enum):
    """Enumeration of possible flow result types."""

    COMPLETED = "COMPLETED"
    DIRECT_OUTPUT = "DIRECT_OUTPUT"
    ERROR = "ERROR"
    HALTED_BY_TARGET = "HALTED_BY_TARGET"


class ExecutionError(BaseModel):
    """Error that occurred during execution."""

    message: str = Field(..., description="Error message")
    step_id: str | None = Field(None, description="Step ID where error occurred")
    step_index: int | None = Field(None, description="Step where error occurred")
    step_type: str | None = Field(None, description="Type of step that failed")
    error_type: str | None = Field(None, description="Type of the original exception")
    context_variables: dict[str, Any] | None = Field(
        None, description="Sanitized context variables at time of error"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    def get_step_identifier(self) -> str:
        """Get a human-readable step identifier for error reporting.

        Returns:
            String identifying the step where the error occurred
        """
        if self.step_id:
            return f"Step '{self.step_id}'"
        elif self.step_index is not None:
            return f"Step {self.step_index}"
        else:
            return "Unknown step"


class ExecutorResult(BaseModel):
    """Result from a single executor."""

    success: bool = Field(..., description="Whether execution was successful")
    data: Any = Field(None, description="Result data from execution")
    variables_updated: dict[str, Any] = Field(
        default_factory=dict, description="Variables updated by this step"
    )
    direct_output: bool = Field(False, description="Whether this is direct output")
    error: str | None = Field(None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("execution_time")
    @classmethod
    def validate_execution_time(cls, v: float) -> float:
        """Validate execution time is non-negative."""
        if v < 0:
            raise ValueError("Execution time cannot be negative")
        return v


class ExecutionContext(BaseModel):
    """Context passed to executors."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    variables: dict[str, Any] = Field(..., description="Current flow variables")
    flow_id: str = Field(..., description="Flow identifier")
    step_index: int = Field(..., description="Current step index")
    step_id: str | None = Field(None, description="Optional step identifier")
    step_type: str | None = Field(None, description="Current step type")
    config: Any | None = Field(None, description="Agent Flows configuration instance")
    step_execution_service: Any | None = Field(None, description="Step execution service instance")
    resolved_credentials: dict[str, CredentialBundle] = Field(
        default_factory=dict,
        description="Decrypted credential bundles active for the current step",
    )
    test_manifest: Any | None = Field(None, description="Test manifest for pinned results")
    trace_log: list["TraceEntry"] | None = Field(
        None, description="Shared list for accumulating trace entries during execution"
    )
    mcp_session_pool: Any | None = Field(
        None, description="MCP session pool for persistent connections"
    )
    session_id: str | None = Field(None, description="Current session id")
    workspace_slug: str | None = Field(None, description="Current workspace slug")
    thread_id: str | None = Field(None, description="Current thread id")
    agent_id: str | None = Field(None, description="Current agent id")

    @field_validator("step_index")
    @classmethod
    def validate_step_index(cls, v: int) -> int:
        """Validate step index is non-negative."""
        if v < 0:
            raise ValueError("Step index cannot be negative")
        return v

    def get_credential(self, alias: str) -> CredentialBundle | None:
        """Retrieve a resolved credential by alias."""
        return self.resolved_credentials.get(alias)


class FlowResultData(BaseModel):
    """The primary outcome data of a flow execution."""

    type: FlowResultType = Field(..., description="Type of flow result")
    target_step_id: str | None = Field(
        None, description="ID of target step (only present when type is HALTED_BY_TARGET)"
    )
    target_step_type: str | None = Field(
        None, description="Type of target step (only present when type is HALTED_BY_TARGET)"
    )
    data: Any = Field(None, description="Result payload data")

    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        """Customize serialization to exclude target fields when None."""
        data = handler(self)

        # Exclude target fields if None
        if data.get("target_step_id") is None:
            data.pop("target_step_id", None)
        if data.get("target_step_type") is None:
            data.pop("target_step_type", None)

        return data


class TargetStepResult(BaseModel):
    """Detailed result from a target step in test execution."""

    step_id: str = Field(..., description="ID of the target step")
    step_type: str = Field(..., description="Type of the target step")
    success: bool = Field(..., description="Whether the step executed successfully")
    execution_time: float = Field(..., description="Step execution time in seconds")
    data: Any = Field(None, description="Data returned by the step")
    variables_updated: dict[str, Any] = Field(
        default_factory=dict, description="Variables updated by the step"
    )


class TraceEntry(BaseModel):
    """Entry in the execution trace showing step-by-step execution history."""

    step_id: str = Field(..., description="ID of the executed step")
    step_type: str = Field(..., description="Type of the executed step")
    success: bool = Field(..., description="Whether the step executed successfully")
    execution_time: float = Field(..., description="Step execution time in seconds")
    data: Any | None = Field(None, description="Data returned by the step")
    variables_updated: dict[str, Any] | None = Field(
        None, description="Variables updated by the step"
    )


class FlowResult(BaseModel):
    """Result of flow execution (production or test mode)."""

    flow_id: str = Field(..., description="Flow identifier")
    success: bool = Field(..., description="Whether execution was successful")
    execution_time: float = Field(..., description="Total execution time in seconds")
    result: FlowResultData = Field(..., description="Primary outcome of the flow")
    errors: list[ExecutionError] = Field(
        default_factory=list,
        description="Errors that occurred during execution (internal use)",
    )
    trace: list[TraceEntry] | None = Field(
        None, description="Step-by-step execution trace (optional)"
    )
    flow_as_output: bool = Field(
        False, description="Whether to use flow result as the output (from Finish executor)"
    )

    @model_serializer(mode="wrap")
    def _serialize(self, handler):
        """Customize serialization to exclude redundant fields."""
        data = handler(self)

        # Exclude trace if None
        if data.get("trace") is None:
            data.pop("trace", None)

        # Always exclude errors array from serialization
        data.pop("errors", None)

        return data

    @field_validator("execution_time")
    @classmethod
    def validate_execution_time(cls, v: float) -> float:
        """Validate execution time is non-negative."""
        if v < 0:
            raise ValueError("Execution time cannot be negative")
        return v
