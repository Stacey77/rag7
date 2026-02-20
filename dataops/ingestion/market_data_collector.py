"""Real-time market data collector.

Subscribes to market data feeds via WebSocket, normalises the events into
shared models, and publishes them to a Redis pub/sub channel for downstream
consumers.  Reconnects automatically with exponential back-off on failure.
"""

from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from typing import Dict, List, Optional

from loguru import logger

from shared.common.exceptions import DataIngestionError
from shared.models.market_data import MarketSnapshot, Ticker


class MarketDataCollector:
    """Collects real-time market data and fans it out over Redis pub/sub.

    Args:
        redis_url: Redis connection URL (``redis://host:port/db``).
        ws_url: WebSocket feed base URL.
        channel_prefix: Redis pub/sub channel prefix (default ``"market."``)
    """

    _MAX_BACKOFF = 60.0  # seconds

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        ws_url: str = "wss://stream.data.alpaca.markets/v2/iex",
        channel_prefix: str = "market.",
    ) -> None:
        self._redis_url = redis_url
        self._ws_url = ws_url
        self._channel_prefix = channel_prefix
        self._symbols: List[str] = []
        self._latest: Dict[str, MarketSnapshot] = {}
        self._running = False
        self._tasks: List[asyncio.Task] = []  # type: ignore[type-arg]
        self._log = logger.bind(component="market_data_collector")

    # ── Public API ─────────────────────────────────────────────────────────

    async def start(self, symbols: List[str]) -> None:
        """Begin collecting market data for the given symbols.

        Opens a WebSocket connection and starts a background task that
        processes messages until :meth:`stop` is called.

        Args:
            symbols: List of instrument symbols, e.g. ``["BTCUSDT", "AAPL"]``.
        """
        if self._running:
            self._log.warning("Collector already running")
            return
        self._symbols = [s.upper() for s in symbols]
        self._running = True
        task = asyncio.create_task(self._run_with_backoff())
        self._tasks.append(task)
        self._log.info("Market data collector started", symbols=self._symbols)

    async def stop(self) -> None:
        """Gracefully stop all collection tasks."""
        self._running = False
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks.clear()
        self._log.info("Market data collector stopped")

    def get_latest(self, symbol: str) -> Optional[MarketSnapshot]:
        """Return the most-recently received snapshot for *symbol*.

        Args:
            symbol: Instrument symbol.

        Returns:
            The latest :class:`~shared.models.market_data.MarketSnapshot`,
            or ``None`` if no data has been received yet.
        """
        return self._latest.get(symbol.upper())

    # ── Internal helpers ───────────────────────────────────────────────────

    async def _run_with_backoff(self) -> None:
        """Main loop with exponential back-off on WebSocket errors."""
        delay = 1.0
        while self._running:
            try:
                await self._connect_and_stream()
                delay = 1.0  # Reset on clean disconnect
            except asyncio.CancelledError:
                break
            except Exception as exc:
                if not self._running:
                    break
                self._log.error(
                    "WebSocket error, reconnecting",
                    error=str(exc),
                    backoff_seconds=delay,
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._MAX_BACKOFF)

    async def _connect_and_stream(self) -> None:
        """Connect to the WebSocket feed and process incoming messages."""
        try:
            import websockets  # type: ignore[import]
        except ImportError as exc:
            raise DataIngestionError(
                "websockets package required: pip install websockets"
            ) from exc

        self._log.info("Connecting to WebSocket feed", url=self._ws_url)
        async with websockets.connect(self._ws_url) as ws:
            # Subscribe to tickers
            sub_msg = json.dumps(
                {"action": "subscribe", "quotes": self._symbols, "trades": self._symbols}
            )
            await ws.send(sub_msg)
            self._log.info("Subscribed to symbols", symbols=self._symbols)

            async for raw_msg in ws:
                if not self._running:
                    break
                try:
                    await self._handle_message(raw_msg)
                except Exception as exc:
                    self._log.warning("Error handling message", error=str(exc))

    async def _handle_message(self, raw: str) -> None:
        """Parse a raw WebSocket message and update internal state + Redis."""
        events = json.loads(raw)
        if not isinstance(events, list):
            events = [events]

        for event in events:
            msg_type = event.get("T", "")
            symbol = event.get("S", "")
            if not symbol:
                continue
            symbol = symbol.upper()

            if msg_type == "q":  # Quote
                ticker = Ticker(
                    symbol=symbol,
                    bid=Decimal(str(event.get("bp", "0"))) or None,
                    ask=Decimal(str(event.get("ap", "0"))) or None,
                )
                existing = self._latest.get(symbol) or MarketSnapshot(symbol=symbol)
                self._latest[symbol] = existing.model_copy(
                    update={"ticker": ticker}
                )
                await self._publish(symbol, {"type": "quote", "symbol": symbol})

            elif msg_type == "t":  # Trade
                existing = self._latest.get(symbol) or MarketSnapshot(symbol=symbol)
                self._latest[symbol] = existing.model_copy(update={})
                await self._publish(symbol, {"type": "trade", "symbol": symbol})

    async def _publish(self, symbol: str, payload: dict) -> None:
        """Publish a message to the Redis channel for *symbol*."""
        try:
            import redis.asyncio as aioredis  # type: ignore[import]

            async with aioredis.from_url(self._redis_url) as r:
                channel = f"{self._channel_prefix}{symbol}"
                await r.publish(channel, json.dumps(payload))
        except Exception as exc:
            self._log.warning("Failed to publish to Redis", symbol=symbol, error=str(exc))
