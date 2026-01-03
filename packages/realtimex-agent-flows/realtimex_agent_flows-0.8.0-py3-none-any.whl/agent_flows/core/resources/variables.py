"""Variable management for flow execution."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from agent_flows.api.http_client import ApiClient
from agent_flows.exceptions import ApiError, SystemVariableError
from agent_flows.models.config import AgentFlowsConfig
from agent_flows.models.flow import FlowConfig
from agent_flows.utils.dict_utils import deep_update, set_nested_value
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class VariableManager:
    """Centralized manager for flow variable initialization and processing."""

    def __init__(self, config: AgentFlowsConfig) -> None:
        self._config = config
        self._system_api_client = ApiClient(
            base_url=config.app_base_url,
            api_key=config.api_key,
            timeout=config.timeout,
            max_retries=config.max_retries,
        )

    async def close(self) -> None:
        """Release owned resources."""
        await self._system_api_client.close()

    async def initialize_variables(
        self, flow_config: FlowConfig, runtime_variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Initialize flow variables from multiple sources with defined precedence.

        Variable sources and precedence (later sources override earlier ones):
        1. Flow defaults (only variables with source="user_input")
        2. System variables (from API endpoint, always fetched per-user)
        3. Runtime variables (provided at execution time)

        System variables with source="system" in flow config are IGNORED to ensure
        actual user-specific values from the API take precedence.

        Args:
            flow_config: Flow configuration containing variable definitions
            runtime_variables: Variables provided at runtime execution

        Returns:
            Initialized variables dictionary with nested structures for dotted keys

        Example:
            flow_manager = VariableManager(config)
            flow_variables = await flow_manager.initialize_variables(
                flow_config, {"custom_var": "value"}
            )
            # Returns: {"user": {"email": "..."}, "custom_var": "value", ...}
        """
        runtime_vars = runtime_variables or {}

        # Extract flow configuration variables
        flow_vars = self._extract_flow_variables(flow_config)

        # Always attempt to load system-provided variables
        system_vars = await self._load_system_variables()

        # Process runtime variables with dotted key support
        processed_runtime = self._process_dotted_variables(
            runtime_vars, variable_source="runtime", fallback_on_conflict=True
        )

        # Merge with precedence: flow_defaults < system_vars < runtime_vars
        final_variables = flow_vars.copy()
        if system_vars:
            deep_update(final_variables, system_vars)
        deep_update(final_variables, processed_runtime)

        log.debug(
            "Variables initialized",
            flow_defaults=len(flow_vars),
            system_vars=len(system_vars),
            runtime_vars=len(processed_runtime),
            total=len(final_variables),
        )
        return final_variables

    async def _load_system_variables(self) -> dict[str, Any]:
        """Load user-specific system variables from API endpoint.

        System variables are always fetched fresh for each execution to ensure
        user-specific values (like email, name, timestamps) are current.

        Returns:
            Processed system variables with nested structure, or empty dict on failure
        """
        if not self._config.load_system_variables:
            log.info("Skipping system variable fetch (disabled in configuration)")
            return {}

        try:
            raw_variables = await self._fetch_system_variables()
        except SystemVariableError as exc:
            log.warning(
                "Failed to load system variables from API",
                error=str(exc),
            )
            return {}

        if not raw_variables:
            log.debug("System variable endpoint returned empty response")
            return {}

        processed = self._process_dotted_variables(
            raw_variables, variable_source="system", fallback_on_conflict=False
        )

        log.debug(
            "System variables loaded from API",
            variable_count=len(processed),
            variable_names=list(processed.keys()),
        )

        return processed

    async def _fetch_system_variables(self) -> Mapping[str, Any]:
        """Fetch system variables from the desktop app backend."""
        try:
            payload = await self._system_api_client.request("GET", "/api/system/prompt-variables")
        except ApiError as exc:
            raise SystemVariableError("Backend request failed") from exc

        try:
            return self._parse_system_payload(payload)
        except SystemVariableError:
            raise
        except Exception as exc:  # pragma: no cover - defensive guard
            raise SystemVariableError("Unexpected error parsing system variables") from exc

    def _parse_system_payload(self, payload: Any) -> Mapping[str, Any]:
        """Parse the expected backend payload format into a key/value mapping."""
        if not isinstance(payload, Mapping):
            raise SystemVariableError("System variable payload must be a JSON object")

        variables = payload.get("variables")
        if not isinstance(variables, list):
            raise SystemVariableError("System variable payload missing 'variables' list")

        result: dict[str, Any] = {}
        for item in variables:
            if not isinstance(item, Mapping):
                continue
            key = item.get("key")
            if not isinstance(key, str) or not key:
                continue
            result[key] = item.get("value")
        return result

    def _extract_flow_variables(self, flow_config: FlowConfig) -> dict[str, Any]:
        """Extract default variables from flow configuration.

        Only extracts variables with source="user_input". Variables with
        source="system" are intentionally ignored to prevent hardcoded
        system variable defaults from overriding actual user-specific values
        loaded from the API.

        Returns:
            Dictionary of user-input variables with nested structures for dotted keys
        """
        variables: dict[str, Any] = {}

        for step in flow_config.steps:
            if step.type == "flow_variables":
                variable_definitions = step.config.get("variables", [])

                for var_def in variable_definitions:
                    if not isinstance(var_def, dict) or "name" not in var_def:
                        continue

                    var_name = var_def["name"]
                    if not VariableManager._is_valid_variable_name(var_name):
                        continue

                    var_source = var_def.get("source", "user_input")

                    # Only extract user_input variables; ignore system variables
                    # to ensure API-provided system values take precedence
                    if var_source == "user_input":
                        default_value = var_def.get("value", "")
                        self._set_default_variable(variables, var_name, default_value)

                break

        log.debug(
            "Extracted flow defaults (user_input only)",
            variable_count=len(variables),
            variable_names=list(variables.keys()),
        )

        return variables

    @staticmethod
    def _process_dotted_variables(
        input_variables: Mapping[str, Any] | None,
        variable_source: str,
        *,
        fallback_on_conflict: bool,
    ) -> dict[str, Any]:
        """Process variables with dotted key notation into nested structures.

        Args:
            input_variables: Variables that may contain dotted keys
            variable_source: Source identifier for logging (e.g., "runtime", "system")
            fallback_on_conflict: Whether to fall back to flat keys when conflicts occur

        Returns:
            Processed variables with dotted keys converted to nested structures
        """
        if not input_variables:
            return {}

        processed = {}

        for key, value in input_variables.items():
            if not isinstance(key, str):
                continue
            if "." in key:
                try:
                    set_nested_value(processed, key, value)
                except ValueError as conflict_error:
                    log.warning(
                        f"{variable_source.title()} variable conflict - using flat key fallback",
                        variable_key=key,
                        variable_source=variable_source,
                        conflict_details=str(conflict_error),
                    )
                    if fallback_on_conflict:
                        processed[key] = value
            else:
                processed[key] = value

        return processed

    @staticmethod
    def _set_default_variable(
        target_variables: dict[str, Any], var_name: str, default_value: Any
    ) -> None:
        """Set a default variable with dotted-notation support and conflict handling."""
        if "." not in var_name:
            target_variables[var_name] = default_value
            return

        try:
            set_nested_value(target_variables, var_name, default_value)
        except ValueError as conflict_error:
            log.warning(
                "Default variable conflict - using flat key fallback",
                variable=var_name,
                conflict_details=str(conflict_error),
            )
            target_variables[var_name] = default_value

    @staticmethod
    def _is_valid_variable_name(var_name: Any) -> bool:
        """Validate variable name for basic requirements.

        Args:
            var_name: Variable name to validate

        Returns:
            True if the variable name is valid, False otherwise
        """
        return var_name is not None and var_name != "" and isinstance(var_name, str)
