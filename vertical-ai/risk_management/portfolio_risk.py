"""Portfolio risk: VaR, CVaR, and drawdown calculations.

Provides :class:`PortfolioRisk` using pure NumPy / SciPy for all statistical
computations.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats
from loguru import logger


class PortfolioRisk:
    """Compute portfolio-level risk metrics from return time series.

    Supports historical simulation and parametric (Gaussian) methods for
    Value-at-Risk and Conditional Value-at-Risk, plus rolling and peak-to-trough
    drawdown analysis.

    Attributes:
        confidence_level: Confidence level for VaR / CVaR (e.g., 0.95).
        method: ``"historical"`` or ``"parametric"``.
        annualisation_factor: Trading days per year used for annualised metrics.
    """

    def __init__(
        self,
        confidence_level: float = 0.95,
        method: str = "historical",
        annualisation_factor: int = 252,
    ) -> None:
        """Initialise PortfolioRisk.

        Args:
            confidence_level: Statistical confidence level (0 < cl < 1).
            method: ``"historical"`` for empirical distribution or
                ``"parametric"`` for Gaussian approximation.
            annualisation_factor: Number of periods in a year.

        Raises:
            ValueError: If confidence_level or method are invalid.
        """
        if not 0 < confidence_level < 1:
            raise ValueError("confidence_level must be in (0, 1).")
        if method not in ("historical", "parametric"):
            raise ValueError("method must be 'historical' or 'parametric'.")
        self.confidence_level = confidence_level
        self.method = method
        self.annualisation_factor = annualisation_factor

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_returns(returns: Any) -> np.ndarray:
        """Convert and validate a returns array.

        Args:
            returns: Array-like of period returns.

        Returns:
            Validated float64 array.

        Raises:
            ValueError: If the array is empty or 1-D check fails.
        """
        arr = np.asarray(returns, dtype=np.float64).ravel()
        if arr.size < 2:
            raise ValueError("returns must have at least 2 observations.")
        return arr

    def _var_historical(self, returns: np.ndarray) -> float:
        """Compute VaR by empirical percentile.

        Args:
            returns: Return array.

        Returns:
            VaR as a positive number representing loss.
        """
        return float(-np.percentile(returns, (1 - self.confidence_level) * 100))

    def _var_parametric(self, returns: np.ndarray) -> float:
        """Compute parametric (Gaussian) VaR.

        Args:
            returns: Return array.

        Returns:
            VaR as a positive number.
        """
        mu = float(np.mean(returns))
        sigma = float(np.std(returns, ddof=1))
        z = stats.norm.ppf(1 - self.confidence_level)
        return float(-(mu + z * sigma))

    def _cvar_historical(self, returns: np.ndarray) -> float:
        """Compute CVaR (Expected Shortfall) empirically.

        Args:
            returns: Return array.

        Returns:
            CVaR as a positive number.
        """
        cutoff = np.percentile(returns, (1 - self.confidence_level) * 100)
        tail = returns[returns <= cutoff]
        return float(-np.mean(tail)) if len(tail) > 0 else 0.0

    def _cvar_parametric(self, returns: np.ndarray) -> float:
        """Compute parametric CVaR (Gaussian).

        Args:
            returns: Return array.

        Returns:
            CVaR as a positive number.
        """
        mu = float(np.mean(returns))
        sigma = float(np.std(returns, ddof=1))
        alpha = 1 - self.confidence_level
        z = stats.norm.ppf(alpha)
        pdf_z = stats.norm.pdf(z)
        cvar = -(mu + sigma * pdf_z / alpha)
        return float(cvar)

    @staticmethod
    def _drawdown_series(cumulative_returns: np.ndarray) -> np.ndarray:
        """Compute the drawdown at each point relative to peak.

        Args:
            cumulative_returns: Cumulative return series (e.g., wealth index).

        Returns:
            Drawdown array (non-positive values).
        """
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / (running_max + 1e-9)
        return drawdown

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def compute_var(self, returns: Any) -> float:
        """Compute Value-at-Risk.

        Args:
            returns: Array-like of period returns.

        Returns:
            VaR (positive = potential loss).
        """
        arr = self._validate_returns(returns)
        if self.method == "parametric":
            return self._var_parametric(arr)
        return self._var_historical(arr)

    def compute_cvar(self, returns: Any) -> float:
        """Compute Conditional Value-at-Risk (Expected Shortfall).

        Args:
            returns: Array-like of period returns.

        Returns:
            CVaR (positive = expected loss beyond VaR threshold).
        """
        arr = self._validate_returns(returns)
        if self.method == "parametric":
            return self._cvar_parametric(arr)
        return self._cvar_historical(arr)

    def compute_drawdowns(self, returns: Any) -> dict[str, float]:
        """Compute drawdown metrics from a return series.

        Args:
            returns: Array-like of period returns.

        Returns:
            Dict with keys ``max_drawdown``, ``avg_drawdown``,
            ``current_drawdown``, ``drawdown_duration`` (in periods).
        """
        arr = self._validate_returns(returns)
        cum = np.cumprod(1 + arr)
        dd = self._drawdown_series(cum)

        max_dd = float(np.min(dd))
        avg_dd = float(np.mean(dd[dd < 0])) if np.any(dd < 0) else 0.0
        current_dd = float(dd[-1])

        # Longest streak below zero
        in_dd = (dd < 0).astype(int)
        max_duration = 0
        current_streak = 0
        for v in in_dd:
            current_streak = current_streak + 1 if v else 0
            max_duration = max(max_duration, current_streak)

        return {
            "max_drawdown": max_dd,
            "avg_drawdown": avg_dd,
            "current_drawdown": current_dd,
            "drawdown_duration": max_duration,
        }

    def full_risk_report(self, returns: Any) -> dict[str, Any]:
        """Generate a full risk report for a return series.

        Args:
            returns: Array-like of period returns.

        Returns:
            Dict containing VaR, CVaR, drawdown metrics, volatility, and
            annualised Sharpe ratio (assuming zero risk-free rate).
        """
        arr = self._validate_returns(returns)
        logger.debug(f"Computing full risk report for {len(arr)} returns")

        var = self.compute_var(arr)
        cvar = self.compute_cvar(arr)
        dd = self.compute_drawdowns(arr)

        vol = float(np.std(arr, ddof=1)) * np.sqrt(self.annualisation_factor)
        ann_return = float(np.mean(arr)) * self.annualisation_factor
        sharpe = ann_return / vol if vol > 0 else 0.0

        return {
            "var": var,
            "cvar": cvar,
            **dd,
            "annualised_volatility": vol,
            "annualised_return": ann_return,
            "sharpe_ratio": sharpe,
            "confidence_level": self.confidence_level,
            "method": self.method,
        }
