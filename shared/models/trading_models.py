"""Pydantic trading domain models: orders, positions, and portfolios."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Side(str, Enum):
    """Order / position side."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order execution type."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderStatus(str, Enum):
    """Lifecycle status of an order."""

    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class TimeInForce(str, Enum):
    """Time-in-force policy for an order."""

    GTC = "GTC"  # Good Till Cancelled
    IOC = "IOC"  # Immediate Or Cancel
    FOK = "FOK"  # Fill Or Kill
    DAY = "DAY"  # Day order
    GTD = "GTD"  # Good Till Date


class Fill(BaseModel):
    """Represents a single execution / fill of an order."""

    fill_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str
    symbol: str
    side: Side
    quantity: Decimal = Field(gt=Decimal("0"))
    price: Decimal = Field(gt=Decimal("0"))
    commission: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {"frozen": True}


class Order(BaseModel):
    """Represents a trading order throughout its lifecycle."""

    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exchange_order_id: Optional[str] = None
    symbol: str
    side: Side
    order_type: OrderType
    quantity: Decimal = Field(gt=Decimal("0"))
    price: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    stop_price: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    average_fill_price: Optional[Decimal] = None
    fills: List[Fill] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    client_metadata: dict = Field(default_factory=dict)

    @field_validator("price")
    @classmethod
    def validate_limit_price(cls, v: Optional[Decimal], info: object) -> Optional[Decimal]:
        """Limit orders require a price."""
        return v

    @property
    def is_open(self) -> bool:
        """Return True if the order is still active."""
        return self.status in {
            OrderStatus.PENDING,
            OrderStatus.SUBMITTED,
            OrderStatus.ACCEPTED,
            OrderStatus.PARTIALLY_FILLED,
        }

    @property
    def remaining_quantity(self) -> Decimal:
        """Quantity not yet filled."""
        return self.quantity - self.filled_quantity

    @property
    def notional_value(self) -> Optional[Decimal]:
        """Notional value if price is known."""
        if self.price is not None:
            return self.quantity * self.price
        if self.average_fill_price is not None:
            return self.filled_quantity * self.average_fill_price
        return None


class Position(BaseModel):
    """Represents an open position in a single instrument."""

    symbol: str
    side: Side
    quantity: Decimal = Field(gt=Decimal("0"))
    average_entry_price: Decimal = Field(gt=Decimal("0"))
    current_price: Optional[Decimal] = Field(default=None, gt=Decimal("0"))
    unrealised_pnl: Decimal = Field(default=Decimal("0"))
    realised_pnl: Decimal = Field(default=Decimal("0"))
    opened_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def notional_value(self) -> Decimal:
        """Current notional value of the position."""
        price = self.current_price or self.average_entry_price
        return self.quantity * price

    @property
    def total_pnl(self) -> Decimal:
        """Sum of realised and unrealised P&L."""
        return self.realised_pnl + self.unrealised_pnl

    def calculate_unrealised_pnl(self, mark_price: Decimal) -> Decimal:
        """Compute unrealised P&L for a given mark price."""
        raw = (mark_price - self.average_entry_price) * self.quantity
        return raw if self.side is Side.BUY else -raw


class Portfolio(BaseModel):
    """Aggregate portfolio state across all positions."""

    portfolio_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str
    positions: dict[str, Position] = Field(default_factory=dict)
    cash_balance: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    total_equity: Decimal = Field(default=Decimal("0"))
    peak_equity: Decimal = Field(default=Decimal("0"))
    realised_pnl: Decimal = Field(default=Decimal("0"))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def drawdown_pct(self) -> float:
        """Current drawdown as a percentage of peak equity."""
        if self.peak_equity <= Decimal("0"):
            return 0.0
        dd = (self.peak_equity - self.total_equity) / self.peak_equity * 100
        return float(max(dd, Decimal("0")))

    @property
    def unrealised_pnl(self) -> Decimal:
        """Total unrealised P&L across all positions."""
        return sum((p.unrealised_pnl for p in self.positions.values()), Decimal("0"))
