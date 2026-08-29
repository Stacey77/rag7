"""Async system health monitoring agent."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any

import numpy as np
from loguru import logger


class AlertSeverity(Enum):
    """Categorical alert severity levels."""

    INFO = auto()
    WARNING = auto()
    CRITICAL = auto()


@dataclass
class HealthCheck:
    """Result of a single component health check.

    Attributes:
        component: Name of the checked component.
        healthy: Overall health flag.
        latency_ms: Check round-trip time.
        details: Additional diagnostic key-value pairs.
        checked_at: UTC timestamp.
    """

    component: str
    healthy: bool
    latency_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MetricReading:
    """A single system metric reading.

    Attributes:
        name: Metric name (e.g. ``"cpu_percent"``).
        value: Numeric metric value.
        unit: Unit string (e.g. ``"%"``, ``"bytes"``).
        host: Originating host identifier.
        collected_at: UTC timestamp.
    """

    name: str
    value: float
    unit: str
    host: str = "localhost"
    collected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Alert:
    """A monitoring alert.

    Attributes:
        alert_id: Unique identifier.
        component: Affected component.
        message: Human-readable alert description.
        severity: Alert severity level.
        metric_value: The metric value that triggered the alert.
        threshold: The threshold that was breached.
        fired_at: UTC timestamp.
        resolved: Whether the alert has been resolved.
    """

    alert_id: str
    component: str
    message: str
    severity: AlertSeverity
    metric_value: float
    threshold: float
    fired_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False


class MonitoringAgent:
    """Autonomous system health monitoring agent.

    Continuously checks component health, collects metrics, and fires
    alerts when thresholds are breached.

    Attributes:
        health_history: Log of all health check results.
        metrics_buffer: Recent metric readings (FIFO, capped).
        active_alerts: Currently open alerts keyed by alert_id.
        _thresholds: Per-metric alert thresholds.
        _buffer_size: Maximum metrics buffer size.
    """

    DEFAULT_THRESHOLDS: dict[str, float] = {
        "cpu_percent": 85.0,
        "memory_percent": 90.0,
        "disk_percent": 95.0,
        "latency_ms": 1000.0,
        "error_rate": 0.05,
    }

    def __init__(
        self,
        thresholds: dict[str, float] | None = None,
        buffer_size: int = 10_000,
    ) -> None:
        """Initialise the monitoring agent.

        Args:
            thresholds: Per-metric alert thresholds; merged with defaults.
            buffer_size: Maximum number of metric readings to retain.
        """
        self.health_history: list[HealthCheck] = []
        self.metrics_buffer: list[MetricReading] = []
        self.active_alerts: dict[str, Alert] = {}
        self._thresholds = {**self.DEFAULT_THRESHOLDS, **(thresholds or {})}
        self._buffer_size = buffer_size
        self._alert_counter = 0
        logger.info("MonitoringAgent initialised")

    async def check_health(self, components: list[str] | None = None) -> list[HealthCheck]:
        """Perform async health checks on the specified components.

        Args:
            components: Component names to check; defaults to a standard set.

        Returns:
            List of :class:`HealthCheck` results.
        """
        targets = components or ["api_gateway", "order_engine", "market_data", "database", "cache"]
        tasks = [self._check_component(c) for c in targets]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        self.health_history.extend(results)

        unhealthy = [r.component for r in results if not r.healthy]
        if unhealthy:
            logger.warning("Unhealthy components detected: {}", unhealthy)
        else:
            logger.debug("All {} components healthy", len(results))
        return results  # type: ignore[return-value]

    async def _check_component(self, component: str) -> HealthCheck:
        """Check the health of a single component.

        Args:
            component: Component identifier.

        Returns:
            :class:`HealthCheck` result.
        """
        start = time.monotonic()
        await asyncio.sleep(0)
        latency_ms = (time.monotonic() - start) * 1000

        rng = np.random.default_rng(seed=hash(component) % (2**16))
        healthy = bool(rng.random() > 0.05)  # 95% healthy baseline
        return HealthCheck(
            component=component,
            healthy=healthy,
            latency_ms=round(latency_ms * 1000, 2),  # realistic simulation
            details={"simulated": True, "response_code": 200 if healthy else 503},
        )

    async def collect_metrics(self, host: str = "localhost") -> list[MetricReading]:
        """Collect a snapshot of system metrics.

        Args:
            host: Host identifier to tag metrics with.

        Returns:
            List of :class:`MetricReading` for standard system metrics.
        """
        await asyncio.sleep(0)
        rng = np.random.default_rng(seed=int(time.monotonic() * 1000) % (2**16))

        readings = [
            MetricReading("cpu_percent", round(float(rng.uniform(20, 95)), 2), "%", host),
            MetricReading("memory_percent", round(float(rng.uniform(40, 85)), 2), "%", host),
            MetricReading("disk_percent", round(float(rng.uniform(30, 70)), 2), "%", host),
            MetricReading("network_bytes_in", round(float(rng.exponential(1e6)), 0), "bytes", host),
            MetricReading("network_bytes_out", round(float(rng.exponential(5e5)), 0), "bytes", host),
            MetricReading("latency_ms", round(float(rng.lognormal(4.0, 0.5)), 2), "ms", host),
            MetricReading("error_rate", round(float(rng.beta(1, 50)), 4), "fraction", host),
        ]

        # Buffer management
        self.metrics_buffer.extend(readings)
        overflow = len(self.metrics_buffer) - self._buffer_size
        if overflow > 0:
            self.metrics_buffer = self.metrics_buffer[overflow:]

        # Auto-fire alerts for threshold breaches
        for reading in readings:
            if reading.name in self._thresholds:
                await self.alert(reading)

        logger.debug("Collected {} metric readings from '{}'", len(readings), host)
        return readings

    async def alert(self, reading: MetricReading) -> Alert | None:
        """Fire an alert if a metric breaches its threshold.

        Args:
            reading: The metric reading to evaluate.

        Returns:
            The fired :class:`Alert`, or ``None`` if no threshold was breached.
        """
        threshold = self._thresholds.get(reading.name)
        if threshold is None or reading.value <= threshold:
            return None

        self._alert_counter += 1
        alert_id = f"alert_{self._alert_counter:06d}"
        severity = (
            AlertSeverity.CRITICAL
            if reading.value > threshold * 1.2
            else AlertSeverity.WARNING
        )

        alert = Alert(
            alert_id=alert_id,
            component=reading.host,
            message=f"{reading.name} = {reading.value}{reading.unit} exceeds threshold {threshold}",
            severity=severity,
            metric_value=reading.value,
            threshold=threshold,
        )
        self.active_alerts[alert_id] = alert
        log = logger.critical if severity == AlertSeverity.CRITICAL else logger.warning
        log("ALERT [{}] {}: {}", severity.name, alert_id, alert.message)
        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved.

        Args:
            alert_id: Identifier of the alert to resolve.

        Returns:
            ``True`` if found and resolved, ``False`` if not found.
        """
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            logger.info("Alert '{}' resolved", alert_id)
            return True
        return False
