"""Metrics collection and aggregation system."""
from __future__ import annotations
import logging
import math
import statistics
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    name: str = ""
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MetricSummary:
    name: str = ""
    count: int = 0
    mean: float = 0.0
    std: float = 0.0
    min_val: float = 0.0
    max_val: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    rate: float = 0.0   # per second
    computed_at: datetime = field(default_factory=datetime.utcnow)


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    idx = max(0, int(len(sorted_values) * p) - 1)
    return sorted_values[idx]


class Counter:
    def __init__(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.labels = labels or {}
        self._value: float = 0.0
        self._created_at: float = time.monotonic()

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    @property
    def value(self) -> float:
        return self._value

    @property
    def rate(self) -> float:
        elapsed = time.monotonic() - self._created_at
        return self._value / max(elapsed, 0.001)


class Gauge:
    def __init__(self, name: str, labels: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.labels = labels or {}
        self._value: float = 0.0

    def set(self, value: float) -> None:
        self._value = value

    def inc(self, amount: float = 1.0) -> None:
        self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        self._value -= amount

    @property
    def value(self) -> float:
        return self._value


class Histogram:
    def __init__(self, name: str, buckets: Optional[List[float]] = None,
                 labels: Optional[Dict[str, str]] = None) -> None:
        self.name = name
        self.labels = labels or {}
        self.buckets = sorted(buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0])
        self._observations: deque = deque(maxlen=10000)
        self._sum: float = 0.0
        self._count: int = 0
        self._bucket_counts: Dict[float, int] = {b: 0 for b in self.buckets}
        self._bucket_counts[math.inf] = 0

    def observe(self, value: float) -> None:
        self._observations.append(value)
        self._sum += value
        self._count += 1
        for b in self.buckets:
            if value <= b:
                self._bucket_counts[b] += 1
        self._bucket_counts[math.inf] += 1

    def summary(self) -> MetricSummary:
        obs = sorted(self._observations)
        if not obs:
            return MetricSummary(name=self.name)
        return MetricSummary(
            name=self.name,
            count=len(obs),
            mean=statistics.mean(obs),
            std=statistics.stdev(obs) if len(obs) > 1 else 0.0,
            min_val=obs[0],
            max_val=obs[-1],
            p50=_percentile(obs, 0.5),
            p95=_percentile(obs, 0.95),
            p99=_percentile(obs, 0.99),
        )


class Timer:
    """Context manager for measuring elapsed time."""

    def __init__(self, histogram: Histogram) -> None:
        self._histogram = histogram
        self._start: Optional[float] = None

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *_: Any) -> None:
        if self._start is not None:
            elapsed = time.perf_counter() - self._start
            self._histogram.observe(elapsed)


class MetricsRegistry:
    """
    Central metrics registry for counters, gauges, and histograms
    with Prometheus-style exposition and time-series querying.
    """

    def __init__(self, namespace: str = "platform") -> None:
        self.namespace = namespace
        self._counters: Dict[str, Counter] = {}
        self._gauges: Dict[str, Gauge] = {}
        self._histograms: Dict[str, Histogram] = {}
        self._time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        logger.info("MetricsRegistry initialized (namespace=%s)", namespace)

    def _full_name(self, name: str) -> str:
        return f"{self.namespace}_{name}" if self.namespace else name

    def counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> Counter:
        full = self._full_name(name)
        if full not in self._counters:
            self._counters[full] = Counter(full, labels)
        return self._counters[full]

    def gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> Gauge:
        full = self._full_name(name)
        if full not in self._gauges:
            self._gauges[full] = Gauge(full, labels)
        return self._gauges[full]

    def histogram(self, name: str, buckets: Optional[List[float]] = None,
                   labels: Optional[Dict[str, str]] = None) -> Histogram:
        full = self._full_name(name)
        if full not in self._histograms:
            self._histograms[full] = Histogram(full, buckets, labels)
        return self._histograms[full]

    def timer(self, name: str) -> Timer:
        h = self.histogram(name)
        return Timer(h)

    def record(self, name: str, value: float) -> None:
        self._time_series[self._full_name(name)].append(
            MetricPoint(name=name, value=value))

    def snapshot(self) -> Dict[str, Any]:
        snap: Dict[str, Any] = {}
        for name, c in self._counters.items():
            snap[name] = {"type": "counter", "value": c.value, "rate": c.rate}
        for name, g in self._gauges.items():
            snap[name] = {"type": "gauge", "value": g.value}
        for name, h in self._histograms.items():
            s = h.summary()
            snap[name] = {"type": "histogram", "count": s.count, "mean": s.mean,
                          "p95": s.p95, "p99": s.p99}
        return snap

    def expose_prometheus(self) -> str:
        lines: List[str] = []
        for name, c in self._counters.items():
            lines += [f"# TYPE {name} counter", f"{name} {c.value}"]
        for name, g in self._gauges.items():
            lines += [f"# TYPE {name} gauge", f"{name} {g.value}"]
        for name, h in self._histograms.items():
            s = h.summary()
            lines += [f"# TYPE {name} histogram",
                      f"{name}_count {s.count}", f"{name}_sum {h._sum}",
                      f"{name}_p50 {s.p50}", f"{name}_p95 {s.p95}", f"{name}_p99 {s.p99}"]
        return "\n".join(lines)
