"""Built-in flow step executors with lazy loading."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .api_call import ApiCallExecutor
    from .base import BaseExecutor
    from .conditional import ConditionalExecutor
    from .finish import FinishExecutor
    from .flow_variables import FlowVariablesExecutor
    from .llm_instruction import LlmInstructionExecutor
    from .loop import LoopExecutor
    from .mcp_server_action import McpServerActionExecutor
    from .stream_ui import StreamUIExecutor
    from .switch import SwitchExecutor
    from .web_scraping import WebScrapingExecutor
    from .web_search import WebSearchExecutor


_LAZY_MAP = {
    "BaseExecutor": (".base", "BaseExecutor"),
    "FlowVariablesExecutor": (".flow_variables", "FlowVariablesExecutor"),
    "ApiCallExecutor": (".api_call", "ApiCallExecutor"),
    "CodeInterpreterExecutor": (".code_interpreter", "CodeInterpreterExecutor"),
    "LlmInstructionExecutor": (".llm_instruction", "LlmInstructionExecutor"),
    "WebScrapingExecutor": (".web_scraping", "WebScrapingExecutor"),
    "ConditionalExecutor": (".conditional", "ConditionalExecutor"),
    "SwitchExecutor": (".switch", "SwitchExecutor"),
    "LoopExecutor": (".loop", "LoopExecutor"),
    "McpServerActionExecutor": (".mcp_server_action", "McpServerActionExecutor"),
    "SetVariablesExecutor": (".set_variables", "SetVariablesExecutor"),
    "StreamUIExecutor": (".stream_ui", "StreamUIExecutor"),
    "WebSearchExecutor": (".web_search", "WebSearchExecutor"),
    "FinishExecutor": (".finish", "FinishExecutor"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY_MAP:
        module_name, attr = _LAZY_MAP[name]
        module = __import__(f"{__name__}{module_name}", fromlist=[attr])
        value = getattr(module, attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:  # pragma: no cover
    return sorted(list(globals()) + list(_LAZY_MAP.keys()))


__all__ = [
    "BaseExecutor",
    "FlowVariablesExecutor",
    "ApiCallExecutor",
    "CodeInterpreterExecutor",
    "LlmInstructionExecutor",
    "WebScrapingExecutor",
    "ConditionalExecutor",
    "SwitchExecutor",
    "LoopExecutor",
    "McpServerActionExecutor",
    "SetVariablesExecutor",
    "StreamUIExecutor",
    "WebSearchExecutor",
    "FinishExecutor",
]
