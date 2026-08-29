"""Capacity planning with auto-scaling logic based on usage trends."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class CapacityMetrics:
    """Resource utilisation metrics for capacity planning.

    Attributes:
        component: Service or resource identifier.
        cpu_utilisation: CPU utilisation fraction (0–1).
        memory_utilisation: Memory utilisation fraction (0–1).
        request_rate: Requests per second.
        current_replicas: Current number of running instances.
        max_replicas: Configured maximum replicas.
        min_replicas: Configured minimum replicas.
        collected_at: UTC timestamp.
    """

    component: str
    cpu_utilisation: float
    memory_utilisation: float
    request_rate: float
    current_replicas: int
    max_replicas: int
    min_replicas: int = 1
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ScalingDecision:
    """An auto-scaling recommendation.

    Attributes:
        component: Target component.
        action: ``"scale_up"``, ``"scale_down"``, or ``"no_change"``.
        current_replicas: Replicas before the action.
        recommended_replicas: Recommended new replica count.
        reason: Human-readable justification.
        confidence: Decision confidence (0–1).
        decided_at: UTC timestamp.
    """

    component: str
    action: str
    current_replicas: int
    recommended_replicas: int
    reason: str
    confidence: float
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ForecastResult:
    """Resource usage forecast.

    Attributes:
        component: Forecasted component.
        horizon_hours: Forecast horizon in hours.
        forecasted_cpu: Predicted CPU utilisation per hour.
        forecasted_requests: Predicted request rate per hour.
        capacity_breach_hour: Hour index at which capacity is breached
            (None if no breach predicted).
        recommended_scale_by: Recommended additional replicas.
    """

    component: str
    horizon_hours: int
    forecasted_cpu: list[float]
    forecasted_requests: list[float]
    capacity_breach_hour: int | None
    recommended_scale_by: int


class CapacityPlanning:
    """Auto-scaling and capacity planning based on usage trends and forecasting.

    Uses linear trend extrapolation for short-horizon forecasts and
    rule-based threshold logic for scaling decisions.

    Attributes:
        metrics_history: Per-component time-series of metric snapshots.
        scaling_history: Log of all scaling decisions.
        _cpu_scale_up_threshold: CPU fraction triggering scale-up.
        _cpu_scale_down_threshold: CPU fraction triggering scale-down.
        _request_rate_scale_factor: Requests/replica target.
    """

    def __init__(
        self,
        cpu_scale_up: float = 0.75,
        cpu_scale_down: float = 0.25,
        request_rate_per_replica: float = 100.0,
    ) -> None:
        """Initialise the capacity planner.

        Args:
            cpu_scale_up: CPU utilisation fraction above which scale-up triggers.
            cpu_scale_down: CPU utilisation fraction below which scale-down triggers.
            request_rate_per_replica: Target requests/sec per replica.
        """
        self.metrics_history: dict[str, list[CapacityMetrics]] = {}
        self.scaling_history: list[ScalingDecision] = []
        self._cpu_scale_up_threshold = cpu_scale_up
        self._cpu_scale_down_threshold = cpu_scale_down
        self._request_rate_per_replica = request_rate_per_replica
        logger.info(
            "CapacityPlanning initialised (cpu_up={}, cpu_down={}, rps_per_replica={})",
            cpu_scale_up,
            cpu_scale_down,
            request_rate_per_replica,
        )

    def record_metrics(self, metrics: CapacityMetrics) -> None:
        """Record a capacity metrics snapshot.

        Args:
            metrics: Metrics snapshot to store.
        """
        component = metrics.component
        if component not in self.metrics_history:
            self.metrics_history[component] = []
        self.metrics_history[component].append(metrics)
        logger.debug(
            "Capacity metrics recorded for '{}': cpu={:.1%}, mem={:.1%}, rps={:.1f}",
            component,
            metrics.cpu_utilisation,
            metrics.memory_utilisation,
            metrics.request_rate,
        )

    def decide_scaling(self, metrics: CapacityMetrics) -> ScalingDecision:
        """Determine whether to scale a component up or down.

        Uses CPU utilisation and request rate to compute the recommended
        replica count.

        Args:
            metrics: Current resource metrics.

        Returns:
            :class:`ScalingDecision` recommendation.
        """
        component = metrics.component
        current = metrics.current_replicas

        # Compute replica target from request rate
        rps_target = max(
            metrics.min_replicas,
            int(np.ceil(metrics.request_rate / self._request_rate_per_replica)),
        )

        # Apply CPU-based adjustment
        if metrics.cpu_utilisation > self._cpu_scale_up_threshold:
            cpu_target = min(metrics.max_replicas, current + max(1, current // 2))
            reason = f"CPU at {metrics.cpu_utilisation:.1%} > {self._cpu_scale_up_threshold:.0%} threshold"
            action = "scale_up"
        elif metrics.cpu_utilisation < self._cpu_scale_down_threshold and current > metrics.min_replicas:
            cpu_target = max(metrics.min_replicas, current - 1)
            reason = f"CPU at {metrics.cpu_utilisation:.1%} < {self._cpu_scale_down_threshold:.0%} threshold"
            action = "scale_down"
        else:
            cpu_target = current
            reason = f"CPU at {metrics.cpu_utilisation:.1%} within thresholds"
            action = "no_change"

        recommended = max(rps_target, cpu_target)
        recommended = int(np.clip(recommended, metrics.min_replicas, metrics.max_replicas))

        if recommended > current:
            action = "scale_up"
        elif recommended < current:
            action = "scale_down"
        else:
            action = "no_change"
            recommended = current

        confidence = self._compute_confidence(metrics)
        decision = ScalingDecision(
            component=component,
            action=action,
            current_replicas=current,
            recommended_replicas=recommended,
            reason=reason,
            confidence=round(confidence, 4),
        )
        self.scaling_history.append(decision)
        logger.info(
            "Scaling decision for '{}': {} ({} → {} replicas)",
            component,
            action,
            current,
            recommended,
        )
        return decision

    def forecast(
        self,
        component: str,
        horizon_hours: int = 24,
    ) -> ForecastResult:
        """Forecast resource usage using linear trend extrapolation.

        Args:
            component: Component to forecast.
            horizon_hours: Number of hours ahead to forecast.

        Returns:
            :class:`ForecastResult` with per-hour predictions.

        Raises:
            ValueError: If fewer than 2 metric snapshots are available.
            KeyError: If no metrics history for this component.
        """
        if component not in self.metrics_history:
            raise KeyError(f"No metrics history for component '{component}'")

        history = self.metrics_history[component]
        if len(history) < 2:
            raise ValueError(f"Need ≥2 samples for forecasting, got {len(history)}")

        cpu_values = np.array([m.cpu_utilisation for m in history])
        rps_values = np.array([m.request_rate for m in history])
        n = len(cpu_values)
        t = np.arange(n, dtype=float)

        # Linear regression
        cpu_slope, cpu_intercept = float(np.polyfit(t, cpu_values, 1))
        rps_slope, rps_intercept = float(np.polyfit(t, rps_values, 1))

        last_metrics = history[-1]
        forecast_cpu: list[float] = []
        forecast_rps: list[float] = []
        breach_hour: int | None = None

        for h in range(horizon_hours):
            t_future = n + h
            cpu_pred = float(np.clip(cpu_slope * t_future + cpu_intercept, 0.0, 1.0))
            rps_pred = float(max(0.0, rps_slope * t_future + rps_intercept))
            forecast_cpu.append(round(cpu_pred, 4))
            forecast_rps.append(round(rps_pred, 2))

            if breach_hour is None and cpu_pred > self._cpu_scale_up_threshold:
                breach_hour = h

        max_rps = max(forecast_rps) if forecast_rps else 0.0
        recommended_scale = max(
            0,
            int(np.ceil(max_rps / self._request_rate_per_replica)) - last_metrics.current_replicas,
        )

        result = ForecastResult(
            component=component,
            horizon_hours=horizon_hours,
            forecasted_cpu=forecast_cpu,
            forecasted_requests=forecast_rps,
            capacity_breach_hour=breach_hour,
            recommended_scale_by=recommended_scale,
        )
        logger.info(
            "Forecast for '{}': horizon={}h, breach_hour={}, scale_by={}",
            component,
            horizon_hours,
            breach_hour,
            recommended_scale,
        )
        return result

    def _compute_confidence(self, metrics: CapacityMetrics) -> float:
        """Compute confidence in a scaling decision.

        Args:
            metrics: Current metrics snapshot.

        Returns:
            Confidence score (0–1).
        """
        history = self.metrics_history.get(metrics.component, [])
        n = len(history)
        # More history → higher confidence, asymptotic to 0.95
        return min(0.95, 0.5 + 0.45 * (1 - 1 / (1 + n / 10.0)))
