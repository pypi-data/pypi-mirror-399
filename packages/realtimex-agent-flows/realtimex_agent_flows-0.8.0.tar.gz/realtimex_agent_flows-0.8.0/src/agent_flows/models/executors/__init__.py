"""Executor configuration models."""

from .api_call import ApiCallExecutorConfig
from .code_interpreter import CodeInterpreterExecutorConfig
from .conditional import ConditionalExecutorConfig
from .finish import FinishExecutorConfig
from .flow_variables import FlowVariablesExecutorConfig
from .llm_instruction import LlmInstructionExecutorConfig
from .loop import LoopExecutorConfig
from .mcp_server_action import McpServerActionExecutorConfig
from .run_command import RunCommandExecutorConfig
from .stream_ui import StreamUIExecutorConfig
from .switch import SwitchExecutorConfig
from .web_scraping import WebScrapingExecutorConfig
from .web_search import WebSearchExecutorConfig

ExecutorConfig = (
    FlowVariablesExecutorConfig
    | ApiCallExecutorConfig
    | WebScrapingExecutorConfig
    | LlmInstructionExecutorConfig
    | ConditionalExecutorConfig
    | CodeInterpreterExecutorConfig
    | SwitchExecutorConfig
    | LoopExecutorConfig
    | McpServerActionExecutorConfig
    | WebSearchExecutorConfig
    | FinishExecutorConfig
    | StreamUIExecutorConfig
    | RunCommandExecutorConfig
)

__all__ = [
    "FlowVariablesExecutorConfig",
    "ApiCallExecutorConfig",
    "WebScrapingExecutorConfig",
    "LlmInstructionExecutorConfig",
    "ConditionalExecutorConfig",
    "CodeInterpreterExecutorConfig",
    "SwitchExecutorConfig",
    "LoopExecutorConfig",
    "McpServerActionExecutorConfig",
    "WebSearchExecutorConfig",
    "FinishExecutorConfig",
    "StreamUIExecutorConfig",
    "RunCommandExecutorConfig",
    "ExecutorConfig",
]
