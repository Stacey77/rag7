"""Trading activity log with PnL tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class TradeDirection(Enum):
    """Trade direction."""

    BUY = auto()
    SELL = auto()


class TradeStatus(Enum):
    """Settlement status of a trade."""

    PENDING = auto()
    FILLED = auto()
    PARTIALLY_FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()


@dataclass
class TradeRecord:
    """A single trade activity record.

    Attributes:
        trade_id: Unique trade identifier.
        symbol: Instrument symbol.
        direction: BUY or SELL.
        quantity: Number of units traded.
        price: Execution price.
        status: Settlement status.
        strategy_id: Owning strategy identifier.
        account_id: Trading account identifier.
        commission: Brokerage commission in base currency.
        slippage: Slippage in price units.
        executed_at: UTC execution timestamp.
        notes: Optional free-text notes.
    """

    trade_id: str
    symbol: str
    direction: TradeDirection
    quantity: float
    price: float
    status: TradeStatus
    strategy_id: str = ""
    account_id: str = ""
    commission: float = 0.0
    slippage: float = 0.0
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""

    @property
    def notional_value(self) -> float:
        """Notional trade value (quantity × price)."""
        return self.quantity * self.price

    @property
    def net_cost(self) -> float:
        """Net cost including commission."""
        sign = 1.0 if self.direction == TradeDirection.BUY else -1.0
        return sign * self.notional_value + self.commission


@dataclass
class PnLSnapshot:
    """Profit and loss snapshot at a point in time.

    Attributes:
        account_id: Account identifier.
        realised_pnl: Realised P&L for closed positions.
        unrealised_pnl: Unrealised P&L on open positions.
        total_pnl: Sum of realised and unrealised.
        trade_count: Number of trades contributing.
        commission_total: Total commission paid.
        snapshot_at: UTC timestamp.
    """

    account_id: str
    realised_pnl: float
    unrealised_pnl: float
    total_pnl: float
    trade_count: int
    commission_total: float
    snapshot_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TradeLogger:
    """Trading activity log with P&L tracking and position management.

    Records all trade executions and computes realised/unrealised P&L
    using a FIFO position model.

    Attributes:
        trades: All trade records keyed by trade_id.
        _positions: Current open positions per account/symbol (FIFO queue).
        _realised_pnl: Cumulative realised P&L per account.
        _commission_totals: Cumulative commissions per account.
    """

    def __init__(self) -> None:
        """Initialise the trade logger."""
        self.trades: dict[str, TradeRecord] = {}
        self._positions: dict[str, list[dict[str, float]]] = {}
        self._realised_pnl: dict[str, float] = {}
        self._commission_totals: dict[str, float] = {}
        self._trade_counter = 0
        logger.info("TradeLogger initialised")

    def log_trade(
        self,
        symbol: str,
        direction: TradeDirection,
        quantity: float,
        price: float,
        status: TradeStatus = TradeStatus.FILLED,
        strategy_id: str = "",
        account_id: str = "default",
        commission: float = 0.0,
        slippage: float = 0.0,
        notes: str = "",
    ) -> TradeRecord:
        """Record a trade execution.

        Args:
            symbol: Instrument symbol.
            direction: BUY or SELL.
            quantity: Units traded.
            price: Execution price.
            status: Trade settlement status.
            strategy_id: Owning strategy.
            account_id: Trading account.
            commission: Brokerage commission.
            slippage: Execution slippage.
            notes: Optional notes.

        Returns:
            The created :class:`TradeRecord`.

        Raises:
            ValueError: If ``quantity`` or ``price`` are non-positive.
        """
        if quantity <= 0:
            raise ValueError(f"quantity must be positive, got {quantity}")
        if price <= 0:
            raise ValueError(f"price must be positive, got {price}")

        self._trade_counter += 1
        trade_id = f"TRADE-{self._trade_counter:010d}"
        record = TradeRecord(
            trade_id=trade_id,
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            price=price,
            status=status,
            strategy_id=strategy_id,
            account_id=account_id,
            commission=commission,
            slippage=slippage,
            notes=notes,
        )
        self.trades[trade_id] = record

        if status == TradeStatus.FILLED:
            self._update_position(record)

        self._commission_totals[account_id] = (
            self._commission_totals.get(account_id, 0.0) + commission
        )
        logger.info(
            "Trade {}: {} {} {} @ {:.4f} (account={})",
            trade_id,
            direction.name,
            quantity,
            symbol,
            price,
            account_id,
        )
        return record

    def _update_position(self, trade: TradeRecord) -> None:
        """Update FIFO position model with a new fill.

        Args:
            trade: Filled trade record.
        """
        key = f"{trade.account_id}:{trade.symbol}"
        if key not in self._positions:
            self._positions[key] = []

        if trade.direction == TradeDirection.BUY:
            self._positions[key].append({"qty": trade.quantity, "cost": trade.price})
        else:
            qty_to_close = trade.quantity
            realised = 0.0
            while qty_to_close > 0 and self._positions[key]:
                lot = self._positions[key][0]
                fill = min(lot["qty"], qty_to_close)
                realised += fill * (trade.price - lot["cost"])
                lot["qty"] -= fill
                qty_to_close -= fill
                if lot["qty"] <= 1e-10:
                    self._positions[key].pop(0)

            account = trade.account_id
            self._realised_pnl[account] = self._realised_pnl.get(account, 0.0) + realised

    def pnl_snapshot(
        self,
        account_id: str = "default",
        current_prices: dict[str, float] | None = None,
    ) -> PnLSnapshot:
        """Compute a P&L snapshot for an account.

        Args:
            account_id: Account to snapshot.
            current_prices: Current mark-to-market prices per symbol.

        Returns:
            :class:`PnLSnapshot` with realised and unrealised P&L.
        """
        realised = self._realised_pnl.get(account_id, 0.0)
        commission_total = self._commission_totals.get(account_id, 0.0)
        unrealised = 0.0

        if current_prices:
            for key, lots in self._positions.items():
                acc, symbol = key.split(":", 1)
                if acc != account_id:
                    continue
                current = current_prices.get(symbol)
                if current is not None:
                    for lot in lots:
                        unrealised += lot["qty"] * (current - lot["cost"])

        trade_count = sum(
            1 for t in self.trades.values()
            if t.account_id == account_id and t.status == TradeStatus.FILLED
        )

        return PnLSnapshot(
            account_id=account_id,
            realised_pnl=round(realised, 4),
            unrealised_pnl=round(unrealised, 4),
            total_pnl=round(realised + unrealised, 4),
            trade_count=trade_count,
            commission_total=round(commission_total, 4),
        )

    def get_trades(
        self,
        account_id: str | None = None,
        symbol: str | None = None,
        strategy_id: str | None = None,
    ) -> list[TradeRecord]:
        """Retrieve filtered trade records.

        Args:
            account_id: Filter by account.
            symbol: Filter by symbol.
            strategy_id: Filter by strategy.

        Returns:
            Matching :class:`TradeRecord` list (most recent first).
        """
        results = [
            t for t in self.trades.values()
            if (account_id is None or t.account_id == account_id)
            and (symbol is None or t.symbol == symbol)
            and (strategy_id is None or t.strategy_id == strategy_id)
        ]
        return sorted(results, key=lambda t: t.executed_at, reverse=True)
