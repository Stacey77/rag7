"""TimescaleDB wrapper for time-series market data.

Uses ``asyncpg`` connection pooling for high-throughput inserts and
window-function queries.  The schema is created automatically on first
connection via :meth:`TimeSeriesDB.initialise`.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from loguru import logger

from shared.common.exceptions import StorageError
from shared.models.market_data import OHLCV, Trade

# ── DDL ──────────────────────────────────────────────────────────────────

_CREATE_OHLCV = """
CREATE TABLE IF NOT EXISTS ohlcv (
    time        TIMESTAMPTZ     NOT NULL,
    symbol      TEXT            NOT NULL,
    interval    TEXT            NOT NULL,
    open        NUMERIC(20, 8)  NOT NULL,
    high        NUMERIC(20, 8)  NOT NULL,
    low         NUMERIC(20, 8)  NOT NULL,
    close       NUMERIC(20, 8)  NOT NULL,
    volume      NUMERIC(30, 8)  NOT NULL,
    vwap        NUMERIC(20, 8),
    num_trades  INTEGER
);
"""

_CREATE_OHLCV_HYPERTABLE = """
SELECT create_hypertable('ohlcv', 'time', if_not_exists => TRUE);
"""

_CREATE_TRADES = """
CREATE TABLE IF NOT EXISTS trades (
    time            TIMESTAMPTZ     NOT NULL,
    trade_id        TEXT            NOT NULL,
    symbol          TEXT            NOT NULL,
    price           NUMERIC(20, 8)  NOT NULL,
    quantity        NUMERIC(30, 8)  NOT NULL,
    is_buyer_maker  BOOLEAN
);
"""

_CREATE_TRADES_HYPERTABLE = """
SELECT create_hypertable('trades', 'time', if_not_exists => TRUE);
"""


class TimeSeriesDB:
    """Async TimescaleDB client with connection pooling.

    Args:
        dsn: asyncpg-compatible PostgreSQL DSN.
        min_pool_size: Minimum connections in the pool (default 2).
        max_pool_size: Maximum connections in the pool (default 10).
    """

    def __init__(
        self,
        dsn: str,
        min_pool_size: int = 2,
        max_pool_size: int = 10,
    ) -> None:
        self._dsn = dsn
        self._min_pool = min_pool_size
        self._max_pool = max_pool_size
        self._pool = None
        self._log = logger.bind(component="time_series_db")

    async def initialise(self) -> None:
        """Create the connection pool and ensure the schema exists."""
        try:
            import asyncpg  # type: ignore[import]

            self._pool = await asyncpg.create_pool(
                dsn=self._dsn,
                min_size=self._min_pool,
                max_size=self._max_pool,
            )
            async with self._pool.acquire() as conn:
                await conn.execute(_CREATE_OHLCV)
                await conn.execute(_CREATE_TRADES)
                try:
                    await conn.execute(_CREATE_OHLCV_HYPERTABLE)
                    await conn.execute(_CREATE_TRADES_HYPERTABLE)
                except Exception:
                    # TimescaleDB extension may not be available in all environments
                    pass
            self._log.info("TimeSeriesDB initialised")
        except Exception as exc:
            raise StorageError(f"Failed to initialise TimeSeriesDB: {exc}") from exc

    async def close(self) -> None:
        """Close all pooled connections."""
        if self._pool:
            await self._pool.close()
            self._log.info("TimeSeriesDB connection pool closed")

    # ── OHLCV operations ───────────────────────────────────────────────────

    async def insert_ohlcv(self, bar: OHLCV) -> None:
        """Insert a single OHLCV bar.

        Args:
            bar: The bar to persist.

        Raises:
            StorageError: On database error.
        """
        if not self._pool:
            raise StorageError("Database not initialised. Call initialise() first.")
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO ohlcv
                        (time, symbol, interval, open, high, low, close, volume, vwap, num_trades)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT DO NOTHING
                    """,
                    bar.timestamp,
                    bar.symbol,
                    bar.interval,
                    bar.open,
                    bar.high,
                    bar.low,
                    bar.close,
                    bar.volume,
                    bar.vwap,
                    bar.num_trades,
                )
        except Exception as exc:
            raise StorageError(f"Failed to insert OHLCV bar: {exc}") from exc

    async def query_ohlcv(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "1m",
    ) -> List[OHLCV]:
        """Fetch OHLCV bars for a symbol in a time range.

        Args:
            symbol: Instrument symbol.
            start: Inclusive start of the time window.
            end: Inclusive end of the time window.
            interval: Bar interval (default ``"1m"``).

        Returns:
            Ordered list of :class:`~shared.models.market_data.OHLCV` bars.

        Raises:
            StorageError: On database error.
        """
        if not self._pool:
            raise StorageError("Database not initialised. Call initialise() first.")
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT time, symbol, interval, open, high, low, close, volume, vwap, num_trades
                    FROM ohlcv
                    WHERE symbol = $1
                      AND interval = $4
                      AND time BETWEEN $2 AND $3
                    ORDER BY time ASC
                    """,
                    symbol,
                    start,
                    end,
                    interval,
                )
            return [
                OHLCV(
                    symbol=r["symbol"],
                    timestamp=r["time"],
                    interval=r["interval"],
                    open=r["open"],
                    high=r["high"],
                    low=r["low"],
                    close=r["close"],
                    volume=r["volume"],
                    vwap=r["vwap"],
                    num_trades=r["num_trades"],
                )
                for r in rows
            ]
        except Exception as exc:
            raise StorageError(f"Failed to query OHLCV: {exc}") from exc

    # ── Trade operations ───────────────────────────────────────────────────

    async def insert_trade(self, trade: Trade) -> None:
        """Persist a single exchange trade.

        Args:
            trade: The trade to store.

        Raises:
            StorageError: On database error.
        """
        if not self._pool:
            raise StorageError("Database not initialised. Call initialise() first.")
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO trades (time, trade_id, symbol, price, quantity, is_buyer_maker)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT DO NOTHING
                    """,
                    trade.timestamp,
                    trade.trade_id,
                    trade.symbol,
                    trade.price,
                    trade.quantity,
                    trade.is_buyer_maker,
                )
        except Exception as exc:
            raise StorageError(f"Failed to insert trade: {exc}") from exc
