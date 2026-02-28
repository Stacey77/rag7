"""Model performance monitoring and drift detection."""
from __future__ import annotations

import logging
import statistics
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class PredictionRecord:
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    model_version: str = ""
    input_features: Dict[str, Any] = field(default_factory=dict)
    prediction: Any = None
    ground_truth: Optional[Any] = None
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    model_name: str = ""
    model_version: str = ""
    window_size: int = 0
    accuracy: float = 0.0
    error_rate: float = 0.0
    mean_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_rps: float = 0.0
    computed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Alert:
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    alert_type: str = ""      # "performance_degradation" | "drift" | "latency" | "error_rate"
    severity: str = "warning"  # "info" | "warning" | "critical"
    message: str = ""
    metric_name: str = ""
    current_value: float = 0.0
    threshold: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False


@dataclass
class MonitoringConfig:
    accuracy_threshold: float = 0.80
    error_rate_threshold: float = 0.05
    latency_p95_threshold_ms: float = 500.0
    drift_threshold: float = 0.1
    window_size: int = 100
    alert_cooldown_seconds: int = 300


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = int(len(sorted_values) * p / 100)
    return sorted_values[min(idx, len(sorted_values) - 1)]


class MetricsCalculator:
    """Computes performance metrics from prediction records."""

    def compute(self, records: List[PredictionRecord]) -> PerformanceMetrics:
        if not records:
            return PerformanceMetrics()

        model_name = records[0].model_name
        model_version = records[0].model_version

        labeled = [r for r in records if r.ground_truth is not None]
        correct = sum(1 for r in labeled if r.prediction == r.ground_truth)
        accuracy = correct / len(labeled) if labeled else 0.0
        error_rate = 1 - accuracy if labeled else 0.0

        latencies = sorted(r.latency_ms for r in records)
        mean_lat = statistics.mean(latencies) if latencies else 0.0
        p95 = _percentile(latencies, 95)
        p99 = _percentile(latencies, 99)

        # Throughput: records per second over the window
        if len(records) >= 2:
            duration = (records[-1].timestamp - records[0].timestamp).total_seconds()
            throughput = len(records) / max(duration, 0.001)
        else:
            throughput = 0.0

        return PerformanceMetrics(
            model_name=model_name,
            model_version=model_version,
            window_size=len(records),
            accuracy=accuracy,
            error_rate=error_rate,
            mean_latency_ms=mean_lat,
            p95_latency_ms=p95,
            p99_latency_ms=p99,
            throughput_rps=throughput,
        )


class ModelMonitor:
    """
    Real-time model performance monitoring with sliding window
    metrics, threshold alerting, and performance history tracking.
    """

    def __init__(self, config: Optional[MonitoringConfig] = None) -> None:
        self._config = config or MonitoringConfig()
        self._records: Dict[str, deque] = {}           # model_name -> deque[PredictionRecord]
        self._alerts: List[Alert] = []
        self._metrics_history: Dict[str, List[PerformanceMetrics]] = {}
        self._calculator = MetricsCalculator()
        self._last_alert_time: Dict[str, datetime] = {}
        logger.info("ModelMonitor initialized")

    def log_prediction(self, model_name: str, model_version: str,
                       input_features: Dict[str, Any],
                       prediction: Any,
                       ground_truth: Optional[Any] = None,
                       latency_ms: float = 0.0) -> PredictionRecord:
        record = PredictionRecord(
            model_name=model_name,
            model_version=model_version,
            input_features=input_features,
            prediction=prediction,
            ground_truth=ground_truth,
            latency_ms=latency_ms,
        )
        if model_name not in self._records:
            self._records[model_name] = deque(maxlen=self._config.window_size * 10)
        self._records[model_name].append(record)
        return record

    def compute_metrics(self, model_name: str) -> Optional[PerformanceMetrics]:
        records = list(self._records.get(model_name, []))
        if not records:
            return None
        window = records[-self._config.window_size:]
        metrics = self._calculator.compute(window)
        self._metrics_history.setdefault(model_name, []).append(metrics)
        self._check_alerts(metrics)
        return metrics

    def _check_alerts(self, metrics: PerformanceMetrics) -> None:
        cfg = self._config
        checks = [
            ("accuracy", metrics.accuracy < cfg.accuracy_threshold,
             f"Accuracy {metrics.accuracy:.1%} below threshold {cfg.accuracy_threshold:.1%}",
             metrics.accuracy, cfg.accuracy_threshold, "warning"),
            ("error_rate", metrics.error_rate > cfg.error_rate_threshold,
             f"Error rate {metrics.error_rate:.1%} above threshold {cfg.error_rate_threshold:.1%}",
             metrics.error_rate, cfg.error_rate_threshold, "warning"),
            ("latency_p95", metrics.p95_latency_ms > cfg.latency_p95_threshold_ms,
             f"P95 latency {metrics.p95_latency_ms:.0f}ms above threshold {cfg.latency_p95_threshold_ms:.0f}ms",
             metrics.p95_latency_ms, cfg.latency_p95_threshold_ms, "critical"),
        ]
        for metric_name, triggered, message, current, threshold, severity in checks:
            if triggered:
                self._maybe_raise_alert(
                    metrics.model_name, metric_name, severity, message, current, threshold
                )

    def _maybe_raise_alert(self, model_name: str, alert_type: str, severity: str,
                            message: str, current: float, threshold: float) -> None:
        import datetime as dt
        key = f"{model_name}:{alert_type}"
        last = self._last_alert_time.get(key)
        if last:
            elapsed = (datetime.utcnow() - last).total_seconds()
            if elapsed < self._config.alert_cooldown_seconds:
                return
        alert = Alert(model_name=model_name, alert_type=alert_type, severity=severity,
                      message=message, metric_name=alert_type,
                      current_value=current, threshold=threshold)
        self._alerts.append(alert)
        self._last_alert_time[key] = datetime.utcnow()
        logger.warning("[ALERT] %s - %s: %s", severity.upper(), model_name, message)

    def get_alerts(self, model_name: Optional[str] = None,
                   severity: Optional[str] = None,
                   unresolved_only: bool = True) -> List[Alert]:
        alerts = self._alerts
        if model_name:
            alerts = [a for a in alerts if a.model_name == model_name]
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        return alerts

    def resolve_alert(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                return True
        return False

    def metrics_history(self, model_name: str, last_n: int = 10) -> List[PerformanceMetrics]:
        history = self._metrics_history.get(model_name, [])
        return history[-last_n:]

    def dashboard(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for model_name in self._records:
            metrics = self.compute_metrics(model_name)
            result[model_name] = {
                "metrics": {
                    "accuracy": metrics.accuracy if metrics else None,
                    "error_rate": metrics.error_rate if metrics else None,
                    "p95_latency_ms": metrics.p95_latency_ms if metrics else None,
                    "throughput_rps": metrics.throughput_rps if metrics else None,
                },
                "prediction_count": len(self._records[model_name]),
                "active_alerts": len(self.get_alerts(model_name)),
            }
        return result
