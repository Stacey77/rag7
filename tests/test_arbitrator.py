"""
Tests for the agent arbitrator.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resolver.arbitrator import AgentArbitrator, ArbitrationStrategy


class TestAgentArbitrator(unittest.TestCase):
    def setUp(self):
        self.arbitrator = AgentArbitrator()

    def _make_requests(self, agents):
        return [{"agent": a, "resource": "GPU", "priority": 0} for a in agents]

    # ------------------------------------------------------------------ #
    # Control arbitration
    # ------------------------------------------------------------------ #

    def test_arbitrate_control_no_requests(self):
        result = self.arbitrator.arbitrate_control_request([])
        self.assertIsNone(result["winner"])

    def test_arbitrate_control_priority_queue(self):
        requests = [
            {"agent": "planning", "priority": 0},
            {"agent": "perception", "priority": 0},
        ]
        result = self.arbitrator.arbitrate_control_request(requests)
        # perception has higher default priority (5 vs 4)
        self.assertEqual(result["winner"], "perception")

    def test_arbitrate_control_emergency_override(self):
        requests = [
            {"agent": "planning", "priority": 0, "emergency": True},
            {"agent": "coordination", "priority": 0, "emergency": True},
        ]
        result = self.arbitrator.arbitrate_control_request(requests)
        self.assertEqual(result["strategy"], ArbitrationStrategy.EMERGENCY_OVERRIDE.value)
        self.assertEqual(result["winner"], "planning")  # planning > coordination

    # ------------------------------------------------------------------ #
    # Resource allocation
    # ------------------------------------------------------------------ #

    def test_arbitrate_resource_allocation_empty(self):
        result = self.arbitrator.arbitrate_resource_allocation([])
        self.assertIsNone(result["winner"])
        self.assertEqual(result["allocation"], {})

    def test_arbitrate_resource_allocation_assigns_winner(self):
        requests = [
            {"agent": "perception", "resource": "GPU"},
            {"agent": "planning", "resource": "GPU"},
        ]
        result = self.arbitrator.arbitrate_resource_allocation(requests)
        self.assertEqual(result["allocation"]["GPU"], "perception")

    def test_arbitrate_resource_multiple_resources(self):
        requests = [
            {"agent": "perception", "resource": "GPU"},
            {"agent": "planning", "resource": "GPU"},
            {"agent": "control", "resource": "CPU"},
            {"agent": "coordination", "resource": "CPU"},
        ]
        result = self.arbitrator.arbitrate_resource_allocation(requests)
        self.assertEqual(result["allocation"]["GPU"], "perception")
        self.assertEqual(result["allocation"]["CPU"], "control")

    # ------------------------------------------------------------------ #
    # Task priority
    # ------------------------------------------------------------------ #

    def test_arbitrate_task_priority_empty(self):
        result = self.arbitrator.arbitrate_task_priority([])
        self.assertIsNone(result["winner"])

    def test_arbitrate_task_priority_orders_tasks(self):
        tasks = [
            {"id": "t1", "agent": "coordination", "priority": 1},
            {"id": "t2", "agent": "perception", "priority": 1},
            {"id": "t3", "agent": "planning", "priority": 2},
        ]
        result = self.arbitrator.arbitrate_task_priority(tasks)
        ordered = result["allocation"]["ordered_tasks"]
        # t3 has higher priority (2) so it should come first
        self.assertEqual(ordered[0], "t3")

    # ------------------------------------------------------------------ #
    # Context-aware arbitration
    # ------------------------------------------------------------------ #

    def test_arbitrate_with_context_emergency(self):
        requests = [
            {"agent": "coordination", "priority": 0},
            {"agent": "control", "priority": 0},
        ]
        result = self.arbitrator.arbitrate_with_context(requests, {"emergency": True})
        self.assertEqual(result["strategy"], ArbitrationStrategy.EMERGENCY_OVERRIDE.value)

    def test_arbitrate_with_context_normal(self):
        requests = [
            {"agent": "coordination", "priority": 0},
            {"agent": "perception", "priority": 0},
        ]
        result = self.arbitrator.arbitrate_with_context(requests, {"emergency": False})
        # Normal priority-based
        self.assertEqual(result["winner"], "perception")

    # ------------------------------------------------------------------ #
    # Default priorities
    # ------------------------------------------------------------------ #

    def test_default_priorities_resolver_highest(self):
        priorities = AgentArbitrator.DEFAULT_PRIORITIES
        self.assertEqual(priorities["resolver"], max(priorities.values()))

    def test_default_priorities_coordination_lowest(self):
        priorities = AgentArbitrator.DEFAULT_PRIORITIES
        self.assertEqual(priorities["coordination"], min(priorities.values()))


if __name__ == "__main__":
    unittest.main()
