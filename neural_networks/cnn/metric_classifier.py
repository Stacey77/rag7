"""Metric time-series classification using CNN-simulated feature-based approach."""
from __future__ import annotations
import math
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class MetricSample:
    name: str
    values: List[float]
    label: str = "unknown"


@dataclass
class TimeSeriesFeatures:
    mean: float
    std: float
    trend: float
    min_val: float
    max_val: float
    range_val: float
    autocorr: float
    seasonality: float

    def as_list(self) -> List[float]:
        return [self.mean, self.std, self.trend, self.min_val,
                self.max_val, self.range_val, self.autocorr, self.seasonality]


def extract_features(values: List[float]) -> TimeSeriesFeatures:
    if not values:
        return TimeSeriesFeatures(0, 0, 0, 0, 0, 0, 0, 0)
    n = len(values)
    mean = statistics.mean(values)
    std = statistics.stdev(values) if n > 1 else 0.0
    min_val, max_val = min(values), max(values)
    range_val = max_val - min_val
    xs = list(range(n))
    x_mean = statistics.mean(xs)
    num = sum((x - x_mean) * (y - mean) for x, y in zip(xs, values))
    denom = sum((x - x_mean) ** 2 for x in xs) + 1e-9
    trend = num / denom
    if n > 1:
        lag1 = values[1:]
        lag0 = values[:-1]
        ac_num = sum((a - mean) * (b - mean) for a, b in zip(lag0, lag1))
        ac_denom = sum((v - mean) ** 2 for v in values) + 1e-9
        autocorr = ac_num / ac_denom
    else:
        autocorr = 0.0
    period = max(2, n // 4)
    seasonality = 0.0
    if n >= period * 2:
        seasonal_pairs = [(values[i], values[i + period]) for i in range(n - period)]
        diffs = [abs(a - b) for a, b in seasonal_pairs]
        seasonality = 1.0 / (statistics.mean(diffs) + 1e-9) if diffs else 0.0
        seasonality = min(1.0, seasonality / (range_val + 1e-9))
    return TimeSeriesFeatures(mean=mean, std=std, trend=trend,
                               min_val=min_val, max_val=max_val,
                               range_val=range_val, autocorr=autocorr,
                               seasonality=seasonality)


class CNNClassifier:
    """Feature-based classifier with 1D conv simulation."""

    def __init__(self, kernel_size: int = 3) -> None:
        self.kernel_size = kernel_size
        self._centroids: Dict[str, List[float]] = {}

    @staticmethod
    def _cosine_sim(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) + 1e-9
        nb = math.sqrt(sum(x * x for x in b)) + 1e-9
        return dot / (na * nb)

    def _sliding_pool(self, values: List[float]) -> List[float]:
        if len(values) < self.kernel_size:
            return values
        return [sum(values[i: i + self.kernel_size]) / self.kernel_size
                for i in range(len(values) - self.kernel_size + 1)]

    def fit(self, samples: List[MetricSample]) -> None:
        logger.info("CNNClassifier fitting on %d samples", len(samples))
        by_label: Dict[str, List[List[float]]] = defaultdict(list)
        for s in samples:
            pooled = self._sliding_pool(s.values)
            feats = extract_features(pooled).as_list()
            by_label[s.label].append(feats)
        for label, feat_list in by_label.items():
            min_len = min(len(f) for f in feat_list)
            centroid = [statistics.mean(f[d] for f in feat_list)
                        for d in range(min_len)]
            self._centroids[label] = centroid
        logger.info("CNNClassifier trained on labels: %s", list(self._centroids.keys()))

    def predict(self, values: List[float]) -> Tuple[str, float]:
        if not self._centroids:
            return "unknown", 0.0
        pooled = self._sliding_pool(values)
        feats = extract_features(pooled).as_list()
        best_label, best_sim = "unknown", -2.0
        for label, centroid in self._centroids.items():
            sim = self._cosine_sim(feats, centroid)
            if sim > best_sim:
                best_sim, best_label = sim, label
        conf = (best_sim + 1) / 2.0
        return best_label, round(conf, 4)


class MetricClassifier:
    def __init__(self) -> None:
        self.cnn = CNNClassifier()
        self._trained = False
        logger.info("MetricClassifier initialised")

    def fit(self, samples: List[MetricSample]) -> None:
        logger.info("MetricClassifier fitting on %d samples", len(samples))
        self.cnn.fit(samples)
        self._trained = True

    def classify(self, sample: MetricSample) -> Tuple[str, float]:
        label, conf = self.cnn.predict(sample.values)
        logger.debug("MetricClassifier: '%s' -> '%s' (%.4f)", sample.name, label, conf)
        return label, conf

    def detect_regime_change(self, values: List[float],
                              window: int = 20) -> List[int]:
        logger.info("Detecting regime changes in series of length %d", len(values))
        change_points = []
        for i in range(window, len(values) - window):
            before = values[i - window: i]
            after = values[i: i + window]
            mean_diff = abs(statistics.mean(after) - statistics.mean(before))
            std_threshold = (statistics.stdev(before) if len(before) > 1 else 1.0)
            if mean_diff > 2 * std_threshold:
                change_points.append(i)
        logger.info("Found %d regime changes", len(change_points))
        return change_points

    def compare_metrics(self, a: MetricSample,
                         b: MetricSample) -> Dict[str, float]:
        fa = extract_features(a.values)
        fb = extract_features(b.values)
        la, lb = fa.as_list(), fb.as_list()
        sim = CNNClassifier._cosine_sim(la, lb)
        mean_diff = abs(fa.mean - fb.mean)
        std_diff = abs(fa.std - fb.std)
        trend_diff = abs(fa.trend - fb.trend)
        return {
            "similarity": round(sim, 4),
            "mean_diff": round(mean_diff, 4),
            "std_diff": round(std_diff, 4),
            "trend_diff": round(trend_diff, 4),
        }
