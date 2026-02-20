"""Slippage prediction: transaction cost estimation from market microstructure.

Provides :class:`SlippagePredictor` which estimates expected slippage in basis
points based on order size, spread, and volume characteristics.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class SlippagePredictor:
    """Predict transaction slippage for a proposed trade.

    Combines three cost components:

    1. **Half-spread cost** – unavoidable cost of crossing the spread.
    2. **Market impact** – price movement caused by the order itself.
    3. **Timing cost** – adverse price drift during execution.

    Attributes:
        impact_factor: Scaling coefficient for the square-root impact term.
        timing_factor: Scaling coefficient for the timing / drift cost.
        adv_lookback: Number of periods used to estimate average daily volume.
    """

    def __init__(
        self,
        impact_factor: float = 0.1,
        timing_factor: float = 0.05,
        adv_lookback: int = 20,
    ) -> None:
        """Initialise SlippagePredictor.

        Args:
            impact_factor: Market-impact scaling factor.
            timing_factor: Timing-cost scaling factor.
            adv_lookback: Look-back periods for ADV estimation.
        """
        self.impact_factor = impact_factor
        self.timing_factor = timing_factor
        self.adv_lookback = adv_lookback

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def predict(
        self,
        order_size: float,
        avg_daily_volume: float,
        spread_bps: float,
        volatility: float,
        urgency: float = 0.5,
    ) -> dict[str, float]:
        """Predict total slippage for a trade.

        Args:
            order_size: Order size (same units as *avg_daily_volume*).
            avg_daily_volume: Average daily traded volume.
            spread_bps: Current bid-ask spread in basis points.
            volatility: Intraday volatility as a fraction (e.g., 0.01 = 1%).
            urgency: Execution urgency in [0, 1].  Higher values cause faster
                (more impactful) execution.

        Returns:
            Dict with keys ``spread_cost_bps``, ``impact_cost_bps``,
            ``timing_cost_bps``, ``total_slippage_bps``.

        Raises:
            ValueError: If avg_daily_volume is zero or negative.
        """
        if avg_daily_volume <= 0:
            raise ValueError("avg_daily_volume must be positive.")

        participation_rate = min(order_size / avg_daily_volume, 1.0)

        spread_cost = spread_bps / 2.0
        impact_cost = (
            self.impact_factor
            * volatility
            * np.sqrt(participation_rate)
            * 10_000
        )
        timing_cost = self.timing_factor * volatility * urgency * 10_000

        total = spread_cost + impact_cost + timing_cost

        result = {
            "spread_cost_bps": round(spread_cost, 4),
            "impact_cost_bps": round(float(impact_cost), 4),
            "timing_cost_bps": round(float(timing_cost), 4),
            "total_slippage_bps": round(float(total), 4),
        }
        logger.debug(f"Slippage estimate: {result}")
        return result

    def predict_from_history(
        self,
        order_size: float,
        volume_history: Any,
        price_history: Any,
        spread_bps: float = 5.0,
        urgency: float = 0.5,
    ) -> dict[str, float]:
        """Predict slippage using historical volume and price series.

        Args:
            order_size: Order size.
            volume_history: Array-like of historical volume observations.
            price_history: Array-like of historical close prices.
            spread_bps: Current spread in basis points.
            urgency: Execution urgency in [0, 1].

        Returns:
            Slippage estimate dict (same keys as :meth:`predict`).
        """
        vols = np.asarray(volume_history, dtype=np.float64)
        prices = np.asarray(price_history, dtype=np.float64)

        adv = float(np.mean(vols[-self.adv_lookback:]))

        returns = np.diff(prices) / prices[:-1]
        volatility = float(np.std(returns, ddof=1)) if len(returns) >= 2 else 0.01

        return self.predict(order_size, adv, spread_bps, volatility, urgency)
