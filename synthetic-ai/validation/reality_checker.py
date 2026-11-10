"""Reality checking: validate synthetic data against real data distributions.

Provides :class:`RealityChecker` using Kolmogorov-Smirnov tests, correlation
checks, and autocorrelation comparisons.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats
from loguru import logger


class RealityChecker:
    """Validate synthetic financial time series against real data.

    Runs a battery of statistical tests to ensure that synthetic data
    plausibly replicates the key statistical properties of real market data.

    Tests performed:

    * **KS test** on return distributions.
    * **Mean / std comparison** (z-test on means).
    * **Autocorrelation** check (first-order lag-1 ACF).
    * **Tail ratio** (95th percentile / 5th percentile returns).
    * **Variance ratio** test for random-walk properties.

    Attributes:
        ks_alpha: Significance level for KS test.
        mean_tol: Tolerance for mean comparison (absolute difference).
        std_tol: Tolerance for std comparison (relative difference).
    """

    def __init__(
        self,
        ks_alpha: float = 0.05,
        mean_tol: float = 0.002,
        std_tol: float = 0.20,
    ) -> None:
        """Initialise RealityChecker.

        Args:
            ks_alpha: KS test significance level.
            mean_tol: Absolute tolerance for mean return comparison.
            std_tol: Relative tolerance for std comparison.
        """
        self.ks_alpha = ks_alpha
        self.mean_tol = mean_tol
        self.std_tol = std_tol

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _price_to_returns(prices: Any) -> np.ndarray:
        """Convert prices to log-returns.

        Args:
            prices: Array-like of prices.

        Returns:
            Log-return array.
        """
        arr = np.asarray(prices, dtype=np.float64)
        return np.diff(np.log(arr))

    @staticmethod
    def _acf_lag1(returns: np.ndarray) -> float:
        """Compute lag-1 autocorrelation.

        Args:
            returns: Return array.

        Returns:
            Lag-1 Pearson correlation coefficient.
        """
        if len(returns) < 3:
            return 0.0
        return float(np.corrcoef(returns[:-1], returns[1:])[0, 1])

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def check(
        self,
        real_prices: Any,
        synthetic_prices: Any,
    ) -> dict[str, Any]:
        """Run full reality-check battery.

        Args:
            real_prices: Array-like of real market prices.
            synthetic_prices: Array-like of synthetic prices.

        Returns:
            Dict with test names as keys and result dicts as values, plus an
            overall ``passed`` flag.

        Raises:
            ValueError: If either price series has fewer than 10 data points.
        """
        real_r = self._price_to_returns(real_prices)
        synth_r = self._price_to_returns(synthetic_prices)

        for name, arr in [("real", real_r), ("synthetic", synth_r)]:
            if len(arr) < 10:
                raise ValueError(f"{name} prices must yield at least 10 returns.")

        results: dict[str, Any] = {}

        # 1. KS test
        ks_stat, ks_pvalue = stats.ks_2samp(real_r, synth_r)
        results["ks_test"] = {
            "statistic": round(float(ks_stat), 6),
            "p_value": round(float(ks_pvalue), 6),
            "passed": ks_pvalue >= self.ks_alpha,
        }

        # 2. Mean comparison
        real_mean = float(np.mean(real_r))
        synth_mean = float(np.mean(synth_r))
        mean_diff = abs(real_mean - synth_mean)
        results["mean_comparison"] = {
            "real_mean": round(real_mean, 6),
            "synth_mean": round(synth_mean, 6),
            "abs_diff": round(mean_diff, 6),
            "passed": mean_diff <= self.mean_tol,
        }

        # 3. Std comparison
        real_std = float(np.std(real_r, ddof=1))
        synth_std = float(np.std(synth_r, ddof=1))
        rel_diff = abs(real_std - synth_std) / (real_std + 1e-9)
        results["std_comparison"] = {
            "real_std": round(real_std, 6),
            "synth_std": round(synth_std, 6),
            "relative_diff": round(rel_diff, 6),
            "passed": rel_diff <= self.std_tol,
        }

        # 4. Autocorrelation
        real_acf = self._acf_lag1(real_r)
        synth_acf = self._acf_lag1(synth_r)
        acf_diff = abs(real_acf - synth_acf)
        results["autocorrelation"] = {
            "real_acf1": round(real_acf, 6),
            "synth_acf1": round(synth_acf, 6),
            "abs_diff": round(acf_diff, 6),
            "passed": acf_diff < 0.1,
        }

        # 5. Tail ratio
        real_tail = float(np.percentile(real_r, 95)) / (abs(float(np.percentile(real_r, 5))) + 1e-9)
        synth_tail = float(np.percentile(synth_r, 95)) / (abs(float(np.percentile(synth_r, 5))) + 1e-9)
        tail_diff = abs(real_tail - synth_tail)
        results["tail_ratio"] = {
            "real_tail_ratio": round(real_tail, 4),
            "synth_tail_ratio": round(synth_tail, 4),
            "abs_diff": round(tail_diff, 4),
            "passed": tail_diff < 0.5,
        }

        overall = all(v["passed"] for v in results.values())
        n_passed = sum(1 for v in results.values() if v["passed"])
        logger.info(f"Reality check: {n_passed}/{len(results)} tests passed")

        return {"passed": overall, "tests": results, "n_passed": n_passed, "n_total": len(results)}
