"""In-process portfolio manager.

Tracks positions, cash, and P&L.  All mutations are protected by an
:class:`asyncio.Lock` so the manager is safe for concurrent async tasks.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, Optional

from loguru import logger

from shared.models.trading_models import Fill, Portfolio, Position, Side


class PortfolioManager:
    """Thread-safe portfolio state manager.

    Args:
        account_id: Unique identifier for the trading account.
        initial_cash: Starting cash balance in USD (default 0).
    """

    def __init__(
        self,
        account_id: str,
        initial_cash: Decimal = Decimal("0"),
    ) -> None:
        self._lock = asyncio.Lock()
        self._portfolio = Portfolio(
            account_id=account_id,
            cash_balance=initial_cash,
            total_equity=initial_cash,
            peak_equity=initial_cash,
        )
        self._log = logger.bind(component="portfolio_manager", account_id=account_id)

    # ── Read operations ────────────────────────────────────────────────────

    async def get_portfolio(self) -> Portfolio:
        """Return a snapshot of the current portfolio."""
        async with self._lock:
            return self._portfolio

    async def get_position(self, symbol: str) -> Optional[Position]:
        """Return the position for *symbol*, or ``None`` if flat.

        Args:
            symbol: Instrument symbol, e.g. ``"BTCUSDT"``.

        Returns:
            Current :class:`~shared.models.trading_models.Position` or ``None``.
        """
        async with self._lock:
            return self._portfolio.positions.get(symbol)

    # ── Write operations ───────────────────────────────────────────────────

    async def update_from_fill(self, fill: Fill) -> None:
        """Update portfolio state after a trade fill.

        Applies the fill to the matching position (opening, adding to,
        reducing, or closing it) and adjusts the cash balance.

        Args:
            fill: The completed :class:`~shared.models.trading_models.Fill`.
        """
        async with self._lock:
            positions = dict(self._portfolio.positions)
            cash = self._portfolio.cash_balance
            realised_pnl = self._portfolio.realised_pnl

            fill_value = fill.quantity * fill.price + fill.commission

            if fill.side is Side.BUY:
                cash -= fill_value
                existing = positions.get(fill.symbol)
                if existing is None:
                    positions[fill.symbol] = Position(
                        symbol=fill.symbol,
                        side=Side.BUY,
                        quantity=fill.quantity,
                        average_entry_price=fill.price,
                    )
                else:
                    # Average in the new fill
                    new_qty = existing.quantity + fill.quantity
                    new_avg = (
                        existing.average_entry_price * existing.quantity
                        + fill.price * fill.quantity
                    ) / new_qty
                    positions[fill.symbol] = existing.model_copy(
                        update={
                            "quantity": new_qty,
                            "average_entry_price": new_avg,
                            "updated_at": datetime.now(timezone.utc),
                        }
                    )
            else:  # SELL
                cash += fill_value
                existing = positions.get(fill.symbol)
                if existing is not None:
                    pnl = (fill.price - existing.average_entry_price) * fill.quantity
                    realised_pnl += pnl if existing.side is Side.BUY else -pnl
                    new_qty = existing.quantity - fill.quantity
                    if new_qty <= Decimal("0"):
                        positions.pop(fill.symbol, None)
                    else:
                        positions[fill.symbol] = existing.model_copy(
                            update={
                                "quantity": new_qty,
                                "realised_pnl": existing.realised_pnl
                                + (pnl if existing.side is Side.BUY else -pnl),
                                "updated_at": datetime.now(timezone.utc),
                            }
                        )

            self._portfolio = self._recompute_equity(
                self._portfolio.model_copy(
                    update={
                        "positions": positions,
                        "cash_balance": cash,
                        "realised_pnl": realised_pnl,
                        "updated_at": datetime.now(timezone.utc),
                    }
                )
            )

        self._log.info(
            "Portfolio updated from fill",
            symbol=fill.symbol,
            side=fill.side,
            quantity=str(fill.quantity),
            price=str(fill.price),
        )

    async def mark_to_market(self, prices: Dict[str, Decimal]) -> None:
        """Revalue all positions using current market prices.

        Args:
            prices: Mapping of ``symbol`` → current mark price.
        """
        async with self._lock:
            positions: Dict[str, Position] = {}
            for symbol, pos in self._portfolio.positions.items():
                mark = prices.get(symbol)
                if mark is not None:
                    unrealised = pos.calculate_unrealised_pnl(mark)
                    positions[symbol] = pos.model_copy(
                        update={
                            "current_price": mark,
                            "unrealised_pnl": unrealised,
                            "updated_at": datetime.now(timezone.utc),
                        }
                    )
                else:
                    positions[symbol] = pos

            self._portfolio = self._recompute_equity(
                self._portfolio.model_copy(
                    update={
                        "positions": positions,
                        "updated_at": datetime.now(timezone.utc),
                    }
                )
            )

        self._log.debug("Mark-to-market applied", symbols=list(prices.keys()))

    # ── Internal helpers ───────────────────────────────────────────────────

    @staticmethod
    def _recompute_equity(portfolio: Portfolio) -> Portfolio:
        """Recalculate ``total_equity`` and update ``peak_equity``."""
        position_value = sum(
            p.notional_value for p in portfolio.positions.values()
        )
        total_equity = portfolio.cash_balance + position_value
        peak_equity = max(portfolio.peak_equity, total_equity)
        return portfolio.model_copy(
            update={"total_equity": total_equity, "peak_equity": peak_equity}
        )
