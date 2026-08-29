"""Position sizing: Kelly criterion, fixed fraction, and volatility targeting.

Provides :class:`PositionSizer` which implements three complementary position
sizing methodologies for risk-controlled trade allocation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class PositionSizer:
    """Compute optimal position sizes using multiple sizing methodologies.

    Implements:

    * **Kelly Criterion** – maximises expected logarithmic growth.
    * **Fixed Fraction** – simple risk-per-trade percentage.
    * **Volatility Targeting** – size inversely proportional to asset vol.

    Attributes:
        max_position_fraction: Hard cap on any single position as a fraction
            of portfolio equity (0 < cap ≤ 1).
        annualisation_factor: Trading periods per year for volatility scaling.
    """

    def __init__(
        self,
        max_position_fraction: float = 0.25,
        annualisation_factor: int = 252,
    ) -> None:
        """Initialise PositionSizer.

        Args:
            max_position_fraction: Maximum fraction of capital for any single
                position.
            annualisation_factor: Used to annualise daily volatility.

        Raises:
            ValueError: If max_position_fraction is outside (0, 1].
        """
        if not 0 < max_position_fraction <= 1:
            raise ValueError("max_position_fraction must be in (0, 1].")
        self.max_position_fraction = max_position_fraction
        self.annualisation_factor = annualisation_factor

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _cap(self, fraction: float) -> float:
        """Apply the maximum position fraction cap.

        Args:
            fraction: Raw computed position fraction.

        Returns:
            Capped fraction.
        """
        return float(np.clip(fraction, 0.0, self.max_position_fraction))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def kelly_criterion(
        self,
        win_rate: float,
        win_loss_ratio: float,
        kelly_fraction: float = 1.0,
    ) -> float:
        """Compute Kelly-optimal position fraction.

        Uses the simplified discrete Kelly formula:
        ``f* = (p * b - q) / b`` where *p* is the win probability, *b* is the
        win/loss ratio, and *q = 1 - p*.

        Args:
            win_rate: Probability of a winning trade (0 < p < 1).
            win_loss_ratio: Average win divided by average loss (b > 0).
            kelly_fraction: Fractional Kelly multiplier to reduce variance
                (commonly 0.25–0.5 in practice).

        Returns:
            Optimal position size as fraction of capital.

        Raises:
            ValueError: If inputs are out of range.
        """
        if not 0 < win_rate < 1:
            raise ValueError("win_rate must be in (0, 1).")
        if win_loss_ratio <= 0:
            raise ValueError("win_loss_ratio must be positive.")
        if not 0 < kelly_fraction <= 1:
            raise ValueError("kelly_fraction must be in (0, 1].")

        p = win_rate
        q = 1.0 - p
        b = win_loss_ratio
        raw_kelly = (p * b - q) / b
        adjusted = raw_kelly * kelly_fraction

        result = self._cap(max(adjusted, 0.0))
        logger.debug(f"Kelly: raw={raw_kelly:.4f}, adjusted={adjusted:.4f}, capped={result:.4f}")
        return result

    def fixed_fraction(
        self,
        risk_per_trade: float,
        stop_loss_pct: float,
        capital: float,
        price: float,
    ) -> dict[str, float]:
        """Compute fixed-fraction position size from a stop-loss percentage.

        Position size is calculated as:
        ``n_shares = (capital × risk_fraction) / (price × stop_loss_pct)``

        Args:
            risk_per_trade: Fraction of capital to risk per trade (e.g., 0.01).
            stop_loss_pct: Stop-loss distance as fraction of price (e.g., 0.02).
            capital: Total portfolio capital in currency units.
            price: Current asset price in currency units.

        Returns:
            Dict with keys ``position_fraction``, ``shares``, ``risk_amount``.

        Raises:
            ValueError: If stop_loss_pct is zero or negative.
        """
        if stop_loss_pct <= 0:
            raise ValueError("stop_loss_pct must be positive.")
        if price <= 0:
            raise ValueError("price must be positive.")

        risk_amount = capital * risk_per_trade
        shares = risk_amount / (price * stop_loss_pct)
        position_value = shares * price
        position_fraction = self._cap(position_value / capital if capital > 0 else 0.0)
        # Re-scale shares if the fraction was capped
        actual_shares = (position_fraction * capital) / price

        logger.debug(
            f"Fixed-fraction: risk={risk_amount:.2f}, shares={actual_shares:.4f}, "
            f"fraction={position_fraction:.4f}"
        )
        return {
            "position_fraction": position_fraction,
            "shares": actual_shares,
            "risk_amount": risk_amount,
        }

    def volatility_targeting(
        self,
        returns: Any,
        target_volatility: float,
        capital: float,
        price: float,
    ) -> dict[str, float]:
        """Compute position size to achieve a target annualised volatility.

        Position fraction = ``target_vol / asset_annualised_vol``.

        Args:
            returns: Array-like of recent period returns for the asset.
            target_volatility: Target annualised portfolio volatility.
            capital: Total portfolio capital.
            price: Current asset price.

        Returns:
            Dict with keys ``position_fraction``, ``shares``,
            ``asset_volatility``.

        Raises:
            ValueError: If returns array is too short.
        """
        arr = np.asarray(returns, dtype=np.float64).ravel()
        if arr.size < 2:
            raise ValueError("returns must have at least 2 observations.")

        daily_vol = float(np.std(arr, ddof=1))
        ann_vol = daily_vol * np.sqrt(self.annualisation_factor)

        if ann_vol == 0:
            logger.warning("Asset volatility is zero; defaulting to max fraction.")
            fraction = self.max_position_fraction
        else:
            fraction = self._cap(target_volatility / ann_vol)

        shares = (fraction * capital) / price if price > 0 else 0.0

        logger.debug(
            f"Vol-targeting: ann_vol={ann_vol:.4f}, target={target_volatility:.4f}, "
            f"fraction={fraction:.4f}"
        )
        return {
            "position_fraction": fraction,
            "shares": shares,
            "asset_volatility": ann_vol,
        }
