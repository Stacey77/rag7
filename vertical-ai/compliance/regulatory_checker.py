"""Regulatory compliance: position limits, wash trading, and PDT checks.

Provides :class:`RegulatoryChecker` for pre-trade and post-trade compliance
validation.
"""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from loguru import logger


class RegulatoryChecker:
    """Check proposed and executed trades against regulatory rules.

    Implements three key compliance checks:

    1. **Position limits** – rejects orders that would breach per-asset or
       portfolio gross exposure limits.
    2. **Wash trading detection** – flags buy-then-sell (or vice versa) of the
       same instrument within a configurable window.
    3. **Pattern Day Trading (PDT)** – counts day-trade round-trips in a
       rolling 5-trading-day window and enforces the FINRA 3-trip limit for
       accounts below the minimum equity threshold.

    Attributes:
        position_limits: Per-symbol maximum absolute position size.
        portfolio_limit: Maximum sum of absolute positions across all symbols.
        wash_trade_window_secs: Time window to detect wash trades.
        pdt_account_minimum: Equity threshold below which PDT applies.
        pdt_max_day_trades: Maximum day trades per rolling 5-day window.
    """

    def __init__(
        self,
        position_limits: dict[str, float] | None = None,
        portfolio_limit: float = 1_000_000.0,
        wash_trade_window_secs: int = 30,
        pdt_account_minimum: float = 25_000.0,
        pdt_max_day_trades: int = 3,
    ) -> None:
        """Initialise RegulatoryChecker.

        Args:
            position_limits: Symbol → max absolute position size.
            portfolio_limit: Maximum total gross exposure.
            wash_trade_window_secs: Seconds within which a buy followed by a
                sell (or vice versa) of the same symbol is flagged as wash.
            pdt_account_minimum: Account equity below which PDT rules apply.
            pdt_max_day_trades: Allowed day trades per rolling 5-day window.
        """
        self.position_limits: dict[str, float] = position_limits or {}
        self.portfolio_limit = portfolio_limit
        self.wash_trade_window_secs = wash_trade_window_secs
        self.pdt_account_minimum = pdt_account_minimum
        self.pdt_max_day_trades = pdt_max_day_trades

        # Internal state for wash-trade and PDT tracking
        self._recent_trades: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._day_trades: list[datetime] = []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _prune_old_trades(self, symbol: str, now: datetime) -> None:
        """Remove wash-trade records outside the detection window.

        Args:
            symbol: Instrument symbol.
            now: Current UTC datetime.
        """
        cutoff = now - timedelta(seconds=self.wash_trade_window_secs)
        self._recent_trades[symbol] = [
            t for t in self._recent_trades[symbol]
            if t["timestamp"] >= cutoff
        ]

    def _prune_old_day_trades(self, now: datetime) -> None:
        """Remove PDT records older than 5 calendar days.

        Args:
            now: Current UTC datetime.
        """
        cutoff = now - timedelta(days=5)
        self._day_trades = [dt for dt in self._day_trades if dt >= cutoff]

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def check_position_limit(
        self,
        symbol: str,
        current_position: float,
        order_size: float,
        side: str,
    ) -> dict[str, Any]:
        """Check whether an order would breach position limits.

        Args:
            symbol: Instrument symbol.
            current_position: Current signed position (positive = long).
            order_size: Unsigned order size.
            side: ``"buy"`` or ``"sell"``.

        Returns:
            Dict with keys ``passed`` (bool), ``reason`` (str or None),
            ``resulting_position`` (float), ``limit`` (float).
        """
        delta = order_size if side == "buy" else -order_size
        resulting = current_position + delta
        limit = self.position_limits.get(symbol, float("inf"))

        if abs(resulting) > limit:
            logger.warning(f"Position limit breach: {symbol} → {resulting} > {limit}")
            return {
                "passed": False,
                "reason": (
                    f"Position {resulting:.0f} exceeds limit {limit:.0f} for {symbol}"
                ),
                "resulting_position": resulting,
                "limit": limit,
            }
        return {"passed": True, "reason": None, "resulting_position": resulting, "limit": limit}

    def check_portfolio_limit(
        self, positions: dict[str, float], prices: dict[str, float]
    ) -> dict[str, Any]:
        """Check gross portfolio exposure against the portfolio limit.

        Args:
            positions: Symbol → signed share position.
            prices: Symbol → current price.

        Returns:
            Dict with keys ``passed``, ``gross_exposure``, ``limit``.
        """
        gross = sum(abs(pos) * prices.get(sym, 0.0) for sym, pos in positions.items())
        passed = gross <= self.portfolio_limit
        if not passed:
            logger.warning(f"Portfolio limit breach: {gross:.2f} > {self.portfolio_limit:.2f}")
        return {
            "passed": passed,
            "gross_exposure": round(gross, 2),
            "limit": self.portfolio_limit,
        }

    def check_wash_trade(
        self,
        symbol: str,
        side: str,
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Detect potential wash trading.

        A wash trade is flagged when an opposite-side order for the same
        symbol arrives within :attr:`wash_trade_window_secs`.

        Args:
            symbol: Instrument symbol.
            side: ``"buy"`` or ``"sell"``.
            timestamp: Order timestamp; defaults to ``datetime.now(UTC)``.

        Returns:
            Dict with keys ``passed`` (False = wash trade detected),
            ``reason``, ``flagged_trades``.
        """
        now = timestamp or datetime.now(timezone.utc)
        self._prune_old_trades(symbol, now)

        opposite = "sell" if side == "buy" else "buy"
        flagged = [
            t for t in self._recent_trades[symbol] if t["side"] == opposite
        ]

        self._recent_trades[symbol].append({"side": side, "timestamp": now})

        if flagged:
            logger.warning(f"Wash trade detected: {symbol} {side} within window")
            return {
                "passed": False,
                "reason": f"Wash trade: {symbol} {side} follows {opposite} within "
                          f"{self.wash_trade_window_secs}s",
                "flagged_trades": flagged,
            }
        return {"passed": True, "reason": None, "flagged_trades": []}

    def check_pattern_day_trading(
        self,
        account_equity: float,
        is_day_trade: bool,
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Enforce FINRA Pattern Day Trading rules.

        Accounts below :attr:`pdt_account_minimum` are limited to
        :attr:`pdt_max_day_trades` round-trips in a rolling 5-day window.

        Args:
            account_equity: Current account equity in USD.
            is_day_trade: Whether the proposed trade is a day trade (same-day
                open and close of the same instrument).
            timestamp: Trade timestamp; defaults to ``datetime.now(UTC)``.

        Returns:
            Dict with keys ``passed``, ``reason``, ``day_trade_count``.
        """
        now = timestamp or datetime.now(timezone.utc)
        self._prune_old_day_trades(now)

        if is_day_trade:
            self._day_trades.append(now)

        count = len(self._day_trades)

        if account_equity >= self.pdt_account_minimum:
            return {"passed": True, "reason": None, "day_trade_count": count}

        if count > self.pdt_max_day_trades:
            logger.warning(f"PDT violation: {count} day trades, equity={account_equity:.2f}")
            return {
                "passed": False,
                "reason": (
                    f"PDT rule: {count} day trades exceed limit of "
                    f"{self.pdt_max_day_trades} for accounts below "
                    f"${self.pdt_account_minimum:,.0f}"
                ),
                "day_trade_count": count,
            }
        return {"passed": True, "reason": None, "day_trade_count": count}

    def full_compliance_check(
        self,
        order: dict[str, Any],
        positions: dict[str, float],
        prices: dict[str, float],
        account_equity: float,
        is_day_trade: bool = False,
    ) -> dict[str, Any]:
        """Run all compliance checks for a proposed order.

        Args:
            order: Dict with keys ``symbol``, ``side``, ``size``,
                optionally ``timestamp``.
            positions: Current signed positions by symbol.
            prices: Current prices by symbol.
            account_equity: Account equity in USD.
            is_day_trade: Whether the order is a day trade.

        Returns:
            Dict with ``passed`` (bool) and ``checks`` (per-rule results).
        """
        symbol = order["symbol"]
        side = order["side"]
        size = float(order["size"])
        ts = order.get("timestamp")

        results: dict[str, Any] = {}
        results["position_limit"] = self.check_position_limit(
            symbol, positions.get(symbol, 0.0), size, side
        )
        results["portfolio_limit"] = self.check_portfolio_limit(positions, prices)
        results["wash_trade"] = self.check_wash_trade(symbol, side, ts)
        results["pdt"] = self.check_pattern_day_trading(account_equity, is_day_trade, ts)

        all_passed = all(v["passed"] for v in results.values())
        return {"passed": all_passed, "checks": results}
