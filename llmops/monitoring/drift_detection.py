"""Model drift detection using PSI and KS statistical tests."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class DriftReport:
    """Report from a single drift detection evaluation.

    Attributes:
        feature_name: Name of the feature that was evaluated.
        method: Statistical method used (``"psi"`` or ``"ks"``).
        statistic: Test statistic value.
        threshold: Threshold above which drift is declared.
        drift_detected: Whether drift was declared.
        severity: Categorical severity label.
        evaluated_at: UTC timestamp of evaluation.
    """

    feature_name: str
    method: str
    statistic: float
    threshold: float
    drift_detected: bool
    severity: str
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DriftDetection:
    """Model degradation and data drift detection.

    Supports Population Stability Index (PSI) for distributional shift
    and the Kolmogorov–Smirnov (KS) two-sample test for continuous
    feature drift.

    PSI severity thresholds (industry standard):
      - PSI < 0.1  → no drift
      - 0.1 ≤ PSI < 0.2 → minor drift
      - PSI ≥ 0.2  → significant drift

    Attributes:
        reference_distributions: Stored reference distributions per feature.
        drift_history: Log of all drift reports generated.
        _psi_threshold: PSI threshold for declaring drift.
        _ks_threshold: KS p-value threshold for declaring drift.
    """

    PSI_MINOR: float = 0.1
    PSI_SIGNIFICANT: float = 0.2

    def __init__(
        self,
        psi_threshold: float = 0.2,
        ks_pvalue_threshold: float = 0.05,
    ) -> None:
        """Initialise the drift detector.

        Args:
            psi_threshold: PSI score above which drift is declared.
            ks_pvalue_threshold: KS p-value below which drift is declared.
        """
        self.reference_distributions: dict[str, np.ndarray] = {}
        self.drift_history: list[DriftReport] = []
        self._psi_threshold = psi_threshold
        self._ks_threshold = ks_pvalue_threshold
        logger.info(
            "DriftDetection initialised (psi_threshold={}, ks_pvalue_threshold={})",
            psi_threshold,
            ks_pvalue_threshold,
        )

    def set_reference(self, feature_name: str, data: np.ndarray) -> None:
        """Store a reference distribution for a feature.

        Args:
            feature_name: Feature identifier.
            data: 1-D array of reference observations.

        Raises:
            ValueError: If ``data`` is not 1-D or has fewer than 30 samples.
        """
        data = np.asarray(data, dtype=float).ravel()
        if data.ndim != 1:
            raise ValueError("data must be 1-D")
        if len(data) < 30:
            raise ValueError(f"Reference requires ≥30 samples, got {len(data)}")
        self.reference_distributions[feature_name] = data
        logger.info("Reference distribution set for feature '{}' ({} samples)", feature_name, len(data))

    def compute_psi(
        self,
        feature_name: str,
        current_data: np.ndarray,
        n_bins: int = 10,
    ) -> DriftReport:
        """Compute PSI between the reference and current distributions.

        Args:
            feature_name: Feature to evaluate (must have a reference set).
            current_data: 1-D array of current observations.
            n_bins: Number of histogram buckets.

        Returns:
            :class:`DriftReport` with PSI result.

        Raises:
            KeyError: If no reference distribution exists for ``feature_name``.
            ValueError: If ``current_data`` has fewer than 10 samples.
        """
        reference = self._get_reference(feature_name)
        current_data = np.asarray(current_data, dtype=float).ravel()
        if len(current_data) < 10:
            raise ValueError(f"current_data requires ≥10 samples, got {len(current_data)}")

        psi = self._psi(reference, current_data, n_bins)
        severity = self._psi_severity(psi)
        drift_detected = psi >= self._psi_threshold

        report = DriftReport(
            feature_name=feature_name,
            method="psi",
            statistic=round(psi, 6),
            threshold=self._psi_threshold,
            drift_detected=drift_detected,
            severity=severity,
        )
        self.drift_history.append(report)
        log = logger.warning if drift_detected else logger.debug
        log(
            "PSI for '{}': {:.4f} ({}) — drift={}",
            feature_name,
            psi,
            severity,
            drift_detected,
        )
        return report

    def compute_ks(
        self,
        feature_name: str,
        current_data: np.ndarray,
    ) -> DriftReport:
        """Compute KS two-sample test between reference and current data.

        Args:
            feature_name: Feature to evaluate (must have a reference set).
            current_data: 1-D array of current observations.

        Returns:
            :class:`DriftReport` with KS statistic and approximate p-value.

        Raises:
            KeyError: If no reference distribution exists for ``feature_name``.
        """
        reference = self._get_reference(feature_name)
        current_data = np.asarray(current_data, dtype=float).ravel()

        ks_stat, p_value = self._ks_two_sample(reference, current_data)
        drift_detected = p_value < self._ks_threshold
        severity = "significant" if drift_detected else "none"

        report = DriftReport(
            feature_name=feature_name,
            method="ks",
            statistic=round(ks_stat, 6),
            threshold=self._ks_threshold,
            drift_detected=drift_detected,
            severity=severity,
        )
        self.drift_history.append(report)
        log = logger.warning if drift_detected else logger.debug
        log(
            "KS for '{}': stat={:.4f}, p={:.4f} — drift={}",
            feature_name,
            ks_stat,
            p_value,
            drift_detected,
        )
        return report

    def evaluate_all(self, current_data: dict[str, np.ndarray]) -> dict[str, DriftReport]:
        """Run PSI drift evaluation on all features with stored references.

        Args:
            current_data: Mapping of feature name to current observations.

        Returns:
            Mapping of feature name to :class:`DriftReport`.
        """
        results: dict[str, DriftReport] = {}
        for feature_name, data in current_data.items():
            if feature_name in self.reference_distributions:
                results[feature_name] = self.compute_psi(feature_name, data)
            else:
                logger.warning("No reference for feature '{}', skipping", feature_name)
        return results

    def _psi(self, reference: np.ndarray, current: np.ndarray, n_bins: int) -> float:
        """Calculate Population Stability Index.

        Args:
            reference: Reference distribution.
            current: Current distribution.
            n_bins: Number of histogram bins.

        Returns:
            PSI value.
        """
        eps = 1e-8
        bin_edges = np.percentile(reference, np.linspace(0, 100, n_bins + 1))
        bin_edges = np.unique(bin_edges)
        if len(bin_edges) < 2:
            return 0.0

        ref_counts = np.histogram(reference, bins=bin_edges)[0].astype(float)
        cur_counts = np.histogram(current, bins=bin_edges)[0].astype(float)

        ref_pct = ref_counts / (ref_counts.sum() + eps)
        cur_pct = cur_counts / (cur_counts.sum() + eps)
        psi = float(np.sum((cur_pct - ref_pct) * np.log((cur_pct + eps) / (ref_pct + eps))))
        return abs(psi)

    def _ks_two_sample(
        self, a: np.ndarray, b: np.ndarray
    ) -> tuple[float, float]:
        """Compute KS statistic and approximate p-value.

        Args:
            a: First sample.
            b: Second sample.

        Returns:
            Tuple of ``(ks_statistic, p_value)``.
        """
        a_sorted = np.sort(a)
        b_sorted = np.sort(b)
        combined = np.concatenate([a_sorted, b_sorted])
        combined = np.unique(combined)

        cdf_a = np.searchsorted(a_sorted, combined, side="right") / len(a_sorted)
        cdf_b = np.searchsorted(b_sorted, combined, side="right") / len(b_sorted)

        ks_stat = float(np.max(np.abs(cdf_a - cdf_b)))

        # Kolmogorov approximation for p-value
        n = len(a) * len(b) / (len(a) + len(b))
        lambda_val = (math.sqrt(n) + 0.12 + 0.11 / math.sqrt(n)) * ks_stat
        p_value = float(2 * sum(
            ((-1) ** (k - 1)) * math.exp(-2 * k * k * lambda_val ** 2)
            for k in range(1, 20)
        ))
        p_value = float(np.clip(p_value, 0.0, 1.0))
        return ks_stat, p_value

    def _psi_severity(self, psi: float) -> str:
        """Categorise PSI value into a severity label.

        Args:
            psi: PSI score.

        Returns:
            ``"none"``, ``"minor"``, or ``"significant"``.
        """
        if psi < self.PSI_MINOR:
            return "none"
        if psi < self.PSI_SIGNIFICANT:
            return "minor"
        return "significant"

    def _get_reference(self, feature_name: str) -> np.ndarray:
        """Retrieve a stored reference distribution.

        Args:
            feature_name: Feature identifier.

        Returns:
            Reference data array.

        Raises:
            KeyError: If no reference has been set for this feature.
        """
        if feature_name not in self.reference_distributions:
            raise KeyError(
                f"No reference distribution for feature '{feature_name}'. "
                "Call set_reference() first."
            )
        return self.reference_distributions[feature_name]
