"""Correlation analysis: rolling asset correlations and clustering.

Provides :class:`CorrelationAnalyzer` for tracking pairwise and portfolio-level
correlation dynamics over time.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger


class CorrelationAnalyzer:
    """Track rolling pairwise correlations between multiple assets.

    Uses a rolling window of period returns to compute Pearson correlation
    matrices and derived statistics such as average correlation and
    minimum-variance cluster identification.

    Attributes:
        window: Rolling window size (number of periods).
        min_periods: Minimum observations required before computing
            correlation (defaults to half the window).
    """

    def __init__(
        self,
        window: int = 60,
        min_periods: int | None = None,
    ) -> None:
        """Initialise CorrelationAnalyzer.

        Args:
            window: Look-back window for rolling correlation.
            min_periods: Minimum periods of data required.  Defaults to
                ``window // 2``.
        """
        if window < 2:
            raise ValueError("window must be at least 2.")
        self.window = window
        self.min_periods = min_periods if min_periods is not None else window // 2

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_returns_matrix(
        returns_matrix: Any,
    ) -> tuple[np.ndarray, int, int]:
        """Parse and validate the returns matrix.

        Args:
            returns_matrix: Array-like of shape ``(n_periods, n_assets)``.

        Returns:
            Tuple of (array, n_periods, n_assets).

        Raises:
            ValueError: If input is not 2-D or has fewer than 2 assets.
        """
        arr = np.asarray(returns_matrix, dtype=np.float64)
        if arr.ndim != 2:
            raise ValueError("returns_matrix must be 2-D (periods × assets).")
        n_periods, n_assets = arr.shape
        if n_assets < 2:
            raise ValueError("At least 2 assets are required.")
        return arr, n_periods, n_assets

    @staticmethod
    def _pearson_corr(x: np.ndarray, y: np.ndarray) -> float:
        """Compute Pearson correlation between two arrays.

        Args:
            x: First array.
            y: Second array.

        Returns:
            Pearson r, or ``nan`` if undefined.
        """
        if len(x) < 2:
            return float("nan")
        vx = x - np.mean(x)
        vy = y - np.mean(y)
        denom = np.sqrt(np.sum(vx ** 2) * np.sum(vy ** 2))
        if denom == 0:
            return float("nan")
        return float(np.sum(vx * vy) / denom)

    def _rolling_corr_pair(
        self,
        series_a: np.ndarray,
        series_b: np.ndarray,
    ) -> np.ndarray:
        """Compute rolling Pearson correlation for a pair of series.

        Args:
            series_a: Return series for asset A.
            series_b: Return series for asset B.

        Returns:
            Array of rolling correlations (NaN before min_periods).
        """
        n = len(series_a)
        corrs = np.full(n, np.nan)
        for i in range(n):
            start = max(0, i - self.window + 1)
            a_win = series_a[start: i + 1]
            b_win = series_b[start: i + 1]
            if len(a_win) >= self.min_periods:
                corrs[i] = self._pearson_corr(a_win, b_win)
        return corrs

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def compute_correlation_matrix(
        self, returns_matrix: Any
    ) -> dict[str, Any]:
        """Compute the full-sample correlation matrix.

        Args:
            returns_matrix: Array-like of shape ``(n_periods, n_assets)``.

        Returns:
            Dict with keys ``correlation_matrix`` (2-D list),
            ``average_correlation`` (float), ``n_assets``, ``n_periods``.
        """
        arr, n_periods, n_assets = self._validate_returns_matrix(returns_matrix)

        if n_periods < self.min_periods:
            raise ValueError(
                f"Need at least {self.min_periods} periods; got {n_periods}."
            )

        corr_mat = np.corrcoef(arr.T)
        # Mask diagonal for average off-diagonal correlation
        mask = ~np.eye(n_assets, dtype=bool)
        avg_corr = float(np.nanmean(corr_mat[mask]))

        logger.debug(f"Correlation matrix: {n_assets}×{n_assets}, avg_corr={avg_corr:.4f}")
        return {
            "correlation_matrix": corr_mat.tolist(),
            "average_correlation": avg_corr,
            "n_assets": n_assets,
            "n_periods": n_periods,
        }

    def rolling_correlations(
        self,
        returns_matrix: Any,
        asset_names: list[str] | None = None,
    ) -> dict[str, Any]:
        """Compute rolling pairwise correlations for all asset pairs.

        Args:
            returns_matrix: Array-like of shape ``(n_periods, n_assets)``.
            asset_names: Optional list of asset name strings.

        Returns:
            Dict mapping ``"asset_i_vs_asset_j"`` strings to lists of rolling
            correlation values.
        """
        arr, n_periods, n_assets = self._validate_returns_matrix(returns_matrix)
        names = asset_names or [f"asset_{i}" for i in range(n_assets)]

        if len(names) != n_assets:
            raise ValueError("asset_names length must match number of assets.")

        result: dict[str, list[float | None]] = {}
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                key = f"{names[i]}_vs_{names[j]}"
                corrs = self._rolling_corr_pair(arr[:, i], arr[:, j])
                result[key] = [None if np.isnan(v) else round(float(v), 6) for v in corrs]

        logger.debug(f"Rolling correlations computed for {len(result)} pairs")
        return result

    def correlation_regime(
        self, returns_matrix: Any
    ) -> dict[str, Any]:
        """Classify the current correlation regime.

        Computes recent vs historical average correlation to detect risk-on /
        risk-off regime shifts.

        Args:
            returns_matrix: Array-like of shape ``(n_periods, n_assets)``.

        Returns:
            Dict with keys ``current_avg_corr``, ``historical_avg_corr``,
            ``regime`` (``"high"``, ``"normal"``, or ``"low"``).
        """
        arr, n_periods, n_assets = self._validate_returns_matrix(returns_matrix)
        recent_n = min(self.window, n_periods)

        historical_corr_mat = np.corrcoef(arr.T)
        recent_corr_mat = np.corrcoef(arr[-recent_n:].T)

        mask = ~np.eye(n_assets, dtype=bool)
        hist_avg = float(np.nanmean(historical_corr_mat[mask]))
        curr_avg = float(np.nanmean(recent_corr_mat[mask]))

        if curr_avg > 0.7:
            regime = "high"
        elif curr_avg < 0.3:
            regime = "low"
        else:
            regime = "normal"

        return {
            "current_avg_corr": round(curr_avg, 4),
            "historical_avg_corr": round(hist_avg, 4),
            "regime": regime,
        }
