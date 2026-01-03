"""Central registry responsible for retrieving and caching flow metadata."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from agent_flows.api.error_mapping import FlowApiErrorMapper
from agent_flows.api.http_client import ApiClient
from agent_flows.core.flows.cache import FlowCache
from agent_flows.exceptions import ApiError
from agent_flows.models.flow import FlowConfig
from agent_flows.utils.logging import get_logger

log = get_logger(__name__)


class FlowRegistry:
    """Central registry for flow discovery and retrieval via the Agent Flows API."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        flow_cache: FlowCache | None = None,
        flow_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        """Initialize FlowRegistry with its own API client.

        Args:
            base_url: Base URL for the Agent Flows API
            api_key: API authentication key
            flow_cache: Optional custom cache implementation
            flow_ttl: Time-to-live for cached flows in seconds
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for transient failures
        """
        self.api_client = ApiClient(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            error_mapper=FlowApiErrorMapper(),
        )
        self._cache = flow_cache or FlowCache(default_ttl=flow_ttl)
        self._flow_ttl = flow_ttl

    async def list_flows(self) -> list[FlowConfig]:
        """List all flows accessible to the authenticated user.

        Returns:
            A list of flow configurations fetched from the remote service.

        Raises:
            ApiError: If the API returns an unexpected payload shape or a non-list response.
        """
        log.info("Fetching flows from API", endpoint="agent-flows")
        payload = await self.api_client.request(
            "GET",
            "agent-flows",
            params={"ignore_purchased_check": "y"},
        )

        if payload is None:
            return []
        if not isinstance(payload, list):
            raise ApiError(
                f"Invalid response format: expected list, received {type(payload)}",
                status_code=200,
                response_body=str(payload),
            )

        flows: list[FlowConfig] = []

        for item in payload:
            if not isinstance(item, dict):
                log.warning("Skipping malformed flow record", item=str(item))
                continue

            config = self._build_flow_config_data(item)
            flow_uuid = config.get("uuid", "").strip()

            try:
                flow_config = FlowConfig(**config)
            except (ValidationError, ValueError) as exc:
                log.warning(
                    "Discarding invalid flow from API response",
                    flow_id=flow_uuid or "<unknown>",
                    error=str(exc),
                )
                continue

            flows.append(flow_config)

            if flow_uuid:
                await self._cache.put(flow_uuid, flow_config, ttl=self._flow_ttl)

        log.info("Fetched flows from API", count=len(flows))
        return [flow.model_copy(deep=True) for flow in flows]

    async def get_flow(self, flow_id: str, *, bypass_cache: bool = False) -> FlowConfig:
        """Retrieve a single flow configuration.

        Args:
            flow_id: UUID of the flow to retrieve.
            bypass_cache: When True, force a fresh fetch from the API.

        Returns:
            The flow configuration matching ``flow_id``.

        Raises:
            ValueError: If ``flow_id`` is empty.
            ApiError: If the API response is not a mapping.
        """
        if not flow_id or not flow_id.strip():
            raise ValueError("Flow ID cannot be empty")

        flow_id = flow_id.strip()

        if not bypass_cache:
            cached = await self._cache.get(flow_id)
            if cached is not None:
                log.info("Returning cached flow", flow_id=flow_id)
                return cached

        log.info("Fetching flow from API", flow_id=flow_id)
        payload = await self.api_client.request(
            "GET",
            f"agent-flows/{flow_id}",
            params={"ignore_purchased_check": "y"},
        )

        if not isinstance(payload, dict):
            raise ApiError(
                f"Invalid response format: expected dict, received {type(payload)}",
                status_code=200,
                response_body=str(payload),
            )

        config_data = self._build_flow_config_data(payload, flow_id)
        flow_config = FlowConfig(**config_data)

        await self._cache.put(flow_id, flow_config, ttl=self._flow_ttl)
        return flow_config

    async def invalidate_cache(self, flow_id: str | None = None) -> None:
        """Invalidate cached flow data.

        Args:
            flow_id: Optional flow identifier. If provided, only that flow is removed;
                otherwise, the entire cache is cleared.
        """
        if flow_id:
            await self._cache.invalidate(flow_id.strip())
            log.debug("Invalidated cached flow", flow_id=flow_id.strip())
        else:
            await self._cache.clear()
            log.debug("Cleared all cached flow data")

    async def close(self) -> None:
        """Close the API client and cleanup resources."""
        if hasattr(self.api_client, "close"):
            await self.api_client.close()

    def _build_flow_config_data(
        self, item: dict[str, Any], flow_id: str | None = None
    ) -> dict[str, Any]:
        """Flatten API payload into a ``FlowConfig`` compatible mapping.

        Args:
            item: Raw record returned by the API.
            flow_id: Optional fallback identifier when the record omits one.

        Returns:
            Dictionary ready to be passed into ``FlowConfig``.
        """
        body = item.get("body") if isinstance(item.get("body"), dict) else {}

        config = {
            "uuid": (item.get("id") or body.get("uuid") or flow_id or "").strip(),
            "name": item.get("name") or body.get("name", ""),
            "description": item.get("description") or body.get("description", ""),
            "active": body.get("active", True),
            "steps": body.get("steps", []),
            "created_at": body.get("created_at"),
            "updated_at": body.get("updated_at"),
        }

        for key, value in body.items():
            config.setdefault(key, value)

        return config
