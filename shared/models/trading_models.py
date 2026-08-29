"""Pydantic models for trading operations.

Provides:

* :class:`Side` – BUY / SELL enum.
* :class:`OrderType` – MARKET, LIMIT, STOP, etc.
* :class:`OrderStatus` – full order lifecycle states.
* :class:`TimeInForce` – GTC, IOC, FOK, GTD.
* :class:`Order` – order request and state model.
* :class:`Fill` – individual execution / trade fill.
* :class:`Position` – open position for one instrument.
* :class:`Portfolio` – aggregate portfolio view.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator


PositiveDecimal = Annotated[Decimal, Field(gt=Decimal("0"))]
NonNegativeDecimal = Annotated[Decimal, Field(ge=Decimal("0"))]


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class Side(str, Enum):
    """Order side."""

    BUY = "BUY"
    SELL = "SELL"

    @property
    def opposite(self) -> "Side":
        """Return the opposite side."""
        return Side.SELL if self is Side.BUY else Side.BUY


class OrderType(str, Enum):
    """Order execution type."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"
    STOP_LIMIT = "STOP_LIMIT"
    TAKE_PROFIT = "TAKE_PROFIT"
    TAKE_PROFIT_LIMIT = "TAKE_PROFIT_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderStatus(str, Enum):
    """Order lifecycle state."""

    PENDING = "PENDING"          # Created locally, not yet sent to exchange.
    SUBMITTED = "SUBMITTED"      # Sent to exchange, awaiting acknowledgement.
    ACCEPTED = "ACCEPTED"        # Acknowledged by exchange.
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

    @property
    def is_terminal(self) -> bool:
        """``True`` for states that cannot transition further."""
        return self in {
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        }

    @property
    def is_active(self) -> bool:
        """``True`` when the order is alive on the exchange."""
        return self in {
            OrderStatus.SUBMITTED,
            OrderStatus.ACCEPTED,
            OrderStatus.PARTIALLY_FILLED,
        }


class TimeInForce(str, Enum):
    """Order time-in-force policy."""

    GTC = "GTC"   # Good Till Cancelled
    IOC = "IOC"   # Immediate Or Cancel
    FOK = "FOK"   # Fill Or Kill
    GTD = "GTD"   # Good Till Date


# ---------------------------------------------------------------------------
# Shared config
# ---------------------------------------------------------------------------


class _BaseTradeModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=False,
        json_encoders={Decimal: str, datetime: lambda v: v.isoformat()},
    )


# ---------------------------------------------------------------------------
# Fill
# ---------------------------------------------------------------------------


class Fill(_BaseTradeModel):
    """A single execution / trade fill for an order.

    Args:
        fill_id: Unique fill identifier.
        order_id: Parent order identifier.
        symbol: Instrument symbol.
        side: Execution side.
        price: Fill execution price.
        quantity: Fill executed quantity.
        commission: Commission charged for this fill.
        commission_asset: Asset used to pay the commission.
        timestamp: Fill timestamp (UTC-aware).
        trade_id: Exchange trade identifier.
    """

    fill_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = Field(..., min_length=1)
    symbol: str = Field(..., min_length=1)
    side: Side
    price: PositiveDecimal
    quantity: PositiveDecimal
    commission: NonNegativeDecimal = Decimal("0")
    commission_asset: str = "USDT"
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    trade_id: str | None = None

    @property
    def notional(self) -> Decimal:
        """Fill notional value (price × quantity)."""
        return self.price * self.quantity


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------


class Order(_BaseTradeModel):
    """Represents a trading order through its full lifecycle.

    Args:
        order_id: Client-generated unique order ID.
        exchange_order_id: Exchange-assigned order ID (set after acceptance).
        symbol: Instrument symbol.
        side: BUY or SELL.
        order_type: Execution type.
        quantity: Requested quantity.
        price: Limit price (required for LIMIT / STOP_LIMIT orders).
        stop_price: Stop trigger price.
        time_in_force: Order duration policy.
        status: Current order lifecycle state.
        filled_quantity: Cumulative executed quantity.
        average_fill_price: Volume-weighted average fill price.
        fills: List of individual fills.
        created_at: Order creation timestamp.
        updated_at: Last state-change timestamp.
        strategy_id: Identifier of the strategy that placed this order.
        tags: Arbitrary metadata tags.
    """

    order_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    exchange_order_id: str | None = None
    symbol: str = Field(..., min_length=1)
    side: Side
    order_type: OrderType
    quantity: PositiveDecimal
    price: PositiveDecimal | None = None
    stop_price: PositiveDecimal | None = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: NonNegativeDecimal = Decimal("0")
    average_fill_price: NonNegativeDecimal | None = None
    fills: list[Fill] = Field(default_factory=list)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    strategy_id: str | None = None
    tags: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _validate_price_requirements(self) -> "Order":
        """Ensure limit/stop orders carry the appropriate price fields."""
        if self.order_type in {OrderType.LIMIT, OrderType.STOP_LIMIT}:
            if self.price is None:
                raise ValueError(
                    f"{self.order_type.value} orders require a limit price."
                )
        if self.order_type in {
            OrderType.STOP_MARKET,
            OrderType.STOP_LIMIT,
            OrderType.TAKE_PROFIT,
            OrderType.TAKE_PROFIT_LIMIT,
        }:
            if self.stop_price is None:
                raise ValueError(
                    f"{self.order_type.value} orders require a stop_price."
                )
        return self

    @property
    def remaining_quantity(self) -> Decimal:
        """Quantity not yet filled."""
        return self.quantity - self.filled_quantity

    @property
    def fill_ratio(self) -> Decimal:
        """Proportion of the order that has been filled (0–1)."""
        return self.filled_quantity / self.quantity

    @property
    def is_complete(self) -> bool:
        """``True`` when the order is in a terminal state."""
        return self.status.is_terminal

    def apply_fill(self, fill: Fill) -> "Order":
        """Return a new Order with the fill applied.

        Args:
            fill: The fill to apply.

        Returns:
            A new immutable Order instance with updated fill state.

        Raises:
            ValueError: If the fill would exceed the order quantity.
        """
        new_filled = self.filled_quantity + fill.quantity
        if new_filled > self.quantity:
            raise ValueError(
                f"Fill quantity {fill.quantity} would exceed order quantity "
                f"{self.quantity} (already filled: {self.filled_quantity})"
            )

        # Compute new VWAP
        if self.average_fill_price and self.filled_quantity > 0:
            total_notional = (
                self.average_fill_price * self.filled_quantity
                + fill.price * fill.quantity
            )
            new_vwap = total_notional / new_filled
        else:
            new_vwap = fill.price

        new_status = (
            OrderStatus.FILLED
            if new_filled == self.quantity
            else OrderStatus.PARTIALLY_FILLED
        )

        return self.model_copy(
            update={
                "fills": [*self.fills, fill],
                "filled_quantity": new_filled,
                "average_fill_price": new_vwap,
                "status": new_status,
                "updated_at": datetime.now(tz=timezone.utc),
            }
        )


