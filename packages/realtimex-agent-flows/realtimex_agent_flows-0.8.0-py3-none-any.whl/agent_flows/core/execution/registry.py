"""ExecutorRegistry for managing flow step executors."""

from __future__ import annotations

import inspect
import re
import threading
from importlib import import_module
from typing import Any

import structlog

from agent_flows.exceptions import ExecutorNotFoundError
from agent_flows.executors.base import BaseExecutor

logger = structlog.get_logger(__name__)

_BUILT_IN_EXECUTORS: dict[str, tuple[str, str]] = {
    "flow_variables": ("agent_flows.executors.flow_variables", "FlowVariablesExecutor"),
    "apiCall": ("agent_flows.executors.api_call", "ApiCallExecutor"),
    "codeInterpreter": ("agent_flows.executors.code_interpreter", "CodeInterpreterExecutor"),
    "llmInstruction": ("agent_flows.executors.llm_instruction", "LlmInstructionExecutor"),
    "setVariables": ("agent_flows.executors.set_variables", "SetVariablesExecutor"),
    "webScraping": ("agent_flows.executors.web_scraping", "WebScrapingExecutor"),
    "webSearch": ("agent_flows.executors.web_search", "WebSearchExecutor"),
    "conditional": ("agent_flows.executors.conditional", "ConditionalExecutor"),
    "switch": ("agent_flows.executors.switch", "SwitchExecutor"),
    "loop": ("agent_flows.executors.loop", "LoopExecutor"),
    "mcpServerAction": ("agent_flows.executors.mcp_server_action", "McpServerActionExecutor"),
    "streamUI": ("agent_flows.executors.stream_ui", "StreamUIExecutor"),
    "finish": ("agent_flows.executors.finish", "FinishExecutor"),
    "runCommand": ("agent_flows.executors.run_command", "RunCommandExecutor"),
}


class ExecutorRegistry:
    """Thread-safe registry for managing flow step executors."""

    def __init__(self) -> None:
        self._executors: dict[str, type[BaseExecutor]] = {}
        self._lock = threading.RLock()

    def register_executor(
        self,
        step_type: str,
        executor_class: type[BaseExecutor],
        override: bool = False,
    ) -> None:
        """Register a custom executor."""
        with self._lock:
            if not self._is_valid_step_type(step_type):
                raise ValueError(
                    f"Invalid step type '{step_type}'. Must be alphanumeric with optional underscores/hyphens"
                )

            if not self._is_valid_executor_class(executor_class):
                raise TypeError(
                    f"Executor class {executor_class.__name__} must inherit from BaseExecutor"
                )

            if step_type in self._executors and not override:
                raise ValueError(f"Executor for step type '{step_type}' already registered")

            self._executors[step_type] = executor_class

            logger.debug(
                "Executor registered",
                step_type=step_type,
                executor_class=executor_class.__name__,
            )

    def get_executor(self, step_type: str) -> BaseExecutor:
        """Get executor instance for a step type."""
        with self._lock:
            if step_type not in self._executors:
                self._load_built_in(step_type)

            if step_type not in self._executors:
                raise ExecutorNotFoundError(f"No executor registered for step type: {step_type}")

            executor_class = self._executors[step_type]
            try:
                return executor_class()
            except Exception as e:  # pragma: no cover - defensive guard
                logger.error(
                    "Failed to instantiate executor",
                    step_type=step_type,
                    error=str(e),
                )
                raise ExecutorNotFoundError(
                    f"Failed to create executor instance for step type: {step_type}"
                ) from e

    def is_registered(self, step_type: str) -> bool:
        """Check if a step type is registered."""
        with self._lock:
            if step_type not in self._executors:
                self._load_built_in(step_type)
            return step_type in self._executors

    def validate_step_config(self, step_type: str, config: dict[str, Any]) -> bool:
        """Validate the configuration for a given step type."""
        executor = self.get_executor(step_type)
        return executor.validate_config(config)

    def _load_built_in(self, step_type: str) -> None:
        module_info = _BUILT_IN_EXECUTORS.get(step_type)
        if not module_info:
            return
        module_name, attr = module_info
        try:
            module = import_module(module_name)
            executor_cls = getattr(module, attr)
            self._executors[step_type] = executor_cls
        except Exception as e:  # pragma: no cover - defensive guard
            logger.warning(
                "Failed to load built-in executor",
                step_type=step_type,
                module=module_name,
                error=str(e),
            )

    def _is_valid_step_type(self, step_type: str) -> bool:
        """Validate step type naming conventions."""
        if not isinstance(step_type, str) or not step_type:
            return False

        # Allow alphanumeric characters, underscores, and hyphens
        return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", step_type))

    def _is_valid_executor_class(self, executor_class: type[Any]) -> bool:
        """Validate that executor class implements BaseExecutor."""
        if not inspect.isclass(executor_class):
            return False

        # Check if it's a subclass of BaseExecutor
        try:
            return issubclass(executor_class, BaseExecutor)
        except TypeError:  # pragma: no cover - defensive guard
            return False
