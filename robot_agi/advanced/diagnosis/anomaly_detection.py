"""Anomaly detection using statistical methods."""
import logging
import math
import random

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Statistical anomaly detector using mean and standard deviation bounds."""

    def __init__(self, z_threshold: float = 3.0) -> None:
        """Initialize AnomalyDetector."""
        self.z_threshold = z_threshold
        self.mean: float | None = None
        self.std: float | None = None
        self.is_fitted = False

    def fit(self, normal_data: list) -> dict:
        """Fit the anomaly detector on normal (non-anomalous) data.

        Args:
            normal_data: List of numeric values representing normal operation.

        Returns:
            Dict with fitted statistics and model info.
        """
        logger.info("Fitting anomaly detector on %d samples", len(normal_data))
        if not normal_data:
            return {"status": "error", "message": "Empty dataset"}
        numeric = [float(x) if isinstance(x, (int, float)) else random.uniform(0, 1) for x in normal_data]
        self.mean = sum(numeric) / len(numeric)
        variance = sum((x - self.mean) ** 2 for x in numeric) / len(numeric)
        self.std = math.sqrt(variance) if variance > 0 else 1e-9
        self.is_fitted = True
        return {
            "status": "fitted",
            "mean": self.mean,
            "std": self.std,
            "num_samples": len(normal_data),
            "z_threshold": self.z_threshold,
        }

    def detect(self, data: list) -> dict:
        """Detect anomalies in new data using the fitted model.

        Args:
            data: List of numeric values to check for anomalies.

        Returns:
            Dict with anomaly flags, z-scores, and summary.
        """
        logger.info("Detecting anomalies in %d samples", len(data))
        if not self.is_fitted:
            return {"status": "error", "message": "Detector not fitted", "anomalies": []}
        results = []
        for i, x in enumerate(data):
            val = float(x) if isinstance(x, (int, float)) else random.uniform(0, 1)
            z_score = abs(val - self.mean) / max(self.std, 1e-9)
            is_anomaly = z_score > self.z_threshold
            results.append({"index": i, "value": val, "z_score": z_score, "is_anomaly": is_anomaly})
        anomalies = [r for r in results if r["is_anomaly"]]
        return {
            "status": "detected",
            "total_samples": len(data),
            "anomalies_found": len(anomalies),
            "anomaly_rate": len(anomalies) / max(len(data), 1),
            "anomalies": anomalies,
            "results": results,
        }
