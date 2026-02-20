"""Time-series anomaly detection using Z-score and IQR methods."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np
from loguru import logger


@dataclass
class TimeSeriesAnomalyResult:
    """Result of a time-series anomaly detection run.

    Attributes:
        metric_name: Name of the evaluated metric.
        method: Detection method used (``"zscore"`` or ``"iqr"``).
        anomaly_indices: Indices of detected anomalies in the input array.
        anomaly_scores: Corresponding anomaly scores.
        threshold: Detection threshold used.
        n_anomalies: Total number of anomalies detected.
        detected_at: UTC timestamp.
    """

    metric_name: str
    method: str
    anomaly_indices: list[int]
    anomaly_scores: list[float]
    threshold: float
    n_anomalies: int
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class TimeSeriesAnomaly:
    """Z-score and IQR based anomaly detection for system metrics.

    Provides two complementary methods:
    - **Z-score**: Robust for roughly Gaussian metrics (CPU, memory).
    - **IQR**: Robust for skewed or heavy-tailed metrics (latency, errors).

    Attributes:
        detection_history: All past detection results.
        _zscore_threshold: Z-score threshold for anomaly classification.
        _iqr_multiplier: IQR multiplier for fence calculation.
    """

    def __init__(
        self,
        zscore_threshold: float = 3.0,
        iqr_multiplier: float = 1.5,
    ) -> None:
        """Initialise the time-series anomaly detector.

        Args:
            zscore_threshold: Z-score absolute value above which a point is
                anomalous (default 3.0 = ~0.3% false positive rate).
            iqr_multiplier: Multiplier for IQR fence (1.5 = mild, 3.0 = extreme).
        """
        self.detection_history: list[TimeSeriesAnomalyResult] = []
        self._zscore_threshold = zscore_threshold
        self._iqr_multiplier = iqr_multiplier
        logger.info(
            "TimeSeriesAnomaly initialised (zscore={}, iqr_mult={})",
            zscore_threshold,
            iqr_multiplier,
        )

    def detect_zscore(
        self,
        data: np.ndarray,
        metric_name: str = "metric",
        threshold: float | None = None,
    ) -> TimeSeriesAnomalyResult:
        """Detect anomalies using a modified Z-score (median-based).

        Uses the median absolute deviation (MAD) for robustness against
        existing outliers corrupting the mean/std estimates.

        Args:
            data: 1-D array of metric values (time-ordered).
            metric_name: Name for labelling the result.
            threshold: Override the default Z-score threshold.

        Returns:
            :class:`TimeSeriesAnomalyResult` with detected anomaly indices.

        Raises:
            ValueError: If ``data`` has fewer than 5 samples.
        """
        data = np.asarray(data, dtype=float)
        if len(data) < 5:
            raise ValueError(f"data must have ≥5 samples, got {len(data)}")

        threshold = threshold or self._zscore_threshold
        median = float(np.median(data))
        mad = float(np.median(np.abs(data - median)))
        mad_std = mad * 1.4826  # Consistency factor for normal distribution

        if mad_std < 1e-10:
            # All values identical — no anomalies
            z_scores = np.zeros(len(data))
        else:
            z_scores = np.abs(data - median) / mad_std

        anomaly_mask = z_scores > threshold
        anomaly_indices = list(np.where(anomaly_mask)[0].astype(int))
        anomaly_scores = [round(float(z_scores[i]), 4) for i in anomaly_indices]

        result = TimeSeriesAnomalyResult(
            metric_name=metric_name,
            method="zscore",
            anomaly_indices=anomaly_indices,
            anomaly_scores=anomaly_scores,
            threshold=threshold,
            n_anomalies=len(anomaly_indices),
        )
        self.detection_history.append(result)

        if anomaly_indices:
            logger.warning(
                "Z-score: {} anomalies in '{}' at indices {}",
                len(anomaly_indices),
                metric_name,
                anomaly_indices[:10],
            )
        else:
            logger.debug("Z-score: no anomalies in '{}'", metric_name)

        return result

    def detect_iqr(
        self,
        data: np.ndarray,
        metric_name: str = "metric",
        multiplier: float | None = None,
    ) -> TimeSeriesAnomalyResult:
        """Detect anomalies using the IQR (Tukey fence) method.

        Args:
            data: 1-D array of metric values (time-ordered).
            metric_name: Name for labelling the result.
            multiplier: Override the default IQR multiplier.

        Returns:
            :class:`TimeSeriesAnomalyResult` with detected anomaly indices.

        Raises:
            ValueError: If ``data`` has fewer than 5 samples.
        """
        data = np.asarray(data, dtype=float)
        if len(data) < 5:
            raise ValueError(f"data must have ≥5 samples, got {len(data)}")

        mult = multiplier or self._iqr_multiplier
        q1, q3 = float(np.percentile(data, 25)), float(np.percentile(data, 75))
        iqr = q3 - q1
        lower_fence = q1 - mult * iqr
        upper_fence = q3 + mult * iqr

        anomaly_mask = (data < lower_fence) | (data > upper_fence)
        anomaly_indices = list(np.where(anomaly_mask)[0].astype(int))

        # Score = normalised distance outside the fence
        scores: list[float] = []
        for i in anomaly_indices:
            if data[i] < lower_fence:
                score = (lower_fence - data[i]) / (iqr + 1e-10)
            else:
                score = (data[i] - upper_fence) / (iqr + 1e-10)
            scores.append(round(float(score), 4))

        result = TimeSeriesAnomalyResult(
            metric_name=metric_name,
            method="iqr",
            anomaly_indices=anomaly_indices,
            anomaly_scores=scores,
            threshold=mult,
            n_anomalies=len(anomaly_indices),
        )
        self.detection_history.append(result)

        if anomaly_indices:
            logger.warning(
                "IQR: {} anomalies in '{}' (fences [{:.2f}, {:.2f}])",
                len(anomaly_indices),
                metric_name,
                lower_fence,
                upper_fence,
            )
        else:
            logger.debug(
                "IQR: no anomalies in '{}' (fences [{:.2f}, {:.2f}])",
                metric_name,
                lower_fence,
                upper_fence,
            )

        return result

    def detect_rolling_zscore(
        self,
        data: np.ndarray,
        metric_name: str = "metric",
        window: int = 20,
        threshold: float | None = None,
    ) -> TimeSeriesAnomalyResult:
        """Detect anomalies using a rolling window Z-score.

        Suitable for non-stationary time series where the baseline drifts.

        Args:
            data: 1-D array of metric values.
            metric_name: Metric label.
            window: Rolling window size.
            threshold: Z-score threshold override.

        Returns:
            :class:`TimeSeriesAnomalyResult`.

        Raises:
            ValueError: If ``len(data) < window``.
        """
        data = np.asarray(data, dtype=float)
        if len(data) < window:
            raise ValueError(f"data length {len(data)} < window {window}")

        threshold = threshold or self._zscore_threshold
        z_scores = np.zeros(len(data))

        for i in range(window, len(data)):
            window_data = data[i - window: i]
            w_mean = float(np.mean(window_data))
            w_std = float(np.std(window_data, ddof=1)) + 1e-10
            z_scores[i] = abs((data[i] - w_mean) / w_std)

        anomaly_mask = z_scores > threshold
        anomaly_indices = list(np.where(anomaly_mask)[0].astype(int))
        anomaly_scores = [round(float(z_scores[i]), 4) for i in anomaly_indices]

        result = TimeSeriesAnomalyResult(
            metric_name=metric_name,
            method="rolling_zscore",
            anomaly_indices=anomaly_indices,
            anomaly_scores=anomaly_scores,
            threshold=threshold,
            n_anomalies=len(anomaly_indices),
        )
        self.detection_history.append(result)
        logger.debug(
            "Rolling Z-score: {} anomalies in '{}'", len(anomaly_indices), metric_name
        )
        return result
