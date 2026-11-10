"""Market impact model: square-root and linear price-impact estimation.

Provides :class:`MarketImpactModel` implementing the Almgren-Chriss square-root
market-impact framework for estimating permanent and temporary price impact.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class MarketImpactModel:
    """Estimate market impact of trades using the square-root model.

    Decomposes total market impact into:

    * **Temporary impact** – immediate, mean-reverting liquidity cost.
    * **Permanent impact** – lasting price change from information content.

    The model follows Almgren & Chriss (2001):
        ``I_temp = eta * sigma * sqrt(v / ADV)``
        ``I_perm = gamma * sigma * (v / ADV)``

    where *v* is trade size, *ADV* is average daily volume, and *sigma* is
    daily volatility.

    Attributes:
        eta: Temporary impact coefficient.
        gamma: Permanent impact coefficient.
        sigma_daily: Default daily return volatility (fraction).
    """

    def __init__(
        self,
        eta: float = 0.142,
        gamma: float = 0.314,
        sigma_daily: float = 0.02,
    ) -> None:
        """Initialise MarketImpactModel.

        Args:
            eta: Temporary impact coefficient (Almgren-Chriss eta).
            gamma: Permanent impact coefficient (Almgren-Chriss gamma).
            sigma_daily: Default daily volatility estimate (fraction).
        """
        self.eta = eta
        self.gamma = gamma
        self.sigma_daily = sigma_daily

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def estimate(
        self,
        order_size: float,
        avg_daily_volume: float,
        volatility: float | None = None,
        side: str = "buy",
    ) -> dict[str, float]:
        """Estimate market impact for a single trade.

        Args:
            order_size: Order size in shares.
            avg_daily_volume: Average daily trading volume in shares.
            volatility: Daily return volatility; falls back to
                :attr:`sigma_daily` if not provided.
            side: ``"buy"`` or ``"sell"``.  Impact direction is signed
                accordingly.

        Returns:
            Dict with keys ``temporary_impact_bps``, ``permanent_impact_bps``,
            ``total_impact_bps``, ``participation_rate``.

        Raises:
            ValueError: If order_size or avg_daily_volume are non-positive,
                or side is invalid.
        """
        if order_size <= 0:
            raise ValueError("order_size must be positive.")
        if avg_daily_volume <= 0:
            raise ValueError("avg_daily_volume must be positive.")
        if side not in ("buy", "sell"):
            raise ValueError("side must be 'buy' or 'sell'.")

        sigma = volatility if volatility is not None else self.sigma_daily
        v_over_adv = order_size / avg_daily_volume
        sign = 1.0 if side == "buy" else -1.0

        temp_impact = self.eta * sigma * np.sqrt(v_over_adv) * 10_000
        perm_impact = self.gamma * sigma * v_over_adv * 10_000

        total_impact = sign * (temp_impact + perm_impact)

        result = {
            "temporary_impact_bps": round(float(sign * temp_impact), 4),
            "permanent_impact_bps": round(float(sign * perm_impact), 4),
            "total_impact_bps": round(float(total_impact), 4),
            "participation_rate": round(float(v_over_adv), 6),
        }
        logger.debug(f"Market impact: {result}")
        return result

    def optimal_execution_schedule(
        self,
        total_shares: float,
        avg_daily_volume: float,
        n_slices: int = 10,
        volatility: float | None = None,
        risk_aversion: float = 1.0,
    ) -> dict[str, Any]:
        """Compute a TWAP-like schedule minimising expected impact plus variance.

        Minimises a linear combination of expected market impact and execution
        risk (price variance) by distributing the order evenly in time.

        Args:
            total_shares: Total shares to execute.
            avg_daily_volume: Average daily volume.
            n_slices: Number of equal time slices.
            volatility: Daily volatility; defaults to :attr:`sigma_daily`.
            risk_aversion: Lambda parameter trading off impact vs risk.

        Returns:
            Dict with keys ``schedule`` (list of slice sizes), ``total_cost_bps``,
            ``execution_shortfall_bps``.
        """
        sigma = volatility if volatility is not None else self.sigma_daily
        slice_size = total_shares / n_slices

        impacts = []
        for i in range(n_slices):
            imp = self.estimate(slice_size, avg_daily_volume, sigma)
            impacts.append(imp["total_impact_bps"])

        total_cost = sum(abs(c) for c in impacts)
        variance_penalty = risk_aversion * sigma * np.sqrt(n_slices) * 10_000
        shortfall = total_cost + float(variance_penalty)

        logger.debug(
            f"Execution schedule: {n_slices} slices, "
            f"total_cost={total_cost:.2f}bps, shortfall={shortfall:.2f}bps"
        )
        return {
            "schedule": [slice_size] * n_slices,
            "impact_per_slice_bps": impacts,
            "total_cost_bps": round(total_cost, 4),
            "execution_shortfall_bps": round(shortfall, 4),
        }
