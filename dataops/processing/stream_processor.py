"""Kafka stream processor using aiokafka.

Provides a high-level publish / subscribe interface over Kafka topics with
automatic reconnect logic and per-topic handler dispatch.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Callable, Dict, List, Optional

from loguru import logger

from shared.common.exceptions import DataIngestionError


class StreamProcessor:
    """Async Kafka producer + consumer wrapper.

    Args:
        bootstrap_servers: Comma-separated list of Kafka broker addresses.
        group_id: Consumer group ID (default ``"agi-trading"``)
        auto_offset_reset: Where to start reading if no committed offset
            exists (``"earliest"`` or ``"latest"``).
    """

    _MAX_BACKOFF = 60.0

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        group_id: str = "agi-trading",
        auto_offset_reset: str = "latest",
    ) -> None:
        self._servers = bootstrap_servers
        self._group_id = group_id
        self._auto_offset_reset = auto_offset_reset
        self._producer = None
        self._consumer = None
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._consumer_task: Optional[asyncio.Task] = None  # type: ignore[type-arg]
        self._log = logger.bind(component="stream_processor")

    # ── Lifecycle ──────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start the Kafka producer and launch the consumer loop."""
        try:
            from aiokafka import AIOKafkaProducer  # type: ignore[import]

            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._servers,
                value_serializer=lambda v: json.dumps(v).encode(),
            )
            await self._producer.start()
            self._running = True
            self._consumer_task = asyncio.create_task(self._consume_loop())
            self._log.info("StreamProcessor started", servers=self._servers)
        except ImportError as exc:
            raise DataIngestionError(
                "aiokafka package required: pip install aiokafka"
            ) from exc
        except Exception as exc:
            raise DataIngestionError(f"Failed to start StreamProcessor: {exc}") from exc

    async def stop(self) -> None:
        """Gracefully stop the producer and consumer."""
        self._running = False
        if self._consumer_task:
            self._consumer_task.cancel()
            await asyncio.gather(self._consumer_task, return_exceptions=True)
        if self._consumer:
            await self._consumer.stop()
        if self._producer:
            await self._producer.stop()
        self._log.info("StreamProcessor stopped")

    # ── Producer ──────────────────────────────────────────────────────────

    async def publish(self, topic: str, message: dict) -> None:
        """Publish a message to a Kafka topic.

        Args:
            topic: Target Kafka topic.
            message: JSON-serialisable message payload.

        Raises:
            DataIngestionError: If the producer is not started or send fails.
        """
        if not self._producer:
            raise DataIngestionError("StreamProcessor not started. Call start() first.")
        try:
            await self._producer.send_and_wait(topic, message)
            self._log.debug("Message published", topic=topic)
        except Exception as exc:
            self._log.error("Failed to publish message", topic=topic, error=str(exc))
            raise DataIngestionError(f"Kafka publish failed: {exc}") from exc

    # ── Consumer ──────────────────────────────────────────────────────────

    def subscribe(self, topic: str, handler: Callable[[str, dict], Any]) -> None:
        """Register a handler for messages on *topic*.

        The handler receives ``(topic: str, message: dict)`` and may be an
        ordinary function or a coroutine.

        Args:
            topic: Kafka topic to subscribe to.
            handler: Callable invoked for each message on the topic.
        """
        self._handlers.setdefault(topic, []).append(handler)
        self._log.info("Handler registered", topic=topic)

    async def _consume_loop(self) -> None:
        """Internal loop that consumes all subscribed topics."""
        delay = 1.0
        while self._running:
            try:
                await self._run_consumer()
                delay = 1.0
            except asyncio.CancelledError:
                break
            except Exception as exc:
                if not self._running:
                    break
                self._log.error(
                    "Consumer error, reconnecting",
                    error=str(exc),
                    backoff_seconds=delay,
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._MAX_BACKOFF)

    async def _run_consumer(self) -> None:
        """Create a consumer, subscribe, and dispatch messages."""
        topics = list(self._handlers.keys())
        if not topics:
            # No topics subscribed; idle until cancelled
            await asyncio.sleep(5)
            return

        from aiokafka import AIOKafkaConsumer  # type: ignore[import]

        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self._servers,
            group_id=self._group_id,
            auto_offset_reset=self._auto_offset_reset,
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        self._consumer = consumer
        await consumer.start()
        self._log.info("Consumer started", topics=topics)
        try:
            async for record in consumer:
                if not self._running:
                    break
                topic = record.topic
                try:
                    payload = record.value
                except Exception:
                    continue
                for handler in self._handlers.get(topic, []):
                    try:
                        result = handler(topic, payload)
                        if asyncio.iscoroutine(result):
                            await result
                    except Exception as exc:
                        self._log.error(
                            "Handler error",
                            topic=topic,
                            handler=getattr(handler, "__name__", str(handler)),
                            error=str(exc),
                        )
        finally:
            await consumer.stop()
