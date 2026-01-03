"""Consolidated loader for flow configurations from any source."""

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from agent_flows.core.flows.registry import FlowRegistry
from agent_flows.models.flow import FlowConfig
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class FlowLoader:
    """Loads flow configurations from files, dictionaries, or registry."""

    def __init__(self, flow_registry: FlowRegistry | None = None):
        """Initialize with optional flow registry for UUID resolution.

        Args:
            flow_registry: FlowRegistry instance for UUID lookups
        """
        self.flow_registry = flow_registry

    async def load(self, flow_source: FlowConfig | str) -> FlowConfig:
        """Load flow configuration from any supported source.

        Args:
            flow_source: FlowConfig object, UUID string, or file path

        Returns:
            FlowConfig object ready for execution

        Raises:
            ValueError: If flow_source type is invalid or loading fails
        """
        if isinstance(flow_source, FlowConfig):
            log.debug("Using provided FlowConfig", flow_name=flow_source.name)
            return flow_source

        if isinstance(flow_source, str):
            # Prioritize file path detection
            if Path(flow_source).exists():
                log.debug("Loading flow from file", file_path=flow_source)
                return self.from_file(flow_source)

            # Fallback to UUID format detection
            if self._is_uuid_format(flow_source):
                if not self.flow_registry:
                    raise ValueError("FlowRegistry required for UUID resolution")
                log.debug("Loading flow from registry", flow_id=flow_source)
                return await self.flow_registry.get_flow(flow_source)

            raise ValueError("Invalid flow source string: expected existing file path or flow UUID")

        raise ValueError(f"Invalid flow source type: {type(flow_source)}")

    @staticmethod
    def from_file(file_path: str) -> FlowConfig:
        """Load flow configuration from JSON file.

        Args:
            file_path: Path to JSON file containing flow configuration

        Returns:
            FlowConfig object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file contains invalid JSON or config
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Flow file not found: {file_path}")

        try:
            with open(path) as f:
                flow_data = json.load(f)

            log.debug("Loading flow from file", file_path=file_path)
            return FlowConfig(**flow_data)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in flow file {file_path}: {str(e)}") from e
        except Exception as e:
            raise ValueError(f"Failed to load flow from {file_path}: {str(e)}") from e

    @staticmethod
    def from_dict(flow_dict: dict[str, Any]) -> FlowConfig:
        """Create flow configuration from dictionary.

        Args:
            flow_dict: Dictionary containing flow configuration

        Returns:
            FlowConfig object

        Raises:
            ValueError: If dictionary contains invalid configuration
        """
        try:
            log.debug("Loading flow from dictionary")
            return FlowConfig(**flow_dict)
        except Exception as e:
            raise ValueError(f"Failed to create flow from dictionary: {str(e)}") from e

    def _is_uuid_format(self, value: str) -> bool:
        """Return True if the value can be parsed as a UUID string."""
        try:
            UUID(value)
        except (ValueError, TypeError):
            return False
        return True
