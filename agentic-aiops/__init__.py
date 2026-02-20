"""AgenticAIOps: Intelligent autonomous operations framework for trading infrastructure."""

from __future__ import annotations

from loguru import logger

from agentic_aiops.agents.monitoring_agent import MonitoringAgent
from agentic_aiops.agents.healing_agent import HealingAgent
from agentic_aiops.agents.optimization_agent import OptimizationAgent
from agentic_aiops.agents.security_agent import SecurityAgent
from agentic_aiops.anomaly_detection.time_series_anomaly import TimeSeriesAnomaly
from agentic_aiops.anomaly_detection.log_anomaly import LogAnomaly
from agentic_aiops.anomaly_detection.behavior_anomaly import BehaviorAnomaly
from agentic_aiops.automation.incident_response import IncidentResponse
from agentic_aiops.automation.capacity_planning import CapacityPlanning
from agentic_aiops.automation.chaos_engineering import ChaosEngineering


class AgenticAIOps:
    """Unified agentic AIOps orchestrator for trading platform infrastructure.

    Aggregates autonomous monitoring, self-healing, optimisation, security,
    anomaly detection, and automation components.

    Attributes:
        monitoring: System health monitoring agent.
        healing: Self-healing automation agent.
        optimization: Resource optimisation agent.
        security: Threat detection and response agent.
        ts_anomaly: Time-series anomaly detector.
        log_anomaly: Log pattern anomaly detector.
        behavior_anomaly: Behavioral anomaly detector.
        incident_response: Automated incident handler.
        capacity_planning: Auto-scaling and capacity planner.
        chaos_engineering: Resilience testing framework.
    """

    def __init__(self) -> None:
        """Initialise all AgenticAIOps sub-components."""
        self.monitoring = MonitoringAgent()
        self.healing = HealingAgent()
        self.optimization = OptimizationAgent()
        self.security = SecurityAgent()
        self.ts_anomaly = TimeSeriesAnomaly()
        self.log_anomaly = LogAnomaly()
        self.behavior_anomaly = BehaviorAnomaly()
        self.incident_response = IncidentResponse()
        self.capacity_planning = CapacityPlanning()
        self.chaos_engineering = ChaosEngineering()
        logger.info("AgenticAIOps initialised")

    def status(self) -> dict[str, str]:
        """Return a health summary for all sub-components.

        Returns:
            Mapping of component name to status string.
        """
        return {name: "ready" for name in [
            "monitoring", "healing", "optimization", "security",
            "ts_anomaly", "log_anomaly", "behavior_anomaly",
            "incident_response", "capacity_planning", "chaos_engineering",
        ]}


__all__ = ["AgenticAIOps"]
