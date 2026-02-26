"""
Health monitoring module for the Resolver Agent.

Tracks the health of all registered agents and robot systems,
generates alerts when health degrades, and provides health reports.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Possible health states for an agent or the overall system."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class AgentHealthRecord:
    """Health metrics for a single agent."""
    agent_name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    error_rate: float = 0.0
    uptime: float = 0.0
    last_updated: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "status": self.status.value,
            "response_time": self.response_time,
            "cpu_usage": self.cpu_usage,
            "memory_usage": self.memory_usage,
            "error_rate": self.error_rate,
            "uptime": self.uptime,
            "last_updated": self.last_updated,
        }


@dataclass
class Alert:
    """A health alert triggered when metrics exceed thresholds."""
    agent_name: str
    metric: str
    value: float
    threshold: float
    message: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
            "timestamp": self.timestamp,
        }


class HealthMonitor:
    """
    Monitor health of all agents and robot systems.

    Metrics tracked per agent:
    - Response time
    - CPU / memory usage
    - Error rate
    - Uptime
    - Message queue length (via metadata)
    """

    # Default alert thresholds
    RESPONSE_TIME_THRESHOLD = 1.0   # seconds
    CPU_THRESHOLD = 80.0            # percent
    MEMORY_THRESHOLD = 85.0         # percent
    ERROR_RATE_THRESHOLD = 0.1      # 10 %
    HEARTBEAT_TIMEOUT = 30.0        # seconds

    def __init__(self):
        self._records: Dict[str, AgentHealthRecord] = {}
        self._alerts: List[Alert] = []
        self._registration_time: Dict[str, float] = {}

    def register_agent(self, agent_name: str) -> None:
        """Register a new agent for health monitoring."""
        self._records[agent_name] = AgentHealthRecord(agent_name=agent_name)
        self._registration_time[agent_name] = time.time()
        logger.debug("HealthMonitor: registered agent '%s'", agent_name)

    def update_agent_health(self, agent_name: str, state: Any) -> None:
        """Update health metrics from an agent's current state."""
        if agent_name not in self._records:
            self.register_agent(agent_name)

        record = self._records[agent_name]
        record.cpu_usage = getattr(state, "cpu_usage", 0.0)
        record.memory_usage = getattr(state, "memory_usage", 0.0)
        record.response_time = getattr(state, "response_time", 0.0)
        error_count = getattr(state, "error_count", 0)
        task_count = getattr(state, "task_count", 1) or 1
        record.error_rate = error_count / task_count
        record.uptime = time.time() - self._registration_time.get(agent_name, time.time())
        record.last_updated = time.time()

        # Derive status from metrics
        record.status = self._derive_status(record)

        # Check thresholds and raise alerts
        self._check_thresholds(record)

    def get_agent_health(self, agent_name: str) -> Dict[str, Any]:
        """Return the latest health record for the given agent."""
        record = self._records.get(agent_name)
        if record is None:
            return {"agent_name": agent_name, "status": HealthStatus.UNKNOWN.value}
        return record.to_dict()

    def monitor_system_health(self) -> Dict[str, Any]:
        """Return health records for all monitored agents."""
        return {name: record.to_dict() for name, record in self._records.items()}

    def compute_overall_status(self, agent_health: Dict[str, Any]) -> str:
        """Compute the overall system status from individual agent statuses."""
        statuses = [info.get("status", HealthStatus.UNKNOWN.value)
                    for info in agent_health.values()]
        if HealthStatus.CRITICAL.value in statuses:
            return HealthStatus.CRITICAL.value
        if HealthStatus.DEGRADED.value in statuses:
            return HealthStatus.DEGRADED.value
        if all(s == HealthStatus.HEALTHY.value for s in statuses) and statuses:
            return HealthStatus.HEALTHY.value
        return HealthStatus.UNKNOWN.value

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate a comprehensive health report."""
        agent_health = self.monitor_system_health()
        return {
            "overall_status": self.compute_overall_status(agent_health),
            "agents": agent_health,
            "alerts": self.get_active_alerts(),
            "total_agents": len(self._records),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Return all currently active (un-cleared) alerts."""
        cutoff = time.time() - 300  # keep alerts for 5 minutes
        self._alerts = [a for a in self._alerts if a.timestamp > cutoff]
        return [a.to_dict() for a in self._alerts]

    def predict_failures(self) -> List[Dict[str, Any]]:
        """Predict potential failures based on current trends."""
        predictions: List[Dict[str, Any]] = []
        for name, record in self._records.items():
            if record.error_rate > 0.05:
                predictions.append({
                    "agent": name,
                    "risk": "high_error_rate",
                    "current_rate": record.error_rate,
                    "prediction": "possible_agent_failure",
                })
            if record.response_time > 0.8:
                predictions.append({
                    "agent": name,
                    "risk": "slow_response",
                    "current_time": record.response_time,
                    "prediction": "possible_timeout",
                })
        return predictions

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _derive_status(self, record: AgentHealthRecord) -> HealthStatus:
        """Determine HealthStatus from a record's metric values."""
        if (record.cpu_usage > self.CPU_THRESHOLD
                or record.memory_usage > self.MEMORY_THRESHOLD
                or record.error_rate > self.ERROR_RATE_THRESHOLD * 2):
            return HealthStatus.CRITICAL
        if (record.response_time > self.RESPONSE_TIME_THRESHOLD
                or record.error_rate > self.ERROR_RATE_THRESHOLD):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    def _check_thresholds(self, record: AgentHealthRecord) -> None:
        """Create alerts when metrics exceed defined thresholds."""
        checks = [
            ("response_time", record.response_time, self.RESPONSE_TIME_THRESHOLD,
             f"Agent '{record.agent_name}' response time {record.response_time:.2f}s "
             f"exceeds threshold {self.RESPONSE_TIME_THRESHOLD}s"),
            ("cpu_usage", record.cpu_usage, self.CPU_THRESHOLD,
             f"Agent '{record.agent_name}' CPU usage {record.cpu_usage:.1f}% "
             f"exceeds threshold {self.CPU_THRESHOLD}%"),
            ("memory_usage", record.memory_usage, self.MEMORY_THRESHOLD,
             f"Agent '{record.agent_name}' memory usage {record.memory_usage:.1f}% "
             f"exceeds threshold {self.MEMORY_THRESHOLD}%"),
            ("error_rate", record.error_rate, self.ERROR_RATE_THRESHOLD,
             f"Agent '{record.agent_name}' error rate {record.error_rate:.2%} "
             f"exceeds threshold {self.ERROR_RATE_THRESHOLD:.0%}"),
        ]
        for metric, value, threshold, message in checks:
            if value > threshold:
                alert = Alert(
                    agent_name=record.agent_name,
                    metric=metric,
                    value=value,
                    threshold=threshold,
                    message=message,
                )
                self._alerts.append(alert)
                logger.warning("ALERT: %s", message)
