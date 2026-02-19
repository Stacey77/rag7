"""Real-time data streaming with pub/sub and windowing."""
from __future__ import annotations

import logging
import queue
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class StreamEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    partition: int = 0
    offset: int = 0


@dataclass
class WindowResult:
    window_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    events: List[StreamEvent] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime = field(default_factory=datetime.utcnow)
    aggregates: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """Simple in-process pub/sub event bus."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = threading.Lock()

    def subscribe(self, topic: str, handler: Callable[[StreamEvent], None]) -> None:
        with self._lock:
            self._subscribers.setdefault(topic, []).append(handler)

    def publish(self, event: StreamEvent) -> int:
        handlers = self._subscribers.get(event.topic, [])
        with self._lock:
            handlers_copy = list(handlers)
        delivered = 0
        for handler in handlers_copy:
            try:
                handler(event)
                delivered += 1
            except Exception as exc:
                logger.warning("Handler error on topic '%s': %s", event.topic, exc)
        return delivered

    def unsubscribe(self, topic: str, handler: Callable) -> bool:
        with self._lock:
            subscribers = self._subscribers.get(topic, [])
            if handler in subscribers:
                subscribers.remove(handler)
                return True
        return False


class TumblingWindow:
    """Fixed-size tumbling window aggregator."""

    def __init__(self, window_size: int = 100, topic: str = "") -> None:
        self.window_size = window_size
        self.topic = topic
        self._buffer: List[StreamEvent] = []
        self._completed_windows: List[WindowResult] = []
        self._lock = threading.Lock()

    def add_event(self, event: StreamEvent) -> Optional[WindowResult]:
        with self._lock:
            self._buffer.append(event)
            if len(self._buffer) >= self.window_size:
                return self._flush()
        return None

    def _flush(self) -> WindowResult:
        events = self._buffer[:]
        self._buffer.clear()
        result = WindowResult(
            topic=self.topic,
            events=events,
            start_time=events[0].timestamp if events else datetime.utcnow(),
            end_time=events[-1].timestamp if events else datetime.utcnow(),
            aggregates=self._aggregate(events),
        )
        self._completed_windows.append(result)
        return result

    def _aggregate(self, events: List[StreamEvent]) -> Dict[str, Any]:
        numeric_fields: Dict[str, List[float]] = {}
        for event in events:
            for k, v in event.payload.items():
                if isinstance(v, (int, float)):
                    numeric_fields.setdefault(k, []).append(float(v))
        aggs: Dict[str, Any] = {"count": len(events)}
        import statistics
        for field_name, values in numeric_fields.items():
            aggs[f"{field_name}_mean"] = statistics.mean(values)
            aggs[f"{field_name}_sum"] = sum(values)
        return aggs

    def force_flush(self) -> Optional[WindowResult]:
        with self._lock:
            if self._buffer:
                return self._flush()
        return None


class StreamProducer:
    """Generates and publishes events to the bus."""

    def __init__(self, bus: EventBus) -> None:
        self._bus = bus
        self._offset_counter: Dict[str, int] = {}

    def publish(self, topic: str, payload: Dict[str, Any],
                partition: int = 0) -> StreamEvent:
        offset = self._offset_counter.get(topic, 0)
        event = StreamEvent(topic=topic, payload=payload,
                            partition=partition, offset=offset)
        self._offset_counter[topic] = offset + 1
        self._bus.publish(event)
        return event

    def publish_batch(self, topic: str,
                      payloads: List[Dict[str, Any]]) -> List[StreamEvent]:
        return [self.publish(topic, p) for p in payloads]


class StreamConsumer:
    """Consumes events from a topic with an optional processing queue."""

    def __init__(self, bus: EventBus, topics: List[str],
                 max_queue: int = 10000) -> None:
        self._bus = bus
        self._topics = topics
        self._queue: queue.Queue = queue.Queue(maxsize=max_queue)
        self._processed: int = 0
        for topic in topics:
            bus.subscribe(topic, self._enqueue)

    def _enqueue(self, event: StreamEvent) -> None:
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            logger.warning("Consumer queue full; dropping event on '%s'", event.topic)

    def poll(self, timeout: float = 0.1) -> Optional[StreamEvent]:
        try:
            event = self._queue.get(timeout=timeout)
            self._processed += 1
            return event
        except queue.Empty:
            return None

    def poll_batch(self, max_events: int = 100,
                   timeout: float = 0.1) -> List[StreamEvent]:
        events: List[StreamEvent] = []
        deadline = time.monotonic() + timeout
        while len(events) < max_events and time.monotonic() < deadline:
            event = self.poll(timeout=max(0, deadline - time.monotonic()))
            if event:
                events.append(event)
        return events

    @property
    def queue_depth(self) -> int:
        return self._queue.qsize()

    @property
    def processed_count(self) -> int:
        return self._processed


class StreamingPipeline:
    """
    End-to-end streaming pipeline with producer, consumer,
    windowing, and real-time aggregation.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._bus = EventBus()
        self._producer = StreamProducer(self._bus)
        self._windows: Dict[str, TumblingWindow] = {}
        self._processors: List[Callable[[StreamEvent], None]] = []
        logger.info("StreamingPipeline '%s' initialized", name)

    def add_window(self, topic: str, window_size: int = 100) -> TumblingWindow:
        window = TumblingWindow(window_size=window_size, topic=topic)
        self._windows[topic] = window
        self._bus.subscribe(topic, lambda e: window.add_event(e))
        return window

    def add_processor(self, topic: str,
                      func: Callable[[StreamEvent], None]) -> None:
        self._bus.subscribe(topic, func)

    def produce(self, topic: str, payload: Dict[str, Any]) -> StreamEvent:
        return self._producer.publish(topic, payload)

    def produce_batch(self, topic: str,
                      payloads: List[Dict[str, Any]]) -> List[StreamEvent]:
        return self._producer.publish_batch(topic, payloads)

    def create_consumer(self, topics: List[str]) -> StreamConsumer:
        return StreamConsumer(self._bus, topics)

    def flush_all_windows(self) -> List[WindowResult]:
        results: List[WindowResult] = []
        for window in self._windows.values():
            r = window.force_flush()
            if r:
                results.append(r)
        return results
