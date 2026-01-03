"""Base executor class - placeholder implementation."""

from abc import ABC, abstractmethod
from typing import Any

from agent_flows.models.execution import ExecutionContext, ExecutorResult


class BaseExecutor(ABC):
    """Base class for flow step executors."""

    @abstractmethod
    async def execute(
        self,
        config: dict[str, Any],
        context: ExecutionContext,
    ) -> ExecutorResult:
        """Execute the step.

        Args:
            config: Step configuration
            context: Execution context

        Returns:
            ExecutorResult with execution results
        """
        pass

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate step configuration.

        Args:
            config: Step configuration to validate

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass

    def get_required_fields(self) -> list[str]:
        """Get list of required configuration fields.

        Returns:
            List of required field names
        """
        return []

    def get_optional_fields(self) -> list[str]:
        """Get list of optional configuration fields.

        Returns:
            List of optional field names
        """
        return []
