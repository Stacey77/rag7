"""Pydantic models for market data.

Provides strongly-typed, validated models for:

* :class:`OHLCV` – candlestick / bar data.
* :class:`Ticker` – best-bid/ask snapshot.
* :class:`OrderBook` – full depth-of-market snapshot.
* :class:`Trade` – individual executed trade.
* :class:`MarketSnapshot` – composite snapshot combining all of the above.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PositiveDecimal = Annotated[Decimal, Field(gt=Decimal("0"))]
NonNegativeDecimal = Annotated[Decimal, Field(ge=Decimal("0"))]


class _BaseMarketModel(BaseModel):
    """Shared configuration for all market-data models."""

    model_config = ConfigDict(
        frozen=True,           # immutable after creation
        populate_by_name=True,
        use_enum_values=True,
        json_encoders={Decimal: str, datetime: lambda v: v.isoformat()},
    )


# ---------------------------------------------------------------------------
# OHLCV
# ---------------------------------------------------------------------------


class OHLCV(_BaseMarketModel):
    """Open-High-Low-Close-Volume candlestick bar.

    Args:
        symbol: Trading pair or instrument symbol (e.g. ``"BTCUSDT"``).
        open_time: Bar open time (UTC-aware).
        close_time: Bar close time (UTC-aware).
        open: Opening price.
        high: Highest price in the interval.
        low: Lowest price in the interval.
        close: Closing price.
        volume: Base-asset volume traded in the interval.
        quote_volume: Quote-asset volume traded in the interval.
        trades: Number of individual trades in the interval.
        interval: Bar duration string (e.g. ``"1m"``, ``"1h"``).
    """

    symbol: str = Field(..., min_length=1, description="Trading pair symbol.")
    open_time: datetime = Field(..., description="Bar open timestamp (UTC).")
    close_time: datetime = Field(..., description="Bar close timestamp (UTC).")
    open: PositiveDecimal = Field(..., description="Opening price.")
    high: PositiveDecimal = Field(..., description="Highest price.")
    low: PositiveDecimal = Field(..., description="Lowest price.")
    close: PositiveDecimal = Field(..., description="Closing price.")
    volume: NonNegativeDecimal = Field(..., description="Base-asset volume.")
    quote_volume: NonNegativeDecimal = Field(
        Decimal("0"), description="Quote-asset volume."
    )
    trades: int = Field(0, ge=0, description="Number of trades in the bar.")
    interval: str = Field("1m", description="Bar interval string.")

    @model_validator(mode="after")
    def _validate_hl(self) -> "OHLCV":
        """Ensure high >= low and both bound open/close."""
        if self.high < self.low:
            raise ValueError(f"high ({self.high}) must be >= low ({self.low})")
        if self.high < max(self.open, self.close):
            raise ValueError("high must be >= max(open, close)")
        if self.low > min(self.open, self.close):
            raise ValueError("low must be <= min(open, close)")
        return self

    @field_validator("open_time", "close_time", mode="before")
    @classmethod
    def _ensure_utc(cls, v: datetime) -> datetime:
        """Attach UTC timezone if the datetime is naive."""
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v

    @property
    def midpoint(self) -> Decimal:
        """Mid-price of high and low."""
        return (self.high + self.low) / Decimal("2")

    @property
    def range(self) -> Decimal:
        """Price range of the bar (high − low)."""
        return self.high - self.low


# ---------------------------------------------------------------------------
# Ticker
# ---------------------------------------------------------------------------


class Ticker(_BaseMarketModel):
    """Best bid/ask snapshot for an instrument.

    Args:
        symbol: Instrument symbol.
        bid: Best bid price.
        ask: Best ask price.
        bid_qty: Quantity available at the best bid.
        ask_qty: Quantity available at the best ask.
        last: Last traded price.
        last_qty: Quantity of the last trade.
        timestamp: Time of the snapshot (UTC-aware).
    """

    symbol: str = Field(..., min_length=1)
    bid: PositiveDecimal
    ask: PositiveDecimal
    bid_qty: NonNegativeDecimal = Decimal("0")
    ask_qty: NonNegativeDecimal = Decimal("0")
    last: PositiveDecimal | None = None
    last_qty: NonNegativeDecimal | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    @model_validator(mode="after")
    def _validate_spread(self) -> "Ticker":
        """Ensure ask >= bid (non-negative spread)."""
        if self.ask < self.bid:
            raise ValueError(
                f"ask ({self.ask}) must be >= bid ({self.bid})"
            )
        return self

    @property
    def spread(self) -> Decimal:
        """Absolute bid-ask spread."""
        return self.ask - self.bid

    @property
    def mid_price(self) -> Decimal:
        """Mid-price between best bid and ask."""
        return (self.bid + self.ask) / Decimal("2")


# ---------------------------------------------------------------------------
# Order Book
# ---------------------------------------------------------------------------


class OrderBookLevel(_BaseMarketModel):
    """A single price-level in the order book.

    Args:
        price: Price of the level.
        quantity: Total quantity resting at this price.
    """

    price: PositiveDecimal
    quantity: NonNegativeDecimal


class OrderBook(_BaseMarketModel):
    """Full order-book depth snapshot.

    Args:
        symbol: Instrument symbol.
        bids: List of bid levels ordered best-to-worst (descending price).
        asks: List of ask levels ordered best-to-worst (ascending price).
        timestamp: Snapshot capture time (UTC-aware).
        last_update_id: Exchange sequence number for this snapshot.
    """

    symbol: str = Field(..., min_length=1)
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    last_update_id: int | None = None

    @property
    def best_bid(self) -> OrderBookLevel | None:
        """Best (highest) bid level, or *None* if empty."""
        return self.bids[0] if self.bids else None

    @property
    def best_ask(self) -> OrderBookLevel | None:
        """Best (lowest) ask level, or *None* if empty."""
        return self.asks[0] if self.asks else None

    @property
    def mid_price(self) -> Decimal | None:
        """Mid-price, or *None* if either side is empty."""
        if self.best_bid and self.best_ask:
            return (self.best_bid.price + self.best_ask.price) / Decimal("2")
        return None

    def bid_liquidity(self, depth: int = 5) -> Decimal:
        """Total quantity available in the top *depth* bid levels.

        Args:
            depth: Number of levels to sum.

        Returns:
            Total bid quantity.
        """
        return sum(
            (lvl.quantity for lvl in self.bids[:depth]), start=Decimal("0")
        )

    def ask_liquidity(self, depth: int = 5) -> Decimal:
        """Total quantity available in the top *depth* ask levels.

        Args:
            depth: Number of levels to sum.

        Returns:
            Total ask quantity.
        """
        return sum(
            (lvl.quantity for lvl in self.asks[:depth]), start=Decimal("0")
        )


# ---------------------------------------------------------------------------
# Trade
# ---------------------------------------------------------------------------


class Trade(_BaseMarketModel):
    """Single executed trade (tape print).

    Args:
        trade_id: Exchange-assigned trade identifier.
        symbol: Instrument symbol.
        price: Execution price.
        quantity: Executed quantity.
        is_buyer_maker: ``True`` when the buy side is the passive (maker) side.
        timestamp: Trade execution time (UTC-aware).
        buyer_order_id: Optional buy-side order ID.
        seller_order_id: Optional sell-side order ID.
    """

    trade_id: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    price: PositiveDecimal
    quantity: PositiveDecimal
    is_buyer_maker: bool = False
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    buyer_order_id: str | None = None
    seller_order_id: str | None = None

    @property
    def notional(self) -> Decimal:
        """Trade notional value (price × quantity)."""
        return self.price * self.quantity


# ---------------------------------------------------------------------------
# Market Snapshot
# ---------------------------------------------------------------------------


class MarketSnapshot(_BaseMarketModel):
    """Composite market snapshot combining ticker, book, and recent trades.

    Args:
        symbol: Instrument symbol.
        ticker: Current ticker snapshot.
        order_book: Current order-book depth.
        recent_trades: Latest trade prints (oldest first).
        latest_candle: Most recently closed OHLCV bar.
        timestamp: Snapshot assembly time (UTC-aware).
    """

    symbol: str = Field(..., min_length=1)
    ticker: Ticker | None = None
    order_book: OrderBook | None = None
    recent_trades: list[Trade] = Field(default_factory=list)
    latest_candle: OHLCV | None = None
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    @property
    def is_complete(self) -> bool:
        """``True`` when all four data components are present."""
        return all(
            [self.ticker, self.order_book, self.recent_trades, self.latest_candle]
        )
