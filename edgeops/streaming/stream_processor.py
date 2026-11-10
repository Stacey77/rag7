"""Event stream processing with filtering, aggregation, and windowing."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

import numpy as np
from loguru import logger


@dataclass
class StreamEvent:
    """A single event in the data stream.

    Attributes:
        event_id: Unique identifier.
        topic: Event topic/stream name.
        payload: Event data dictionary.
        timestamp: Event creation time (monotonic seconds).
        partition_key: Optional key for partitioned processing.
    """

    event_id: str
    topic: str
    payload: dict[str, Any]
    timestamp: float = field(default_factory=time.monotonic)
    partition_key: str = ""


@dataclass
class WindowResult:
    """Result of a windowed aggregation.

    Attributes:
        topic: Source topic.
        window_start: Window start time (monotonic).
        window_end: Window end time (monotonic).
        n_events: Number of events in the window.
        aggregations: Computed aggregation values.
    """

    topic: str
    window_start: float
    window_end: float
    n_events: int
    aggregations: dict[str, Any]


# Type aliases
FilterFn = Callable[[StreamEvent], bool]
AggregatorFn = Callable[[list[StreamEvent]], dict[str, Any]]


class StreamProcessor:
    """Event stream processing with filtering, aggregation, and windowing.

    Supports registering named topics, per-topic filter chains,
    tumbling window aggregations, and async event processing.

    Attributes:
        topics: Registered topic names and their event buffers.
        _filters: Per-topic filter functions.
        _aggregators: Per-topic aggregation functions.
        _window_size_s: Default tumbling window size in seconds.
        _processed_count: Total processed event count.
    """

    def __init__(self, window_size_s: float = 60.0, buffer_size: int = 10_000) -> None:
        """Initialise the stream processor.

        Args:
            window_size_s: Default tumbling window size in seconds.
            buffer_size: Maximum events retained per topic.
        """
        self.topics: dict[str, deque[StreamEvent]] = {}
        self._filters: dict[str, list[FilterFn]] = {}
        self._aggregators: dict[str, AggregatorFn] = {}
        self._window_size_s = window_size_s
        self._buffer_size = buffer_size
        self._processed_count = 0
        logger.info("StreamProcessor initialised (window={}s)", window_size_s)

    def register_topic(
        self,
        topic: str,
        filter_fn: FilterFn | None = None,
        aggregator_fn: AggregatorFn | None = None,
    ) -> None:
        """Register a new event topic.

        Args:
            topic: Topic name.
            filter_fn: Optional filter; events returning False are discarded.
            aggregator_fn: Optional aggregation function for window results.

        Raises:
            ValueError: If ``topic`` is already registered.
        """
        if topic in self.topics:
            raise ValueError(f"Topic '{topic}' already registered")

        self.topics[topic] = deque(maxlen=self._buffer_size)
        self._filters[topic] = [filter_fn] if filter_fn else []
        self._aggregators[topic] = aggregator_fn or self._default_aggregator
        logger.debug("Topic '{}' registered", topic)

    def add_filter(self, topic: str, filter_fn: FilterFn) -> None:
        """Add a filter function to an existing topic.

        Args:
            topic: Target topic.
            filter_fn: Filter function to append.

        Raises:
            KeyError: If topic is not registered.
        """
        if topic not in self.topics:
            raise KeyError(f"Topic '{topic}' not registered")
        self._filters[topic].append(filter_fn)

    async def process_event(self, event: StreamEvent) -> bool:
        """Process a single event through the filter chain.

        Args:
            event: Incoming stream event.

        Returns:
            ``True`` if the event passed all filters and was buffered.
        """
        await asyncio.sleep(0)

        if event.topic not in self.topics:
            logger.debug("Unknown topic '{}', dropping event", event.topic)
            return False

        for f in self._filters.get(event.topic, []):
            if not f(event):
                logger.debug("Event '{}' filtered out", event.event_id)
                return False

        self.topics[event.topic].append(event)
        self._processed_count += 1
        return True

    async def process_batch(self, events: list[StreamEvent]) -> int:
        """Process a batch of events asynchronously.

        Args:
            events: List of stream events.

        Returns:
            Number of events that passed filters.
        """
        results = await asyncio.gather(*[self.process_event(e) for e in events])
        accepted = sum(1 for r in results if r)
        logger.debug("Batch: {}/{} events accepted", accepted, len(events))
        return accepted

    def tumbling_window(
        self,
        topic: str,
        window_size_s: float | None = None,
    ) -> WindowResult:
        """Compute a tumbling window aggregation for a topic.

        Args:
            topic: Topic to aggregate.
            window_size_s: Window duration override.

        Returns:
            :class:`WindowResult` with aggregated values.

        Raises:
            KeyError: If topic is not registered.
        """
        if topic not in self.topics:
            raise KeyError(f"Topic '{topic}' not registered")

        ws = window_size_s or self._window_size_s
        now = time.monotonic()
        window_start = now - ws

        events_in_window = [e for e in self.topics[topic] if e.timestamp >= window_start]
        aggregations = self._aggregators[topic](events_in_window)

        return WindowResult(
            topic=topic,
            window_start=window_start,
            window_end=now,
            n_events=len(events_in_window),
            aggregations=aggregations,
        )

    @staticmethod
    def _default_aggregator(events: list[StreamEvent]) -> dict[str, Any]:
        """Default aggregator: count and collect unique partition keys.

        Args:
            events: Events in the window.

        Returns:
            Aggregation dictionary.
        """
        return {
            "count": len(events),
            "unique_partitions": len({e.partition_key for e in events}),
        }

    @property
    def total_processed(self) -> int:
        """Total number of events processed (including filtered)."""
        return self._processed_count
