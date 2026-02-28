"""Data and model drift detection."""
from __future__ import annotations

import logging
import math
import statistics
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DriftReport:
    feature_name: str = ""
    drift_score: float = 0.0
    drift_type: str = ""        # "covariate" | "label" | "concept" | "none"
    is_drifted: bool = False
    threshold: float = 0.1
    test_statistic: float = 0.0
    test_name: str = ""
    reference_stats: Dict[str, float] = field(default_factory=dict)
    current_stats: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DriftSummary:
    drifted_features: List[str] = field(default_factory=list)
    stable_features: List[str] = field(default_factory=list)
    overall_drift_score: float = 0.0
    reports: List[DriftReport] = field(default_factory=list)
    recommendation: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


def _descriptive_stats(values: List[float]) -> Dict[str, float]:
    if not values:
        return {}
    return {
        "mean": statistics.mean(values),
        "std": statistics.stdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "median": statistics.median(values),
        "count": float(len(values)),
    }


def _ks_statistic(reference: List[float], current: List[float]) -> float:
    """Kolmogorov-Smirnov statistic (max absolute CDF difference)."""
    if not reference or not current:
        return 0.0
    all_values = sorted(set(reference + current))
    ref_sorted = sorted(reference)
    cur_sorted = sorted(current)
    n_ref, n_cur = len(ref_sorted), len(cur_sorted)
    max_diff = 0.0
    for val in all_values:
        cdf_ref = sum(1 for v in ref_sorted if v <= val) / n_ref
        cdf_cur = sum(1 for v in cur_sorted if v <= val) / n_cur
        max_diff = max(max_diff, abs(cdf_ref - cdf_cur))
    return max_diff


def _psi_score(reference: List[float], current: List[float], n_bins: int = 10) -> float:
    """Population Stability Index (PSI)."""
    if not reference or not current:
        return 0.0
    min_v = min(min(reference), min(current))
    max_v = max(max(reference), max(current))
    if max_v == min_v:
        return 0.0
    bin_width = (max_v - min_v) / n_bins
    boundaries = [min_v + i * bin_width for i in range(n_bins + 1)]

    def bin_counts(values: List[float]) -> List[float]:
        counts = [0] * n_bins
        for v in values:
            idx = min(int((v - min_v) / bin_width), n_bins - 1)
            counts[idx] += 1
        total = len(values)
        return [(c + 0.0001) / total for c in counts]

    ref_pct = bin_counts(reference)
    cur_pct = bin_counts(current)
    psi = sum((c - r) * math.log(c / r) for r, c in zip(ref_pct, cur_pct))
    return psi


def _chi_square_drift(ref_labels: List[Any], cur_labels: List[Any]) -> float:
    """Chi-square statistic normalized as drift score for categorical data."""
    ref_counts = Counter(ref_labels)
    cur_counts = Counter(cur_labels)
    all_cats = set(ref_counts) | set(cur_counts)
    n_ref, n_cur = len(ref_labels), len(cur_labels)
    if n_ref == 0 or n_cur == 0:
        return 0.0
    chi2 = 0.0
    for cat in all_cats:
        expected = ref_counts.get(cat, 0) / n_ref * n_cur
        observed = cur_counts.get(cat, 0)
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected
    # Normalize to 0-1 range
    return min(1.0, chi2 / (len(all_cats) * n_cur + 1e-9))


class CovariateShiftDetector:
    """Detects input feature distribution drift."""

    def __init__(self, ks_threshold: float = 0.1, psi_threshold: float = 0.2) -> None:
        self.ks_threshold = ks_threshold
        self.psi_threshold = psi_threshold

    def detect(self, feature_name: str, reference: List[float],
               current: List[float]) -> DriftReport:
        ks = _ks_statistic(reference, current)
        psi = _psi_score(reference, current)
        drift_score = max(ks, psi / 5)  # normalize PSI
        is_drifted = ks > self.ks_threshold or psi > self.psi_threshold

        return DriftReport(
            feature_name=feature_name,
            drift_score=drift_score,
            drift_type="covariate" if is_drifted else "none",
            is_drifted=is_drifted,
            threshold=self.ks_threshold,
            test_statistic=ks,
            test_name="KS+PSI",
            reference_stats=_descriptive_stats(reference),
            current_stats=_descriptive_stats(current),
        )


