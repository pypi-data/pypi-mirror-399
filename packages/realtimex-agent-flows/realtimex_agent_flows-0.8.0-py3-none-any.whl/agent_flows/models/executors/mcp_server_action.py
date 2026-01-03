"""MCP Server Action executor configuration model."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..shared import CommonValidators, MCPProvider, OutputMixin, TimeoutRetryMixin


class McpServerActionExecutorConfig(OutputMixin, TimeoutRetryMixin, BaseModel):
    """Configuration for McpServerActionExecutor."""

    model_config = ConfigDict(extra="allow")

    provider: MCPProvider = Field(..., description="MCP provider type")
    serverId: str = Field(..., description="MCP server identifier")
    action: str = Field(..., description="MCP action/tool name to execute")
    params: dict[str, Any] = Field(
        default_factory=dict, description="Parameters for the MCP action"
    )

    # Apply common validators
    _validate_server_id = CommonValidators.validate_server_id
    _validate_action = CommonValidators.validate_action_name

    @field_validator("params")
    @classmethod
    def _validate_params_keys(cls, v: dict[str, Any]) -> dict[str, Any]:
        # Ensure JSON-safe, non-empty string keys
        for k in v:
            if not isinstance(k, str) or not k.strip():
                raise ValueError("params keys must be non-empty strings")
        return v
