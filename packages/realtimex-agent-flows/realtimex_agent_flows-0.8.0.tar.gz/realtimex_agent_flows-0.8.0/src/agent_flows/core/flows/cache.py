"""Caching system for flow configurations."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any

from agent_flows.models.flow import FlowConfig
from agent_flows.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class CacheEntry:
    """In-memory cache entry for a flow configuration."""

    flow_config: FlowConfig
    expires_at: float | None
    last_access: float

    def is_expired(self, now: float) -> bool:
        return self.expires_at is not None and now >= self.expires_at

    def clone(self) -> FlowConfig:
        return self.flow_config.model_copy(deep=True)


class FlowCache:
    """Lightweight async-safe cache for `FlowConfig` objects."""

    def __init__(self, max_size: int = 128, default_ttl: int = 600) -> None:
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._entries: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._hits = 0
        self._misses = 0

    async def get(self, flow_id: str) -> FlowConfig | None:
        """Return a cached flow configuration if present and not expired."""
        async with self._lock:
            entry = self._entries.get(flow_id)
            if entry is None:
                self._misses += 1
                logger.debug("Flow cache miss", flow_id=flow_id)
                return None

            now = time.monotonic()
            if entry.is_expired(now):
                self._entries.pop(flow_id, None)
                self._misses += 1
                logger.debug("Flow cache entry expired", flow_id=flow_id)
                return None

            entry.last_access = now
            self._hits += 1
            logger.debug("Flow cache hit", flow_id=flow_id)
            return entry.clone()

    async def put(self, flow_id: str, flow_config: FlowConfig, ttl: int | None = None) -> None:
        """Store a flow configuration in the cache."""
        ttl = self.default_ttl if ttl is None else ttl
        expires_at = None if ttl <= 0 else time.monotonic() + ttl
        entry = CacheEntry(
            flow_config=flow_config.model_copy(deep=True),
            expires_at=expires_at,
            last_access=time.monotonic(),
        )

        async with self._lock:
            if flow_id not in self._entries and len(self._entries) >= self.max_size:
                self._evict_lru_locked()
            self._entries[flow_id] = entry
            logger.debug("Cached flow", flow_id=flow_id, ttl=ttl)

    async def invalidate(self, flow_id: str) -> bool:
        """Remove a single flow from the cache."""
        async with self._lock:
            removed = self._entries.pop(flow_id, None) is not None
            if removed:
                logger.debug("Invalidated cached flow", flow_id=flow_id)
            return removed

    async def clear(self) -> None:
        """Clear all cached flows."""
        async with self._lock:
            count = len(self._entries)
            self._entries.clear()
        if count:
            logger.info("Cleared cached flows", removed=count)

    async def cleanup_expired(self) -> int:
        """Remove expired entries and return the number removed."""
        async with self._lock:
            now = time.monotonic()
            expired = [key for key, entry in self._entries.items() if entry.is_expired(now)]
            for key in expired:
                self._entries.pop(key, None)
            if expired:
                logger.debug("Removed expired cached flows", removed=len(expired))
            return len(expired)

    async def get_stats(self) -> dict[str, Any]:
        """Return simple cache statistics."""
        async with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests) if total_requests else 0.0
            return {
                "size": len(self._entries),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
            }

    def _evict_lru_locked(self) -> None:
        if not self._entries:
            return
        lru_key = min(self._entries, key=lambda key: self._entries[key].last_access)
        self._entries.pop(lru_key, None)
        logger.debug("Evicted least recently used flow", flow_id=lru_key)
