"""Memory Manager – short-term and long-term memory with consolidation.

Short-term memory stores recent observations up to a configurable cap.
Long-term memory persists important memories indefinitely.  Consolidation
moves high-importance short-term memories into long-term storage.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")


@dataclass
class Memory:
    """A single memory record.

    Attributes:
        memory_id: Unique identifier, auto-generated.
        content: The stored payload.
        importance: Importance score in ``[0.0, 1.0]``.
        tags: Labels for semantic recall filtering.
        timestamp: Unix epoch time at creation.
    """

    content: Any
    importance: float = 0.5
    tags: list[str] = field(default_factory=list)
    memory_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


class MemoryManager:
    """Manages short-term and long-term memory stores.

    Short-term memory is a bounded FIFO buffer.  Long-term memory is an
    unbounded list seeded by the consolidation pass.

    Attributes:
        _short_term: Bounded list of recent :class:`Memory` objects.
        _long_term: Unbounded list of consolidated :class:`Memory` objects.
        _short_term_capacity: Maximum number of short-term memories.
        _consolidation_threshold: Minimum importance for consolidation.
    """

    def __init__(
        self,
        short_term_capacity: int = 100,
        consolidation_threshold: float = 0.7,
    ) -> None:
        """Initialise the memory manager.

        Args:
            short_term_capacity: Maximum short-term memory slots. Defaults to 100.
            consolidation_threshold: Minimum importance for a short-term memory
                to be moved into long-term storage. Defaults to 0.7.
        """
        self._short_term: list[Memory] = []
        self._long_term: list[Memory] = []
        self._short_term_capacity = short_term_capacity
        self._consolidation_threshold = consolidation_threshold
        log.info(
            "MemoryManager initialised",
            capacity=short_term_capacity,
            threshold=consolidation_threshold,
        )

    def remember(self, memory: Memory) -> str:
        """Store a new memory in short-term memory, evicting the oldest if full.

        Args:
            memory: The :class:`Memory` to store.

        Returns:
            The ``memory_id`` of the stored memory.
        """
        if len(self._short_term) >= self._short_term_capacity:
            evicted = self._short_term.pop(0)
            log.debug("Short-term eviction", memory_id=evicted.memory_id)
        self._short_term.append(memory)
        log.debug("Memory stored", memory_id=memory.memory_id, importance=memory.importance)
        return memory.memory_id

    def recall(
        self,
        tags: list[str] | None = None,
        long_term: bool = False,
        limit: int | None = None,
    ) -> list[Memory]:
        """Retrieve memories optionally filtered by tags.

        Args:
            tags: If provided, only memories containing *all* given tags are
                returned.
            long_term: When ``True`` searches long-term memory; otherwise
                searches short-term memory.
            limit: Maximum number of memories to return (most recent first).

        Returns:
            List of matching :class:`Memory` objects, newest first.
        """
        source = self._long_term if long_term else self._short_term
        results = source[::-1]  # newest first

        if tags:
            results = [m for m in results if all(t in m.tags for t in tags)]

        if limit is not None:
            results = results[:limit]

        log.debug(
            "Memory recalled",
            count=len(results),
            long_term=long_term,
            tags=tags,
        )
        return results

    def consolidate(self) -> int:
        """Move high-importance short-term memories to long-term storage.

        Memories whose ``importance`` meets or exceeds the consolidation
        threshold are appended to long-term memory and removed from
        short-term memory.

        Returns:
            Number of memories consolidated.
        """
        to_consolidate = [
            m for m in self._short_term if m.importance >= self._consolidation_threshold
        ]
        for memory in to_consolidate:
            self._long_term.append(memory)
            self._short_term.remove(memory)

        if to_consolidate:
            log.info(
                "Memories consolidated",
                count=len(to_consolidate),
                long_term_total=len(self._long_term),
            )
        return len(to_consolidate)

    def get_stats(self) -> dict[str, int]:
        """Return counts for both memory stores.

        Returns:
            Dict with ``short_term_count`` and ``long_term_count``.
        """
        return {
            "short_term_count": len(self._short_term),
            "long_term_count": len(self._long_term),
        }
