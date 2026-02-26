"""
Integration tests for the Resolver Agent with all 5 existing agents.
"""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.base_agent import AgentState, AgentStatus, BaseAgent
from agents.resolver_agent import ResolverAgent


# ---------------------------------------------------------------------------
# Stub agents representing the 5 existing agents
# ---------------------------------------------------------------------------

class _StubAgent(BaseAgent):
    """Generic stub agent for integration tests."""

    def __init__(self, name: str, priority: int = 0):
        super().__init__(name=name, priority=priority)
        self._received_messages = []

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def execute(self, task):
        return {"done": True, "agent": self.name}

    def receive_message(self, message):
        self._received_messages.append(message)
        super().receive_message(message)


class PerceptionAgent(_StubAgent):
    def __init__(self):
        super().__init__("perception", priority=5)


class PlanningAgent(_StubAgent):
    def __init__(self):
        super().__init__("planning", priority=4)


class ControlAgent(_StubAgent):
    def __init__(self):
        super().__init__("control", priority=3)


class CommunicationAgent(_StubAgent):
    def __init__(self):
        super().__init__("communication", priority=2)


class CoordinationAgent(_StubAgent):
    def __init__(self):
        super().__init__("coordination", priority=1)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestResolverIntegration(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()
        self.perception = PerceptionAgent()
        self.planning = PlanningAgent()
        self.control = ControlAgent()
        self.communication = CommunicationAgent()
        self.coordination = CoordinationAgent()

        self.all_agents = [
            self.perception, self.planning, self.control,
            self.communication, self.coordination,
        ]
        self.resolver.integrate_with_agents(self.all_agents)

    def test_all_agents_registered(self):
        for agent in self.all_agents:
            self.assertIn(agent.name, self.resolver._monitored_agents)

    def test_resolver_registered_in_all_agents(self):
        for agent in self.all_agents:
            self.assertIn("resolver", agent._connected_agents)

    def test_monitor_agents_returns_all_statuses(self):
        result = self.resolver.monitor_agents()
        for agent in self.all_agents:
            self.assertIn(agent.name, result)

    def test_conflict_resolution_notifies_agents(self):
        conflict = {
            "type": "control",
            "agents": ["planning", "control"],
            "description": "Competing control requests",
        }
        self.resolver.resolve_conflict(conflict)
        # Both planning and control should have received a resolution message
        planning_msgs = [
            m for m in self.planning._received_messages
            if m.message_type == "conflict_resolution"
        ]
        control_msgs = [
            m for m in self.control._received_messages
            if m.message_type == "conflict_resolution"
        ]
        self.assertEqual(len(planning_msgs), 1)
        self.assertEqual(len(control_msgs), 1)

    def test_health_report_covers_all_agents(self):
        for agent in self.all_agents:
            agent.start()
        health = self.resolver.assess_system_health()
        for agent in self.all_agents:
            self.assertIn(agent.name, health["agents"])
        for agent in self.all_agents:
            agent.stop()

    def test_resource_arbitration_across_agents(self):
        requests = [
            {"agent": ag.name, "resource": "GPU"}
            for ag in self.all_agents
        ]
        result = self.resolver.arbitrate_resources(requests)
        # perception has highest priority → gets GPU
        self.assertEqual(result["allocation"]["GPU"], "perception")

    def test_error_recovery_for_each_agent(self):
        for agent in self.all_agents:
            error = {
                "type": "agent_crash",
                "agent": agent.name,
                "severity": 3,
            }
            result = self.resolver.recover_from_error(error)
            self.assertIn("recovery_action", result)

    def test_deadlock_breaking_with_agents(self):
        # Set up a circular wait
        self.resolver.deadlock_detector.update_wait_graph("planning", ["control"])
        self.resolver.deadlock_detector.update_wait_graph("control", ["planning"])
        deadlock = self.resolver.detect_deadlock()
        self.assertIsNotNone(deadlock)
        result = self.resolver.break_deadlock(deadlock)
        self.assertTrue(result["success"])

    def test_fallback_execution_for_navigation(self):
        failure = {"type": "navigation", "depth": 0}
        result = self.resolver.execute_fallback(failure)
        self.assertIn("executed_steps", result)
        self.assertTrue(result["success"])

    def test_full_task_dispatch(self):
        """Verify all execute() task types work end-to-end."""
        tasks = [
            {"type": "health_check"},
            {"type": "detect_deadlock"},
            {"type": "resolve_conflict",
             "conflict": {"type": "control", "agents": ["planning", "control"]}},
            {"type": "recover_error",
             "error": {"type": "sensor_failure", "sensor": "camera"}},
            {"type": "arbitrate",
             "requests": [{"agent": "perception", "resource": "GPU"}]},
            {"type": "execute_fallback",
             "failure": {"type": "navigation"}},
        ]
        for task in tasks:
            with self.subTest(task_type=task["type"]):
                result = self.resolver.execute(task)
                # detect_deadlock returns None when there is no deadlock (valid)
                if task["type"] != "detect_deadlock":
                    self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
