"""
Tests for the Resolver Agent.
"""

import sys
import os
import time
import unittest

# Ensure the repo root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agents.base_agent import AgentState, AgentStatus, BaseAgent
from agents.resolver_agent import ResolverAgent


# ---------------------------------------------------------------------------
# Minimal concrete agent for tests
# ---------------------------------------------------------------------------

class _DummyAgent(BaseAgent):
    def __init__(self, name: str, priority: int = 0):
        super().__init__(name=name, priority=priority)

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def execute(self, task):
        return {"done": True}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestResolverAgentInit(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()

    def test_name_and_priority(self):
        self.assertEqual(self.resolver.name, "resolver")
        self.assertEqual(self.resolver.priority, 6)

    def test_components_initialized(self):
        self.assertIsNotNone(self.resolver.conflict_detector)
        self.assertIsNotNone(self.resolver.conflict_resolver)
        self.assertIsNotNone(self.resolver.error_handler)
        self.assertIsNotNone(self.resolver.arbitrator)
        self.assertIsNotNone(self.resolver.health_monitor)
        self.assertIsNotNone(self.resolver.deadlock_detector)
        self.assertIsNotNone(self.resolver.fallback_planner)


class TestResolverAgentIntegration(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()
        self.perception = _DummyAgent("perception", priority=5)
        self.planning = _DummyAgent("planning", priority=4)
        self.control = _DummyAgent("control", priority=3)

    def test_integrate_with_agents(self):
        agents = [self.perception, self.planning, self.control]
        self.resolver.integrate_with_agents(agents)
        self.assertIn("perception", self.resolver._monitored_agents)
        self.assertIn("planning", self.resolver._monitored_agents)
        self.assertIn("control", self.resolver._monitored_agents)

    def test_integrate_connects_resolver_to_agents(self):
        self.resolver.integrate_with_agents([self.perception])
        self.assertIn("resolver", self.perception._connected_agents)


class TestResolverConflictHandling(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()
        self.resolver.integrate_with_agents([
            _DummyAgent("perception"),
            _DummyAgent("planning"),
        ])

    def test_resolve_conflict_returns_dict(self):
        conflict = {
            "type": "control",
            "agents": ["perception", "planning"],
            "description": "Test conflict",
        }
        result = self.resolver.resolve_conflict(conflict)
        self.assertIsInstance(result, dict)
        self.assertIn("winning_agent", result)

    def test_detect_conflicts_returns_list(self):
        conflicts = self.resolver.detect_conflicts()
        self.assertIsInstance(conflicts, list)


class TestResolverErrorRecovery(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()

    def test_recover_from_sensor_error(self):
        error = {"type": "sensor_failure", "sensor": "camera", "severity": 2}
        result = self.resolver.recover_from_error(error)
        self.assertIsInstance(result, dict)
        self.assertIn("recovery_action", result)

    def test_recover_from_agent_crash(self):
        error = {"type": "agent_crash", "agent": "planning", "severity": 3}
        result = self.resolver.recover_from_error(error)
        self.assertIn("recovery_action", result)


class TestResolverResourceArbitration(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()

    def test_arbitrate_resources_returns_allocation(self):
        requests = [
            {"agent": "perception", "resource": "GPU", "priority": 5},
            {"agent": "planning", "resource": "GPU", "priority": 4},
        ]
        result = self.resolver.arbitrate_resources(requests)
        self.assertIsInstance(result, dict)
        allocation = result.get("allocation", {})
        self.assertIn("GPU", allocation)
        self.assertEqual(allocation["GPU"], "perception")


class TestResolverHealthAssessment(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()
        self.resolver.integrate_with_agents([
            _DummyAgent("perception"),
            _DummyAgent("planning"),
        ])
        # Start agents so they report HEALTHY
        for agent in self.resolver._monitored_agents.values():
            agent.start()

    def tearDown(self):
        for agent in self.resolver._monitored_agents.values():
            agent.stop()

    def test_assess_system_health_returns_dict(self):
        health = self.resolver.assess_system_health()
        self.assertIsInstance(health, dict)
        self.assertIn("overall_status", health)
        self.assertIn("agents", health)
        self.assertIn("alerts", health)

    def test_generate_health_report_has_timestamp(self):
        report = self.resolver.generate_health_report()
        self.assertIn("report_generated_at", report)


class TestResolverDeadlockDetection(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()

    def test_detect_deadlock_no_deadlock(self):
        result = self.resolver.detect_deadlock()
        self.assertIsNone(result)

    def test_break_deadlock(self):
        self.resolver.deadlock_detector.update_wait_graph("A", ["B"])
        self.resolver.deadlock_detector.update_wait_graph("B", ["A"])
        deadlock = self.resolver.detect_deadlock()
        self.assertIsNotNone(deadlock)
        result = self.resolver.break_deadlock(deadlock)
        self.assertTrue(result.get("success"))


class TestResolverFallbackExecution(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()

    def test_execute_fallback_navigation(self):
        failure = {"type": "navigation", "depth": 0}
        result = self.resolver.execute_fallback(failure)
        self.assertIsInstance(result, dict)
        self.assertIn("executed_steps", result)
        self.assertTrue(result.get("success"))


class TestResolverExecuteDispatch(unittest.TestCase):
    def setUp(self):
        self.resolver = ResolverAgent()

    def test_execute_health_check(self):
        result = self.resolver.execute({"type": "health_check"})
        self.assertIn("overall_status", result)

    def test_execute_unknown_task(self):
        result = self.resolver.execute({"type": "nonexistent"})
        self.assertIn("error", result)

    def test_execute_detect_deadlock(self):
        result = self.resolver.execute({"type": "detect_deadlock"})
        self.assertIsNone(result)  # no deadlock in fresh state

    def test_execute_resolve_conflict(self):
        task = {
            "type": "resolve_conflict",
            "conflict": {"type": "control", "agents": ["planning", "control"]},
        }
        result = self.resolver.execute(task)
        self.assertIn("strategy", result)


if __name__ == "__main__":
    unittest.main()
