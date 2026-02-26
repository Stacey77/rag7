"""
Health Monitoring Demo

Demonstrates the Resolver Agent's health monitoring capabilities
including per-agent metrics, alerts, and failure prediction.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from agents.base_agent import AgentState, AgentStatus, BaseAgent
from agents.resolver_agent import ResolverAgent
from resolver.health_monitor import HealthMonitor


def demo_individual_agent_monitoring():
    print("\n=== Individual Agent Health Monitoring ===")
    monitor = HealthMonitor()

    # Simulate different agent health scenarios
    scenarios = {
        "perception": {"cpu_usage": 20.0, "memory_usage": 30.0,
                       "response_time": 0.05, "error_count": 0, "task_count": 100},
        "planning":   {"cpu_usage": 45.0, "memory_usage": 60.0,
                       "response_time": 1.8, "error_count": 2, "task_count": 50},
        "control":    {"cpu_usage": 85.0, "memory_usage": 40.0,
                       "response_time": 0.1, "error_count": 0, "task_count": 200},
        "communication": {"cpu_usage": 15.0, "memory_usage": 20.0,
                          "response_time": 0.2, "error_count": 8, "task_count": 80},
    }

    for agent_name, metrics in scenarios.items():
        state = AgentState(name=agent_name)
        for k, v in metrics.items():
            setattr(state, k, v)
        monitor.update_agent_health(agent_name, state)
        health = monitor.get_agent_health(agent_name)
        print(f"  {agent_name:15s}: {health['status'].upper():10s} "
              f"CPU={health['cpu_usage']:5.1f}%  "
              f"RT={health['response_time']:.2f}s")


def demo_system_health_report():
    print("\n=== System Health Report ===")
    monitor = HealthMonitor()

    for agent_name, (cpu, rt) in [
        ("perception", (20.0, 0.1)),
        ("planning", (50.0, 0.5)),
        ("control", (90.0, 0.05)),   # Critical: high CPU
    ]:
        state = AgentState(name=agent_name)
        state.cpu_usage = cpu
        state.response_time = rt
        monitor.update_agent_health(agent_name, state)

    report = monitor.generate_health_report()
    print(f"  Overall status: {report['overall_status'].upper()}")
    print(f"  Monitored agents: {report['total_agents']}")
    print(f"  Active alerts: {len(report['alerts'])}")
    for alert in report["alerts"]:
        print(f"    ⚠️  {alert['message']}")


def demo_full_resolver_health():
    print("\n=== Resolver Agent Health Dashboard Data ===")

    class _DummyAgent(BaseAgent):
        def __init__(self, name, priority=0):
            super().__init__(name, priority)
        def on_start(self): pass
        def on_stop(self): pass
        def execute(self, task): return {}

    resolver = ResolverAgent()
    agents = [
        _DummyAgent("perception", 5),
        _DummyAgent("planning", 4),
        _DummyAgent("control", 3),
        _DummyAgent("communication", 2),
        _DummyAgent("coordination", 1),
    ]
    for agent in agents:
        agent.start()
    resolver.integrate_with_agents(agents)
    resolver.start()

    health = resolver.generate_health_report()
    print(f"  Overall: {health['overall_status'].upper()}")
    print(f"  Generated: {health['report_generated_at']}")
    print("  Agents:")
    for name, data in health["agents"].items():
        print(f"    {name:15s}: {data.get('status', 'unknown').upper()}")

    resolver.stop()
    for agent in agents:
        agent.stop()
    print("\nDemo completed successfully!")


if __name__ == "__main__":
    demo_individual_agent_monitoring()
    demo_system_health_report()
    demo_full_resolver_health()
