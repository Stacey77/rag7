"""Edge data cache with TTL expiry and LRU eviction."""

from __future__ import annotations

import asyncio
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from loguru import logger


T = TypeVar("T")


@dataclass
class CacheEntry:
    """A single cache entry with TTL metadata.

    Attributes:
        key: Cache key.
        value: Stored value.
        ttl_s: Time-to-live in seconds (None = never expires).
        created_at: Monotonic creation timestamp.
        last_accessed_at: Monotonic last-access timestamp.
        hit_count: Number of times this entry has been read.
    """

    key: str
    value: Any
    ttl_s: float | None
    created_at: float = field(default_factory=time.monotonic)
    last_accessed_at: float = field(default_factory=time.monotonic)
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        """Whether this entry has exceeded its TTL."""
        if self.ttl_s is None:
            return False
        return (time.monotonic() - self.created_at) > self.ttl_s


class EdgeCache:
    """Local edge data cache with TTL expiry and LRU eviction.

    Implements an async-safe, bounded LRU cache with optional per-entry
    TTL.  Expired entries are lazily evicted on access and eagerly
    evicted during ``purge_expired()``.

    Attributes:
        _store: Ordered dict acting as LRU store (most-recently-used last).
        _max_size: Maximum number of entries before LRU eviction.
        _default_ttl_s: Default TTL when none is specified per entry.
        _hits: Cache hit counter.
        _misses: Cache miss counter.
        _evictions: LRU eviction counter.
    """

    def __init__(
        self,
        max_size: int = 1_000,
        default_ttl_s: float | None = 300.0,
    ) -> None:
        """Initialise the edge cache.

        Args:
            max_size: Maximum number of cached entries.
            default_ttl_s: Default TTL in seconds (None = no expiry).

        Raises:
            ValueError: If ``max_size`` < 1.
        """
        if max_size < 1:
            raise ValueError(f"max_size must be ≥1, got {max_size}")

        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_size = max_size
        self._default_ttl_s = default_ttl_s
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        logger.info("EdgeCache initialised (max_size={}, default_ttl={}s)", max_size, default_ttl_s)

    async def get(self, key: str) -> Any | None:
        """Retrieve a cached value by key.

        Expired entries are evicted on access and treated as misses.

        Args:
            key: Cache key.

        Returns:
            Cached value, or ``None`` if not found or expired.
        """
        await asyncio.sleep(0)

        entry = self._store.get(key)
        if entry is None:
            self._misses += 1
            return None

        if entry.is_expired:
            self._evict(key)
            self._misses += 1
            logger.debug("Cache miss (expired): '{}'", key)
            return None

        # LRU: move to end (most recently used)
        self._store.move_to_end(key)
        entry.last_accessed_at = time.monotonic()
        entry.hit_count += 1
        self._hits += 1
        logger.debug("Cache hit: '{}'", key)
        return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_s: float | None = ...,  # type: ignore[assignment]
    ) -> None:
        """Store a value in the cache.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl_s: TTL in seconds; uses ``default_ttl_s`` when omitted,
                or ``None`` for no expiry.
        """
        await asyncio.sleep(0)

        effective_ttl = self._default_ttl_s if ttl_s is ... else ttl_s

        entry = CacheEntry(key=key, value=value, ttl_s=effective_ttl)

        if key in self._store:
            self._store.move_to_end(key)
        elif len(self._store) >= self._max_size:
            # Evict LRU (first item)
            oldest_key, _ = next(iter(self._store.items()))
            self._evict(oldest_key)

        self._store[key] = entry
        logger.debug("Cache set: '{}' (ttl={}s)", key, effective_ttl)

    async def delete(self, key: str) -> bool:
        """Remove a key from the cache.

        Args:
            key: Cache key to remove.

        Returns:
            ``True`` if the key existed and was removed.
        """
        await asyncio.sleep(0)
        if key in self._store:
            del self._store[key]
            logger.debug("Cache delete: '{}'", key)
            return True
        return False

    async def purge_expired(self) -> int:
        """Eagerly remove all expired entries.

        Returns:
            Number of entries purged.
        """
        await asyncio.sleep(0)
        expired_keys = [k for k, v in self._store.items() if v.is_expired]
        for key in expired_keys:
            self._evict(key)
        if expired_keys:
            logger.info("Purged {} expired cache entries", len(expired_keys))
        return len(expired_keys)

    async def clear(self) -> int:
        """Remove all entries from the cache.

        Returns:
            Number of entries removed.
        """
        await asyncio.sleep(0)
        count = len(self._store)
        self._store.clear()
        logger.info("Cache cleared ({} entries removed)", count)
        return count

    def stats(self) -> dict[str, Any]:
        """Return cache performance statistics.

        Returns:
            Dictionary with hit/miss/eviction counts and hit rate.
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            "size": len(self._store),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": round(hit_rate, 4),
        }

    def _evict(self, key: str) -> None:
        """Remove an entry and increment the eviction counter.

        Args:
            key: Key to evict.
        """
        if key in self._store:
            del self._store[key]
            self._evictions += 1
