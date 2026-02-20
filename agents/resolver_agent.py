"""
Resolver Agent - The 6th Agent: System Mediator and Health Guardian.

Responsibilities:
- Conflict resolution between agents
- Error detection and recovery
- Deadlock detection and breaking
- Resource arbitration
- Priority management
- System health monitoring
- Fallback strategy execution
"""

import logging
import threading
import time
from typing import Any, Dict, List, Optional

from agents.base_agent import AgentMessage, AgentStatus, BaseAgent
from resolver.arbitrator import AgentArbitrator
from resolver.conflict_resolution import ConflictDetector, ConflictResolver
from resolver.deadlock_detector import DeadlockDetector
from resolver.error_recovery import ErrorRecoverySystem
from resolver.fallback_planner import FallbackPlanner
from resolver.health_monitor import HealthMonitor


class ResolverAgent(BaseAgent):
    """
    The 6th Agent: System Resolver and Health Guardian.

    This agent monitors all other agents, resolves conflicts, handles errors
    gracefully, and ensures the system continues operating even when problems arise.
    """

    AGENT_NAME = "resolver"
    AGENT_PRIORITY = 6  # Highest priority - can override all others

    def __init__(self):
        super().__init__(name=self.AGENT_NAME, priority=self.AGENT_PRIORITY)
        self.conflict_detector = ConflictDetector()
        self.conflict_resolver = ConflictResolver()
        self.error_handler = ErrorRecoverySystem()
        self.arbitrator = AgentArbitrator()
        self.health_monitor = HealthMonitor()
        self.deadlock_detector = DeadlockDetector()
        self.fallback_planner = FallbackPlanner()
        self._monitored_agents: Dict[str, BaseAgent] = {}
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_interval: float = 1.0  # seconds between health checks

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def on_start(self) -> None:
        """Start background monitoring thread."""
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True, name="resolver-monitor"
        )
        self._monitor_thread.start()
        self.logger.info("Resolver Agent started - monitoring %d agents",
                         len(self._monitored_agents))

    def on_stop(self) -> None:
        """Stop background monitoring thread."""
        if self._monitor_thread and self._monitor_thread.is_alive():
            # The daemon thread will stop with the process; signal the loop
            self._running = False
        self.logger.info("Resolver Agent stopped")

    # ------------------------------------------------------------------ #
    # Agent integration
    # ------------------------------------------------------------------ #

    def integrate_with_agents(self, agents: List[BaseAgent]) -> None:
        """Connect resolver to a list of agents for monitoring and arbitration."""
        for agent in agents:
            self._monitored_agents[agent.name] = agent
            self.connect_agent(agent)
            agent.connect_agent(self)
            self.health_monitor.register_agent(agent.name)
            self.logger.info("Integrated with agent: %s", agent.name)

    def start_monitoring(self) -> None:
        """Start the resolver and all monitoring sub-systems."""
        if not self._running:
            self.start()

    # ------------------------------------------------------------------ #
    # Monitoring loop
    # ------------------------------------------------------------------ #

    def _monitoring_loop(self) -> None:
        """Background loop that continuously monitors all registered agents."""
        while self._running:
            try:
                self.monitor_agents()
                time.sleep(self._monitor_interval)
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.error("Error in monitoring loop: %s", exc)

    def monitor_agents(self) -> Dict[str, Any]:
        """Monitor all registered agents and return a status summary."""
        results: Dict[str, Any] = {}
        for agent_name, agent in self._monitored_agents.items():
            try:
                state = agent.get_state()
                self.health_monitor.update_agent_health(agent_name, state)
                results[agent_name] = {
                    "status": state.status.value,
                    "last_heartbeat": state.last_heartbeat,
                    "error_count": state.error_count,
                }
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.warning("Failed to monitor agent '%s': %s", agent_name, exc)
                results[agent_name] = {"status": "unreachable", "error": str(exc)}

        # Check for conflicts and deadlocks
        conflicts = self.detect_conflicts()
        for conflict in conflicts:
            self.resolve_conflict(conflict)

        deadlock = self.deadlock_detector.detect()
        if deadlock:
            self.break_deadlock(deadlock)

        return results

    # ------------------------------------------------------------------ #
    # Conflict management
    # ------------------------------------------------------------------ #

    def detect_conflicts(self) -> List[Dict[str, Any]]:
        """Detect active conflicts between agents."""
        agent_states = {
            name: agent.get_state()
            for name, agent in self._monitored_agents.items()
        }
        return self.conflict_detector.detect_all(agent_states)

    def resolve_conflict(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a conflict between agents and return the resolution."""
        self.logger.info("Resolving conflict: %s", conflict.get("type", "unknown"))
        resolution = self.conflict_resolver.resolve(conflict)

        # Notify involved agents of the resolution
        for agent_name in conflict.get("agents", []):
            if agent_name in self._monitored_agents:
                self.send_message(
                    recipient=agent_name,
                    message_type="conflict_resolution",
                    payload={"conflict": conflict, "resolution": resolution},
                    priority=self.AGENT_PRIORITY,
                )
        return resolution

    # ------------------------------------------------------------------ #
    # Error recovery
    # ------------------------------------------------------------------ #

    def recover_from_error(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an error and attempt recovery. Returns the recovery result."""
        self.logger.warning(
            "Recovering from error: type=%s, severity=%s",
            error.get("type", "unknown"),
            error.get("severity", "unknown"),
        )
        return self.error_handler.execute_recovery(error)

    # ------------------------------------------------------------------ #
    # Resource arbitration
    # ------------------------------------------------------------------ #

    def arbitrate_resources(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Decide resource allocation when multiple agents request the same resource."""
        return self.arbitrator.arbitrate_resource_allocation(requests)

    # ------------------------------------------------------------------ #
    # Deadlock management
    # ------------------------------------------------------------------ #

    def detect_deadlock(self) -> Optional[Dict[str, Any]]:
        """Detect deadlocks among monitored agents."""
        return self.deadlock_detector.detect()

    def break_deadlock(self, deadlock: Dict[str, Any]) -> Dict[str, Any]:
        """Break a detected deadlock."""
        self.logger.warning("Breaking deadlock: %s", deadlock)
        return self.deadlock_detector.break_deadlock(deadlock)

    # ------------------------------------------------------------------ #
    # Health assessment
    # ------------------------------------------------------------------ #

    def assess_system_health(self) -> Dict[str, Any]:
        """Check and return the overall system health status."""
        agent_health = {}
        for agent_name in self._monitored_agents:
            agent_health[agent_name] = self.health_monitor.get_agent_health(agent_name)

        overall = self.health_monitor.compute_overall_status(agent_health)
        alerts = self.health_monitor.get_active_alerts()

        return {
            "overall_status": overall,
            "agents": agent_health,
            "alerts": alerts,
            "timestamp": time.time(),
        }

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate a detailed health report for the entire system."""
        health = self.assess_system_health()
        health["report_generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        health["monitored_agents_count"] = len(self._monitored_agents)
        return health

    # ------------------------------------------------------------------ #
    # Fallback execution
    # ------------------------------------------------------------------ #

    def execute_fallback(self, failure: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a fallback strategy in response to a failure."""
        self.logger.info("Executing fallback for failure: %s", failure.get("type", "unknown"))
        plan = self.fallback_planner.plan_fallback(failure)
        return self.fallback_planner.execute_fallback(plan)

    # ------------------------------------------------------------------ #
    # Dashboard
    # ------------------------------------------------------------------ #

    def launch_dashboard(self, port: int = 8080) -> None:
        """Launch the health monitoring web dashboard."""
        from dashboard.health_dashboard import HealthDashboard  # pylint: disable=import-outside-toplevel
        dashboard = HealthDashboard(resolver_agent=self, port=port)
        dashboard.run()

    # ------------------------------------------------------------------ #
    # BaseAgent interface
    # ------------------------------------------------------------------ #

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a resolver task (dispatched by task type)."""
        task_type = task.get("type", "")
        dispatch: Dict[str, Any] = {
            "resolve_conflict": lambda: self.resolve_conflict(task.get("conflict", {})),
            "recover_error": lambda: self.recover_from_error(task.get("error", {})),
            "arbitrate": lambda: self.arbitrate_resources(task.get("requests", [])),
            "health_check": lambda: self.assess_system_health(),
            "detect_deadlock": lambda: self.detect_deadlock(),
            "execute_fallback": lambda: self.execute_fallback(task.get("failure", {})),
        }
        handler = dispatch.get(task_type)
        if handler is None:
            return {"error": f"Unknown task type: {task_type}"}
        return handler()