class LabelShiftDetector:
    """Detects output label distribution changes."""

    def __init__(self, threshold: float = 0.15) -> None:
        self.threshold = threshold

    def detect(self, feature_name: str, ref_labels: List[Any],
               cur_labels: List[Any]) -> DriftReport:
        score = _chi_square_drift(ref_labels, cur_labels)
        is_drifted = score > self.threshold
        return DriftReport(
            feature_name=feature_name,
            drift_score=score,
            drift_type="label" if is_drifted else "none",
            is_drifted=is_drifted,
            threshold=self.threshold,
            test_statistic=score,
            test_name="Chi-Square",
        )


class DriftDetector:
    """
    Comprehensive drift detection combining covariate shift,
    label shift, and concept drift detection.
    """

    def __init__(self, ks_threshold: float = 0.1, psi_threshold: float = 0.2,
                 label_threshold: float = 0.15) -> None:
        self._covariate = CovariateShiftDetector(ks_threshold, psi_threshold)
        self._label = LabelShiftDetector(label_threshold)
        self._reference_data: Dict[str, List[float]] = {}
        self._reference_labels: Dict[str, List[Any]] = {}
        logger.info("DriftDetector initialized")

    def set_reference(self, feature_data: Dict[str, List[float]],
                      labels: Optional[List[Any]] = None) -> None:
        self._reference_data = {k: list(v) for k, v in feature_data.items()}
        if labels:
            self._reference_labels["output"] = list(labels)
        logger.info("Reference dataset set: %d features, %d samples",
                    len(feature_data), len(next(iter(feature_data.values()), [])))

    def detect_feature_drift(self, feature_name: str,
                              current_values: List[float]) -> DriftReport:
        reference = self._reference_data.get(feature_name, [])
        if not reference:
            return DriftReport(feature_name=feature_name, drift_type="no_reference")
        return self._covariate.detect(feature_name, reference, current_values)

    def detect_label_drift(self, current_labels: List[Any]) -> DriftReport:
        reference = self._reference_labels.get("output", [])
        if not reference:
            return DriftReport(feature_name="output", drift_type="no_reference")
        return self._label.detect("output", reference, current_labels)

    def detect_all(self, current_data: Dict[str, List[float]],
                   current_labels: Optional[List[Any]] = None) -> DriftSummary:
        reports: List[DriftReport] = []
        for feature_name, values in current_data.items():
            report = self.detect_feature_drift(feature_name, values)
            reports.append(report)

        if current_labels:
            label_report = self.detect_label_drift(current_labels)
            reports.append(label_report)

        drifted = [r.feature_name for r in reports if r.is_drifted]
        stable = [r.feature_name for r in reports if not r.is_drifted]
        overall_score = sum(r.drift_score for r in reports) / max(len(reports), 1)

        if len(drifted) == 0:
            recommendation = "No drift detected. Model is stable."
        elif len(drifted) <= len(reports) * 0.3:
            recommendation = f"Minor drift in {len(drifted)} features. Monitor closely."
        else:
            recommendation = f"Significant drift in {len(drifted)}/{len(reports)} features. Consider retraining."

        return DriftSummary(
            drifted_features=drifted,
            stable_features=stable,
            overall_drift_score=overall_score,
            reports=reports,
            recommendation=recommendation,
        )

    def update_reference(self, new_data: Dict[str, List[float]],
                         blend_ratio: float = 0.2) -> None:
        """Incrementally update reference distribution."""
        for feature_name, values in new_data.items():
            existing = self._reference_data.get(feature_name, [])
            keep = int(len(existing) * (1 - blend_ratio))
            self._reference_data[feature_name] = existing[-keep:] + values
