"""Pre-trade risk engine.

Evaluates a proposed order against the current portfolio state and a set of
configurable limits.  Returns a :class:`~shared.models.ai_models.RiskAssessment`
regardless of outcome so callers can inspect rejection reasons.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from loguru import logger

from shared.common.config import RiskSettings, get_config
from shared.models.ai_models import RiskAssessment
from shared.models.trading_models import Order, Portfolio


class RiskEngine:
    """Stateless pre-trade risk checker.

    All limit values are sourced from :class:`~shared.common.config.RiskSettings`
    and can be overridden by passing a custom ``settings`` instance.

    Args:
        settings: Risk limit settings.  Defaults to ``get_config().risk``.
    """

    def __init__(self, settings: Optional[RiskSettings] = None) -> None:
        self._settings = settings or get_config().risk
        self._log = logger.bind(component="risk_engine")

    async def evaluate(self, order: Order, portfolio: Portfolio) -> RiskAssessment:
        """Run all pre-trade risk checks for *order* against *portfolio*.

        Args:
            order: The proposed order.
            portfolio: Current portfolio state.

        Returns:
            :class:`RiskAssessment` with ``is_approved`` set accordingly.
        """
        rejection_reasons: List[str] = []
        warnings: List[str] = []
        risk_score = 0.0

        # ── Estimate notional value ────────────────────────────────────────
        price_estimate = order.price or self._estimate_price(order.symbol, portfolio)
        proposed_notional = order.quantity * price_estimate if price_estimate else Decimal("0")

        # ── Check 1: max order size ────────────────────────────────────────
        max_order = Decimal(str(self._settings.max_order_size_usd))
        if proposed_notional > max_order:
            reason = (
                f"Order notional {proposed_notional:.2f} USD exceeds max "
                f"order size {max_order:.2f} USD"
            )
            rejection_reasons.append(reason)
            risk_score = min(risk_score + 0.4, 1.0)
            self._log.warning("Risk check failed: max order size", reason=reason)

        # ── Check 2: max position size ─────────────────────────────────────
        max_position = Decimal(str(self._settings.max_position_size_usd))
        existing_position = portfolio.positions.get(order.symbol)
        existing_notional = (
            existing_position.notional_value if existing_position else Decimal("0")
        )
        total_position_notional = existing_notional + proposed_notional
        if total_position_notional > max_position:
            reason = (
                f"Combined position notional {total_position_notional:.2f} USD would exceed "
                f"max position size {max_position:.2f} USD"
            )
            rejection_reasons.append(reason)
            risk_score = min(risk_score + 0.35, 1.0)
            self._log.warning("Risk check failed: max position size", reason=reason)

        # ── Check 3: portfolio drawdown ────────────────────────────────────
        current_drawdown = portfolio.drawdown_pct
        max_drawdown = self._settings.max_portfolio_drawdown_pct
        if current_drawdown >= max_drawdown:
            reason = (
                f"Portfolio drawdown {current_drawdown:.2f}% at or above "
                f"limit {max_drawdown:.2f}%"
            )
            rejection_reasons.append(reason)
            risk_score = min(risk_score + 0.5, 1.0)
            self._log.warning("Risk check failed: drawdown limit", reason=reason)
        elif current_drawdown >= max_drawdown * 0.8:
            warnings.append(
                f"Portfolio drawdown {current_drawdown:.2f}% approaching "
                f"limit {max_drawdown:.2f}%"
            )
            risk_score = min(risk_score + 0.1, 1.0)

        # ── Check 4: daily loss limit ──────────────────────────────────────
        realised_loss = -portfolio.realised_pnl  # positive number = loss
        daily_limit = Decimal(str(self._settings.daily_loss_limit_usd))
        if realised_loss >= daily_limit:
            reason = (
                f"Realised daily loss {realised_loss:.2f} USD at or above "
                f"limit {daily_limit:.2f} USD"
            )
            rejection_reasons.append(reason)
            risk_score = min(risk_score + 0.5, 1.0)
            self._log.warning("Risk check failed: daily loss limit", reason=reason)

        is_approved = len(rejection_reasons) == 0

        assessment = RiskAssessment(
            symbol=order.symbol,
            proposed_quantity=order.quantity,
            proposed_notional_usd=proposed_notional,
            current_drawdown_pct=current_drawdown,
            is_approved=is_approved,
            risk_score=risk_score,
            rejection_reasons=rejection_reasons,
            warnings=warnings,
        )

        self._log.info(
            "Risk assessment complete",
            symbol=order.symbol,
            is_approved=is_approved,
            risk_score=risk_score,
            rejections=len(rejection_reasons),
        )
        return assessment

    @staticmethod
    def _estimate_price(symbol: str, portfolio: Portfolio) -> Optional[Decimal]:
        """Best-effort price estimate from existing positions."""
        pos = portfolio.positions.get(symbol)
        if pos and pos.current_price:
            return pos.current_price
        if pos:
            return pos.average_entry_price
        return None
