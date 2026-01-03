"""Agent Flows Python Package.

A standalone Python library for executing Agent Flows - visual, no-code
workflows that can be integrated into Python-based AI agents and applications.
"""

from .api.http_client import ApiClient
from .core.execution import ExecutorRegistry, FlowExecutor
from .core.flows.cache import FlowCache
from .exceptions import (
    AgentFlowsError,
    ApiError,
    ConfigurationError,
    ExecutorError,
    ExecutorNotFoundError,
    FlowError,
    FlowExecutionError,
    FlowNotFoundError,
    IntegrationError,
    MCPError,
)
from .models.config import AgentFlowsConfig, LiteLLMConfig, MCPConfig
from .models.execution import ExecutionContext, ExecutorResult, FlowResult
from .models.flow import FlowConfig, FlowStep, FlowSummary
from .models.test import PinnedResult, TestManifest
from .utils.config import load_config

__version__ = "0.1.0"
__author__ = "RealTimeX Team"
__email__ = "team@realtimex.ai"

__all__ = [
    # Core classes
    "FlowExecutor",
    "ExecutorRegistry",
    "ApiClient",
    "FlowCache",
    # Configuration
    "AgentFlowsConfig",
    "LiteLLMConfig",
    "MCPConfig",
    "load_config",
    # Data models
    "FlowConfig",
    "FlowStep",
    "FlowSummary",
    "FlowResult",
    "ExecutionContext",
    "ExecutorResult",
    "TestManifest",
    "PinnedResult",
    # Exceptions
    "AgentFlowsError",
    "FlowError",
    "FlowExecutionError",
    "ConfigurationError",
    "ExecutorError",
    "ExecutorNotFoundError",
    "ApiError",
    "FlowNotFoundError",
    "IntegrationError",
    "MCPError",
]
