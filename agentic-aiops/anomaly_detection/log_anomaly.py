"""Log pattern anomaly detection using frequency analysis."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class LogAnomaly:
    """A detected anomalous log pattern.

    Attributes:
        pattern: The anomalous log pattern or message template.
        frequency: How often this pattern appeared in the current window.
        expected_frequency: Expected frequency from the baseline.
        frequency_ratio: current / expected (>1 = more common, <1 = less common).
        anomaly_score: Normalised anomaly score (0–1).
        is_anomaly: Whether this pattern is classified as anomalous.
        sample_messages: Up to 3 example raw log lines.
        detected_at: UTC timestamp.
    """

    pattern: str
    frequency: int
    expected_frequency: float
    frequency_ratio: float
    anomaly_score: float
    is_anomaly: bool
    sample_messages: list[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Regex templates for normalising log messages into patterns
_NORMALISATION_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "<IP>"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE), "<UUID>"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?\b"), "<TIMESTAMP>"),
    (re.compile(r"\b\d+\b"), "<NUM>"),
    (re.compile(r'"[^"]{0,200}"'), "<STR>"),
]


class LogAnomalyDetector:
    """Log pattern anomaly detection using frequency-based analysis.

    Maintains a baseline pattern frequency distribution and detects
    new log windows that deviate significantly.

    Attributes:
        baseline_frequencies: Pattern → expected frequency per window.
        detection_history: All past detection results.
        _z_threshold: Z-score threshold for frequency anomalies.
        _new_pattern_threshold: Fraction of messages in new patterns
            above which a new-pattern alert fires.
    """

    def __init__(
        self,
        z_threshold: float = 3.0,
        new_pattern_threshold: float = 0.1,
    ) -> None:
        """Initialise the log anomaly detector.

        Args:
            z_threshold: Z-score threshold for frequency anomalies.
            new_pattern_threshold: Fraction of new patterns that triggers
                an alert.
        """
        self.baseline_frequencies: dict[str, float] = {}
        self.detection_history: list[LogAnomaly] = []
        self._z_threshold = z_threshold
        self._new_pattern_threshold = new_pattern_threshold
        self._baseline_std: dict[str, float] = {}
        logger.info("LogAnomalyDetector initialised (z={}, new_pat={})", z_threshold, new_pattern_threshold)

    def build_baseline(self, log_lines: list[str]) -> dict[str, float]:
        """Build a frequency baseline from a reference log corpus.

        Args:
            log_lines: List of reference log message strings.

        Returns:
            Mapping of pattern → mean frequency count.

        Raises:
            ValueError: If ``log_lines`` is empty.
        """
        if not log_lines:
            raise ValueError("log_lines must not be empty")

        patterns = [self._normalise(line) for line in log_lines]
        counts = Counter(patterns)
        total = len(log_lines)

        # Store as fraction for normalised comparison
        self.baseline_frequencies = {
            pat: count / total for pat, count in counts.items()
        }
        # Use a heuristic std: assume Poisson-like (std ≈ sqrt(mean))
        self._baseline_std = {
            pat: max(1e-4, (freq / total) ** 0.5 / total)
            for pat, freq in counts.items()
        }
        logger.info("Baseline built: {} unique patterns from {} lines", len(counts), total)
        return dict(self.baseline_frequencies)

    def detect(
        self,
        log_lines: list[str],
        *,
        return_all: bool = False,
    ) -> list[LogAnomaly]:
        """Detect anomalous patterns in a new log window.

        Args:
            log_lines: Current log lines to analyse.
            return_all: If ``True``, return results for all patterns (not
                just anomalies).

        Returns:
            List of :class:`LogAnomaly` for detected anomalies
            (or all patterns if ``return_all=True``).

        Raises:
            RuntimeError: If no baseline has been built yet.
            ValueError: If ``log_lines`` is empty.
        """
        if not self.baseline_frequencies:
            raise RuntimeError("Baseline not built. Call build_baseline() first.")
        if not log_lines:
            raise ValueError("log_lines must not be empty")

        total = len(log_lines)
        patterns = [self._normalise(line) for line in log_lines]
        current_counts = Counter(patterns)
        current_freqs = {pat: count / total for pat, count in current_counts.items()}

        # Sample messages per pattern
        sample_map: dict[str, list[str]] = {}
        for line, pat in zip(log_lines, patterns):
            if pat not in sample_map:
                sample_map[pat] = []
            if len(sample_map[pat]) < 3:
                sample_map[pat].append(line[:200])

        results: list[LogAnomaly] = []
        new_pattern_count = 0

        all_patterns = set(self.baseline_frequencies) | set(current_freqs)

        for pattern in all_patterns:
            current_freq = current_freqs.get(pattern, 0.0)
            expected_freq = self.baseline_frequencies.get(pattern, 0.0)
            raw_count = current_counts.get(pattern, 0)

            is_new = pattern not in self.baseline_frequencies
            if is_new:
                new_pattern_count += 1

            # Anomaly score based on normalised deviation
            if expected_freq < 1e-10:
                score = min(1.0, current_freq * 10.0) if current_freq > 0 else 0.0
                is_anomaly = current_freq > self._new_pattern_threshold
            else:
                ratio = current_freq / expected_freq
                score = min(1.0, abs(ratio - 1.0))
                std = self._baseline_std.get(pattern, 1e-4)
                z = abs((current_freq - expected_freq) / std)
                is_anomaly = z > self._z_threshold

            ratio = current_freq / (expected_freq + 1e-10)
            anomaly = LogAnomaly(
                pattern=pattern[:200],
                frequency=raw_count,
                expected_frequency=round(expected_freq * total, 2),
                frequency_ratio=round(float(ratio), 4),
                anomaly_score=round(score, 4),
                is_anomaly=is_anomaly,
                sample_messages=sample_map.get(pattern, []),
            )
            if is_anomaly or return_all:
                results.append(anomaly)

        # Check for new pattern rate
        new_rate = new_pattern_count / max(len(all_patterns), 1)
        if new_rate > self._new_pattern_threshold:
            logger.warning(
                "High new pattern rate: {:.1%} ({} new patterns)",
                new_rate,
                new_pattern_count,
            )

        anomalies = [r for r in results if r.is_anomaly]
        self.detection_history.extend(anomalies)

        if anomalies:
            logger.warning("{} log anomalies detected in {} lines", len(anomalies), total)
        else:
            logger.debug("No log anomalies in {} lines", total)

        return results if return_all else anomalies

    def _normalise(self, line: str) -> str:
        """Normalise a log line into a pattern by replacing variable parts.

        Args:
            line: Raw log message.

        Returns:
            Normalised pattern string.
        """
        result = line.strip()
        for pattern, replacement in _NORMALISATION_RULES:
            result = pattern.sub(replacement, result)
        return result[:200]  # Truncate for memory efficiency
