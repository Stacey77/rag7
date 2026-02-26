"""
Tests for the conflict resolution module.
"""

import sys
import os
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resolver.conflict_resolution import (
    Conflict,
    ConflictDetector,
    ConflictPredictor,
    ConflictResolver,
    ConflictType,
    Resolution,
    ResolutionStrategy,
)
from agents.base_agent import AgentState, AgentStatus


class TestConflictDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ConflictDetector()

    def test_no_conflicts_empty_states(self):
        result = self.detector.detect_all({})
        self.assertEqual(result, [])

    def test_control_conflict_detected(self):
        state_a = AgentState(name="planning")
        state_a.metadata["requesting_control"] = True
        state_b = AgentState(name="control")
        state_b.metadata["requesting_control"] = True
        conflicts = self.detector.detect_control_conflict(
            {"planning": state_a, "control": state_b}
        )
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["type"], ConflictType.CONTROL.value)
        self.assertIn("planning", conflicts[0]["agents"])
        self.assertIn("control", conflicts[0]["agents"])

    def test_task_conflict_detected(self):
        state_a = AgentState(name="coordination")
        state_a.metadata["assigned_tasks"] = ["task_1"]
        state_b = AgentState(name="planning")
        state_b.metadata["assigned_tasks"] = ["task_1"]
        conflicts = self.detector.detect_task_conflict(
            {"coordination": state_a, "planning": state_b}
        )
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["type"], ConflictType.TASK.value)

    def test_resource_conflict_detected(self):
        state_a = AgentState(name="perception")
        state_a.metadata["requested_resources"] = ["GPU"]
        state_b = AgentState(name="planning")
        state_b.metadata["requested_resources"] = ["GPU"]
        conflicts = self.detector.detect_resource_conflict(
            {"perception": state_a, "planning": state_b}
        )
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["details"]["resource"], "GPU")

    def test_perception_planning_conflict_no_disagreement(self):
        state_p = AgentState(name="perception")
        state_p.metadata["detected_objects"] = ["chair"]
        state_pl = AgentState(name="planning")
        state_pl.metadata["known_objects"] = ["chair"]
        conflicts = self.detector.detect_perception_planning_conflict(
            {"perception": state_p, "planning": state_pl}
        )
        self.assertEqual(conflicts, [])

    def test_perception_planning_conflict_with_disagreement(self):
        state_p = AgentState(name="perception")
        state_p.metadata["detected_objects"] = ["chair", "table"]
        state_pl = AgentState(name="planning")
        state_pl.metadata["known_objects"] = ["chair"]
        conflicts = self.detector.detect_perception_planning_conflict(
            {"perception": state_p, "planning": state_pl}
        )
        self.assertEqual(len(conflicts), 1)


class TestConflictResolver(unittest.TestCase):
    def setUp(self):
        self.resolver = ConflictResolver()

    def _make_conflict(self, agents=None):
        return {
            "type": ConflictType.CONTROL.value,
            "agents": agents or ["planning", "control"],
            "description": "Test conflict",
        }

    def test_resolve_by_priority(self):
        conflict = self._make_conflict(["planning", "control"])
        result = self.resolver.resolve_by_priority(conflict)
        self.assertEqual(result.winning_agent, "planning")  # priority 4 > 3

    def test_resolve_by_priority_returns_resolution(self):
        conflict = self._make_conflict()
        result = self.resolver.resolve(conflict, ResolutionStrategy.PRIORITY_BASED)
        self.assertIn("winning_agent", result)
        self.assertIn("strategy", result)

    def test_resolve_by_voting(self):
        conflict = self._make_conflict(["perception", "planning"])
        result = self.resolver.resolve_by_voting(conflict)
        self.assertEqual(result.winning_agent, "perception")  # priority 5 > 4

    def test_resolve_by_expertise_control_conflict(self):
        conflict = self._make_conflict()
        result = self.resolver.resolve_by_expertise(conflict)
        self.assertEqual(result.winning_agent, "control")

    def test_resolve_by_cost_no_options(self):
        conflict = self._make_conflict()
        result = self.resolver.resolve_by_cost(conflict)
        # Falls back to priority-based
        self.assertIsInstance(result.winning_agent, str)

    def test_resolve_by_cost_with_options(self):
        conflict = {
            "type": ConflictType.RESOURCE.value,
            "agents": ["planning", "control"],
            "details": {
                "options": [
                    {"id": "opt_a", "agent": "planning", "cost": 10},
                    {"id": "opt_b", "agent": "control", "cost": 5},
                ]
            },
        }
        result = self.resolver.resolve_by_cost(conflict)
        self.assertEqual(result.winning_agent, "control")

    def test_resolution_history_grows(self):
        conflict = self._make_conflict()
        self.resolver.resolve(conflict)
        self.resolver.resolve(conflict)
        self.assertEqual(len(self.resolver.resolution_history), 2)

    def test_resolve_no_agents(self):
        conflict = {"type": "control", "agents": []}
        result = self.resolver.resolve_by_priority(conflict)
        self.assertFalse(result.success)


class TestConflict(unittest.TestCase):
    def test_to_dict(self):
        c = Conflict(
            conflict_type=ConflictType.TASK,
            agents=["a", "b"],
            description="test",
        )
        d = c.to_dict()
        self.assertEqual(d["type"], ConflictType.TASK.value)
        self.assertEqual(d["agents"], ["a", "b"])
        self.assertIn("timestamp", d)


class TestConflictPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = ConflictPredictor()

    def test_predict_no_conflicts(self):
        predictions = self.predictor.predict({})
        self.assertEqual(predictions, [])

    def test_predict_resource_contention(self):
        state_a = AgentState(name="perception")
        state_a.metadata["requested_resources"] = ["GPU"]
        state_b = AgentState(name="planning")
        state_b.metadata["requested_resources"] = ["GPU"]
        predictions = self.predictor.predict(
            {"perception": state_a, "planning": state_b}
        )
        self.assertEqual(len(predictions), 1)
        self.assertGreater(predictions[0]["probability"], 0.5)

    def test_suggest_preventive_actions_empty(self):
        actions = self.predictor.suggest_preventive_actions({})
        self.assertEqual(actions, [])


if __name__ == "__main__":
    unittest.main()