# ---------------------------------------------------------------------------
# Position
# ---------------------------------------------------------------------------


class Position(_BaseTradeModel):
    """Open position in a single instrument.

    Args:
        symbol: Instrument symbol.
        side: Net position side (BUY = long, SELL = short).
        quantity: Absolute open quantity.
        average_entry_price: Volume-weighted average entry price.
        unrealised_pnl: Mark-to-market unrealised P&L.
        realised_pnl: Realised P&L from closed sub-positions.
        notional: Current mark-to-market notional value.
        opened_at: Position open timestamp.
        updated_at: Last update timestamp.
        strategy_id: Identifier of the owning strategy.
    """

    symbol: str = Field(..., min_length=1)
    side: Side
    quantity: PositiveDecimal
    average_entry_price: PositiveDecimal
    unrealised_pnl: Decimal = Decimal("0")
    realised_pnl: Decimal = Decimal("0")
    notional: NonNegativeDecimal = Decimal("0")
    opened_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    strategy_id: str | None = None

    def mark_to_market(self, mark_price: Decimal) -> "Position":
        """Return a new Position with unrealised P&L and notional updated.

        Args:
            mark_price: Current market price used for marking.

        Returns:
            Updated Position (immutable copy).
        """
        notional = mark_price * self.quantity
        sign = Decimal("1") if self.side is Side.BUY else Decimal("-1")
        upnl = sign * (mark_price - self.average_entry_price) * self.quantity
        return self.model_copy(
            update={
                "unrealised_pnl": upnl,
                "notional": notional,
                "updated_at": datetime.now(tz=timezone.utc),
            }
        )


# ---------------------------------------------------------------------------
# Portfolio
# ---------------------------------------------------------------------------


class Portfolio(_BaseTradeModel):
    """Aggregate portfolio view across all open positions.

    Args:
        portfolio_id: Unique portfolio identifier.
        account_id: Owning account / sub-account identifier.
        positions: Map of symbol → Position.
        cash_balance: Available cash in quote currency.
        total_equity: Total equity (cash + mark-to-market position values).
        total_unrealised_pnl: Sum of unrealised P&L across all positions.
        total_realised_pnl: Sum of realised P&L across all positions.
        peak_equity: Highest recorded equity (used for drawdown calculation).
        updated_at: Last update timestamp.
    """

    portfolio_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    account_id: str = Field(..., min_length=1)
    positions: dict[str, Position] = Field(default_factory=dict)
    cash_balance: NonNegativeDecimal = Decimal("0")
    total_equity: NonNegativeDecimal = Decimal("0")
    total_unrealised_pnl: Decimal = Decimal("0")
    total_realised_pnl: Decimal = Decimal("0")
    peak_equity: NonNegativeDecimal = Decimal("0")
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    @property
    def current_drawdown_pct(self) -> Decimal:
        """Current drawdown from peak equity as a percentage.

        Returns:
            Drawdown percentage (0 = at peak, 100 = total loss).
        """
        if self.peak_equity == Decimal("0"):
            return Decimal("0")
        return (
            (self.peak_equity - self.total_equity) / self.peak_equity * Decimal("100")
        )

    @property
    def open_symbol_count(self) -> int:
        """Number of symbols with open positions."""
        return len(self.positions)

    def get_position(self, symbol: str) -> Position | None:
        """Retrieve a position by symbol.

        Args:
            symbol: Instrument symbol.

        Returns:
            The position, or *None* if no open position exists.
        """
        return self.positions.get(symbol)
