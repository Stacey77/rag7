"""
Tests for the health monitoring module.
"""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resolver.health_monitor import AgentHealthRecord, HealthMonitor, HealthStatus
from agents.base_agent import AgentState


class TestHealthMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = HealthMonitor()

    def _make_state(self, **kwargs) -> AgentState:
        state = AgentState(name=kwargs.get("name", "test_agent"))
        for k, v in kwargs.items():
            if k != "name":
                setattr(state, k, v)
        return state

    def test_register_agent(self):
        self.monitor.register_agent("perception")
        self.assertIn("perception", self.monitor._records)

    def test_update_agent_health_auto_registers(self):
        state = self._make_state(name="planning", cpu_usage=10.0)
        self.monitor.update_agent_health("planning", state)
        self.assertIn("planning", self.monitor._records)

    def test_healthy_agent_status(self):
        state = self._make_state(
            name="control",
            cpu_usage=20.0,
            memory_usage=30.0,
            response_time=0.1,
            error_count=0,
            task_count=10,
        )
        self.monitor.update_agent_health("control", state)
        health = self.monitor.get_agent_health("control")
        self.assertEqual(health["status"], HealthStatus.HEALTHY.value)

    def test_degraded_agent_status_slow_response(self):
        state = self._make_state(
            name="control",
            response_time=2.0,
            error_count=0,
            task_count=1,
        )
        self.monitor.update_agent_health("control", state)
        health = self.monitor.get_agent_health("control")
        self.assertEqual(health["status"], HealthStatus.DEGRADED.value)

    def test_critical_agent_status_high_cpu(self):
        state = self._make_state(name="control", cpu_usage=95.0)
        self.monitor.update_agent_health("control", state)
        health = self.monitor.get_agent_health("control")
        self.assertEqual(health["status"], HealthStatus.CRITICAL.value)

    def test_unknown_agent_not_registered(self):
        health = self.monitor.get_agent_health("nonexistent")
        self.assertEqual(health["status"], HealthStatus.UNKNOWN.value)

    def test_compute_overall_healthy(self):
        agent_health = {
            "a": {"status": "healthy"},
            "b": {"status": "healthy"},
        }
        status = self.monitor.compute_overall_status(agent_health)
        self.assertEqual(status, HealthStatus.HEALTHY.value)

    def test_compute_overall_degraded(self):
        agent_health = {
            "a": {"status": "healthy"},
            "b": {"status": "degraded"},
        }
        status = self.monitor.compute_overall_status(agent_health)
        self.assertEqual(status, HealthStatus.DEGRADED.value)

    def test_compute_overall_critical_overrides_degraded(self):
        agent_health = {
            "a": {"status": "degraded"},
            "b": {"status": "critical"},
        }
        status = self.monitor.compute_overall_status(agent_health)
        self.assertEqual(status, HealthStatus.CRITICAL.value)

    def test_generate_health_report_structure(self):
        self.monitor.register_agent("test")
        report = self.monitor.generate_health_report()
        self.assertIn("overall_status", report)
        self.assertIn("agents", report)
        self.assertIn("alerts", report)
        self.assertIn("generated_at", report)

    def test_alert_generated_on_high_cpu(self):
        state = self._make_state(name="planning", cpu_usage=90.0)
        self.monitor.update_agent_health("planning", state)
        alerts = self.monitor.get_active_alerts()
        self.assertTrue(any(a["metric"] == "cpu_usage" for a in alerts))

    def test_alert_generated_on_slow_response(self):
        state = self._make_state(name="planning", response_time=3.0)
        self.monitor.update_agent_health("planning", state)
        alerts = self.monitor.get_active_alerts()
        self.assertTrue(any(a["metric"] == "response_time" for a in alerts))

    def test_predict_failures_empty(self):
        predictions = self.monitor.predict_failures()
        self.assertEqual(predictions, [])

    def test_predict_failures_high_error_rate(self):
        state = self._make_state(name="control", error_count=10, task_count=100)
        self.monitor.update_agent_health("control", state)
        predictions = self.monitor.predict_failures()
        self.assertTrue(any(p["agent"] == "control" for p in predictions))

    def test_monitor_system_health_multiple_agents(self):
        for name in ["perception", "planning", "control"]:
            self.monitor.register_agent(name)
        system_health = self.monitor.monitor_system_health()
        self.assertEqual(len(system_health), 3)


if __name__ == "__main__":
    unittest.main()
