"""Distribution matching: statistical distribution validation using moments.

Provides :class:`DistributionMatcher` for comparing empirical moments and
fitting parametric distributions to financial return data.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy import stats
from loguru import logger


class DistributionMatcher:
    """Validate and match statistical distributions for financial returns.

    Computes the first four statistical moments, fits candidate parametric
    distributions, and selects the best fit by AIC criterion.

    Attributes:
        candidate_distributions: Distributions to consider for fitting.
        moment_tolerances: Acceptable relative error for each moment.
    """

    _DEFAULT_CANDIDATES: list[str] = ["norm", "t", "laplace", "logistic", "gennorm"]

    def __init__(
        self,
        candidate_distributions: list[str] | None = None,
        moment_tolerances: dict[str, float] | None = None,
    ) -> None:
        """Initialise DistributionMatcher.

        Args:
            candidate_distributions: List of scipy.stats distribution names
                to consider.
            moment_tolerances: Dict mapping moment names (``"mean"``, ``"std"``,
                ``"skewness"``, ``"kurtosis"``) to acceptable relative errors.
        """
        self.candidate_distributions = (
            candidate_distributions or self._DEFAULT_CANDIDATES
        )
        self.moment_tolerances = moment_tolerances or {
            "mean": 0.5,
            "std": 0.2,
            "skewness": 0.5,
            "kurtosis": 1.0,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_moments(data: np.ndarray) -> dict[str, float]:
        """Compute the first four standardised moments.

        Args:
            data: 1-D array of observations.

        Returns:
            Dict with ``mean``, ``std``, ``skewness``, ``kurtosis`` (excess).
        """
        return {
            "mean": float(np.mean(data)),
            "std": float(np.std(data, ddof=1)),
            "skewness": float(stats.skew(data)),
            "kurtosis": float(stats.kurtosis(data)),
        }

    def _fit_distribution(
        self, dist_name: str, data: np.ndarray
    ) -> dict[str, Any] | None:
        """Fit a parametric distribution and compute AIC.

        Args:
            dist_name: scipy.stats distribution name.
            data: Sample data array.

        Returns:
            Dict with ``distribution``, ``params``, ``aic``, or None on
            failure.
        """
        try:
            dist = getattr(stats, dist_name)
            params = dist.fit(data)
            log_lik = np.sum(dist.logpdf(data, *params))
            k = len(params)
            aic = 2 * k - 2 * float(log_lik)
            return {"distribution": dist_name, "params": params, "aic": aic}
        except Exception as exc:
            logger.debug(f"Failed to fit {dist_name}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def compute_moments(self, data: Any) -> dict[str, float]:
        """Compute descriptive statistics and moments of a data series.

        Args:
            data: Array-like of numeric values.

        Returns:
            Moments dict: ``mean``, ``std``, ``skewness``, ``kurtosis``.

        Raises:
            ValueError: If fewer than 4 data points are provided.
        """
        arr = np.asarray(data, dtype=np.float64).ravel()
        if len(arr) < 4:
            raise ValueError("At least 4 data points are required.")
        return self._compute_moments(arr)

    def fit_best_distribution(
        self, data: Any
    ) -> dict[str, Any]:
        """Fit candidate distributions and return the best by AIC.

        Args:
            data: Array-like of return observations.

        Returns:
            Dict with keys ``best_distribution``, ``best_aic``, ``best_params``,
            and ``all_fits`` (list of all candidate results).
        """
        arr = np.asarray(data, dtype=np.float64).ravel()
        if len(arr) < 10:
            raise ValueError("At least 10 data points are required for distribution fitting.")

        fits = []
        for dist_name in self.candidate_distributions:
            result = self._fit_distribution(dist_name, arr)
            if result is not None:
                fits.append(result)

        if not fits:
            raise RuntimeError("No distributions could be fitted to the data.")

        best = min(fits, key=lambda x: x["aic"])
        logger.debug(
            f"Best distribution: {best['distribution']}, AIC={best['aic']:.2f}"
        )
        return {
            "best_distribution": best["distribution"],
            "best_aic": round(best["aic"], 4),
            "best_params": best["params"],
            "all_fits": [
                {"distribution": f["distribution"], "aic": round(f["aic"], 4)}
                for f in sorted(fits, key=lambda x: x["aic"])
            ],
        }

    def compare_moments(
        self,
        real_data: Any,
        synthetic_data: Any,
    ) -> dict[str, Any]:
        """Compare moments between real and synthetic datasets.

        Args:
            real_data: Reference data array.
            synthetic_data: Synthetic data array to validate.

        Returns:
            Dict with per-moment comparisons and a ``passed`` flag.
        """
        real_arr = np.asarray(real_data, dtype=np.float64).ravel()
        synth_arr = np.asarray(synthetic_data, dtype=np.float64).ravel()

        real_m = self._compute_moments(real_arr)
        synth_m = self._compute_moments(synth_arr)

        comparisons: dict[str, Any] = {}
        for moment_name in ("mean", "std", "skewness", "kurtosis"):
            rv = real_m[moment_name]
            sv = synth_m[moment_name]
            tol = self.moment_tolerances.get(moment_name, 0.5)
            rel_err = abs(rv - sv) / (abs(rv) + 1e-9)
            comparisons[moment_name] = {
                "real": round(rv, 6),
                "synthetic": round(sv, 6),
                "relative_error": round(rel_err, 6),
                "tolerance": tol,
                "passed": rel_err <= tol,
            }

        overall = all(v["passed"] for v in comparisons.values())
        logger.debug(f"Moment comparison: overall_passed={overall}")
        return {"passed": overall, "moments": comparisons}
