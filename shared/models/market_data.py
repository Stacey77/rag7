"""Pydantic market data models: OHLCV, order books, tickers, and trades."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    """A single OHLCV (candlestick) bar."""

    symbol: str
    timestamp: datetime
    open: Decimal = Field(gt=Decimal("0"))
    high: Decimal = Field(gt=Decimal("0"))
    low: Decimal = Field(gt=Decimal("0"))
    close: Decimal = Field(gt=Decimal("0"))
    volume: Decimal = Field(ge=Decimal("0"))
    interval: str = "1m"  # e.g. "1m", "5m", "1h", "1d"
    vwap: Optional[Decimal] = None
    num_trades: Optional[int] = None

    model_config = {"frozen": True}


class OrderBookLevel(BaseModel):
    """A single price level in an order book."""

    price: Decimal = Field(gt=Decimal("0"))
    quantity: Decimal = Field(ge=Decimal("0"))

    model_config = {"frozen": True}


class OrderBook(BaseModel):
    """Level-2 order book snapshot."""

    symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    bids: List[OrderBookLevel] = Field(default_factory=list)
    asks: List[OrderBookLevel] = Field(default_factory=list)
    sequence: Optional[int] = None

    @property
    def best_bid(self) -> Optional[Decimal]:
        """Highest bid price."""
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Optional[Decimal]:
        """Lowest ask price."""
        return self.asks[0].price if self.asks else None

    @property
    def mid_price(self) -> Optional[Decimal]:
        """Mid price between best bid and best ask."""
        if self.best_bid is not None and self.best_ask is not None:
            return (self.best_bid + self.best_ask) / Decimal("2")
        return None

    @property
    def spread(self) -> Optional[Decimal]:
        """Bid-ask spread."""
        if self.best_bid is not None and self.best_ask is not None:
            return self.best_ask - self.best_bid
        return None


class Ticker(BaseModel):
    """Real-time ticker / quote summary."""

    symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    bid: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    ask: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    last: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    volume_24h: Optional[Decimal] = None
    price_change_24h: Optional[Decimal] = None
    price_change_pct_24h: Optional[float] = None
    high_24h: Optional[Decimal] = None
    low_24h: Optional[Decimal] = None

    model_config = {"frozen": True}


class Trade(BaseModel):
    """A single executed trade on the exchange."""

    trade_id: str
    symbol: str
    timestamp: datetime
    price: Decimal = Field(gt=Decimal("0"))
    quantity: Decimal = Field(gt=Decimal("0"))
    is_buyer_maker: Optional[bool] = None

    model_config = {"frozen": True}


class MarketSnapshot(BaseModel):
    """Aggregated market snapshot for a single instrument."""

    symbol: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ticker: Optional[Ticker] = None
    order_book: Optional[OrderBook] = None
    last_bar: Optional[OHLCV] = None
    last_trade: Optional[Trade] = None
