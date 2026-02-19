"""Sequence anomaly detection using statistical and isolation-forest-like methods."""
from __future__ import annotations
import math
import random
import logging
import statistics
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AnomalyConfig:
    window_size: int = 20
    threshold_sigma: float = 3.0
    n_estimators: int = 50
    max_samples: int = 256
    contamination: float = 0.05
    random_seed: int = 42


@dataclass
class AnomalyScore:
    index: int
    value: float
    score: float
    is_anomaly: bool
    method: str


class WindowedDetector:
    """Sliding-window statistics-based detector."""

    def __init__(self, config: AnomalyConfig) -> None:
        self.config = config
        self._baseline_mean: float = 0.0
        self._baseline_std: float = 1.0

    def fit(self, normal_data: List[float]) -> None:
        logger.debug("WindowedDetector fitting on %d samples", len(normal_data))
        self._baseline_mean = statistics.mean(normal_data)
        self._baseline_std = statistics.stdev(normal_data) if len(normal_data) > 1 else 1.0

    def score(self, sequence: List[float]) -> List[float]:
        scores = []
        for i, val in enumerate(sequence):
            window = sequence[max(0, i - self.config.window_size): i + 1]
            local_mean = statistics.mean(window) if window else self._baseline_mean
            local_std = (statistics.stdev(window) if len(window) > 1
                         else self._baseline_std)
            z = abs(val - local_mean) / (local_std + 1e-9)
            norm_z = abs(val - self._baseline_mean) / (self._baseline_std + 1e-9)
            scores.append(max(z, norm_z) / (self.config.threshold_sigma + 1e-9))
        return scores


class IsolationTree:
    """Single isolation tree using random feature splits."""

    def __init__(self, max_depth: int, rng: random.Random) -> None:
        self.max_depth = max_depth
        self.rng = rng
        self._splits: List[float] = []

    def fit(self, data: List[float]) -> None:
        self._splits = []
        lo, hi = min(data), max(data)
        for _ in range(self.max_depth):
            if lo >= hi:
                break
            split = self.rng.uniform(lo, hi)
            self._splits.append(split)
            mid = statistics.median(data)
            if split < mid:
                lo = split
            else:
                hi = split

    def path_length(self, value: float) -> int:
        depth = 0
        for split in self._splits:
            depth += 1
            if value <= split:
                break
        return depth


class IsolationForestDetector:
    """Isolation forest anomaly scoring."""

    def __init__(self, config: AnomalyConfig) -> None:
        self.config = config
        self.rng = random.Random(config.random_seed)
        self.trees: List[IsolationTree] = []
        self._avg_path: float = 1.0

    def _avg_path_length(self, n: int) -> float:
        if n <= 1:
            return 1.0
        return 2 * (math.log(n - 1) + 0.5772156649) - (2 * (n - 1) / n)

    def fit(self, normal_data: List[float]) -> None:
        logger.debug("IsolationForest fitting with %d estimators", self.config.n_estimators)
        sample_size = min(len(normal_data), self.config.max_samples)
        max_depth = int(math.ceil(math.log2(sample_size + 1)))
        self.trees = []
        for _ in range(self.config.n_estimators):
            sample = self.rng.choices(normal_data, k=sample_size)
            tree = IsolationTree(max_depth, self.rng)
            tree.fit(sample)
            self.trees.append(tree)
        self._avg_path = self._avg_path_length(sample_size)

    def score(self, sequence: List[float]) -> List[float]:
        scores = []
        for val in sequence:
            avg_len = statistics.mean(t.path_length(val) for t in self.trees) if self.trees else 1.0
            anomaly_score = 2 ** (-avg_len / (self._avg_path + 1e-9))
            scores.append(anomaly_score)
        return scores


class AnomalyDetector:
    def __init__(self, config: Optional[AnomalyConfig] = None) -> None:
        self.config = config or AnomalyConfig()
        self.windowed = WindowedDetector(self.config)
        self.isolation = IsolationForestDetector(self.config)
        self._threshold: float = 0.6
        logger.info("AnomalyDetector initialised: %s", self.config)

    def fit(self, normal_data: List[float]) -> None:
        logger.info("Fitting AnomalyDetector on %d samples", len(normal_data))
        self.windowed.fit(normal_data)
        self.isolation.fit(normal_data)
        iso_scores = self.isolation.score(normal_data)
        win_scores = self.windowed.score(normal_data)
        combined = [(i + w) / 2 for i, w in zip(iso_scores, win_scores)]
        self._threshold = sorted(combined)[int(len(combined) * (1 - self.config.contamination))]
        logger.info("Threshold set to %.4f", self._threshold)

    def detect(self, sequence: List[float]) -> List[AnomalyScore]:
        logger.info("Detecting anomalies in sequence of length %d", len(sequence))
        iso_scores = self.isolation.score(sequence)
        win_scores = self.windowed.score(sequence)
        results = []
        for idx, (val, i_s, w_s) in enumerate(zip(sequence, iso_scores, win_scores)):
            combined = (i_s + w_s) / 2
            results.append(AnomalyScore(
                index=idx,
                value=val,
                score=round(combined, 4),
                is_anomaly=combined > self._threshold,
                method="ensemble",
            ))
        return results

    def batch_detect(self, sequences: List[List[float]]) -> List[List[AnomalyScore]]:
        logger.info("Batch detecting over %d sequences", len(sequences))
        return [self.detect(seq) for seq in sequences]

    def get_threshold(self) -> float:
        return self._threshold
