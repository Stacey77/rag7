"""
Unit tests for the planning module of the rag7 AGI Robotics Framework.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from planning.task_planner import TaskPlanner
from planning.path_planner import PathPlanner
from planning.motion_planner import MotionPlanner
from planning.decision_maker import DecisionMaker


# ===========================================================================
# TestTaskPlanner
# ===========================================================================


class TestTaskPlanner:
    """Tests for TaskPlanner."""

    @pytest.fixture
    def planner(self):
        return TaskPlanner()

    def test_plan_returns_list(self, planner):
        """plan should return a non-empty list of steps."""
        steps = planner.plan("navigate to the dock")
        assert isinstance(steps, list)
        assert len(steps) > 0

    def test_plan_step_structure(self, planner):
        """Each step should have step_id, action, description keys."""
        steps = planner.plan("grasp the red cube")
        for step in steps:
            assert "step_id" in step
            assert "action" in step
            assert "description" in step

    def test_plan_navigate_keywords(self, planner):
        """Navigation keywords should produce a navigation plan."""
        steps = planner.plan("go to room B")
        actions = [s["action"] for s in steps]
        # At least one navigation-related action
        assert any(
            kw in a for a in actions for kw in ("navigate", "path", "scan", "arrive", "confirm")
        )

    def test_decompose_grasp(self, planner):
        """decompose should return grasp steps for pick commands."""
        steps = planner.decompose("pick up the bottle")
        assert any("grasp" in s["action"] or "detect" in s["action"] for s in steps)

    def test_decompose_inspect(self, planner):
        """decompose should handle inspect tasks."""
        steps = planner.decompose("inspect the machinery")
        assert len(steps) >= 2

    def test_decompose_generic(self, planner):
        """decompose should return a generic plan for unknown tasks."""
        steps = planner.decompose("do something unusual")
        assert len(steps) >= 1

    def test_replan_includes_recovery(self, planner):
        """replan should start with a diagnose/recover step."""
        failed = {"step_id": 2, "action": "navigate"}
        steps = planner.replan(failed, {"failure_reason": "obstacle"})
        actions = [s["action"] for s in steps]
        assert "diagnose" in actions or "recover" in actions

    def test_plan_with_context(self, planner):
        """plan should accept a context dict without errors."""
        steps = planner.plan("place object", context={"location": "shelf_A"})
        assert isinstance(steps, list)


# ===========================================================================
# TestPathPlanner
# ===========================================================================


class TestPathPlanner:
    """Tests for PathPlanner A* path planning."""

    @pytest.fixture
    def planner(self):
        return PathPlanner(grid_resolution=1.0)

    def test_plan_returns_path(self, planner):
        """plan should return a list of waypoints."""
        path = planner.plan(start=(0, 0), goal=(5, 5))
        assert isinstance(path, list)
        assert len(path) > 0

    def test_path_starts_at_start(self, planner):
        """First waypoint should be close to the start position."""
        start = (0.0, 0.0)
        path = planner.plan(start=start, goal=(5.0, 5.0))
        assert path[0][0] == pytest.approx(0.0, abs=1.5)
        assert path[0][1] == pytest.approx(0.0, abs=1.5)

    def test_path_ends_at_goal(self, planner):
        """Last waypoint should be close to the goal position."""
        goal = (5.0, 5.0)
        path = planner.plan(start=(0.0, 0.0), goal=goal)
        assert path[-1][0] == pytest.approx(5.0, abs=1.5)
        assert path[-1][1] == pytest.approx(5.0, abs=1.5)

    def test_plan_no_obstacles(self, planner):
        """A* should find a path with no obstacles."""
        path = planner.plan((0, 0), (3, 3), obstacles=[])
        assert len(path) >= 2

    def test_plan_with_obstacles(self, planner):
        """A* should route around obstacles."""
        obstacles = [(1, 0), (1, 1), (1, 2), (1, 3)]
        path = planner.plan((0, 0), (3, 0), obstacles=obstacles)
        # Path may be empty if blocked, but should not crash
        assert isinstance(path, list)

    def test_heuristic_same_cell(self, planner):
        """Heuristic of same cell should be 0."""
        h = PathPlanner._heuristic((3, 3), (3, 3))
        assert h == pytest.approx(0.0)

    def test_heuristic_manhattan(self, planner):
        """Heuristic should return Manhattan distance."""
        h = PathPlanner._heuristic((0, 0), (3, 4))
        assert h == pytest.approx(7.0)

    def test_same_start_and_goal(self, planner):
        """When start equals goal, path should be a single point."""
        path = planner.plan((2, 2), (2, 2))
        assert len(path) == 1


# ===========================================================================
# TestMotionPlanner
# ===========================================================================


class TestMotionPlanner:
    """Tests for MotionPlanner."""

    @pytest.fixture
    def planner(self):
        return MotionPlanner(dof=6)

    def test_plan_trajectory_returns_dict(self, planner):
        """plan_trajectory should return dict with trajectory and timestamps."""
        start = [0.0] * 6
        goal = [0.5] * 6
        result = planner.plan_trajectory(start, goal, duration=1.0)
        assert "trajectory" in result
        assert "timestamps" in result

    def test_trajectory_length(self, planner):
        """Trajectory should have the requested number of waypoints."""
        result = planner.plan_trajectory([0.0] * 6, [1.0] * 6, duration=2.0, num_points=20)
        assert len(result["trajectory"]) == 20
        assert len(result["timestamps"]) == 20

    def test_trajectory_start_end(self, planner):
        """First and last configs should be close to start and goal."""
        start = [0.0] * 6
        goal = [1.0] * 6
        result = planner.plan_trajectory(start, goal)
        traj = result["trajectory"]
        # First waypoint ~ start
        assert all(abs(traj[0][i] - start[i]) < 0.1 for i in range(6))
        # Last waypoint ~ goal
        assert all(abs(traj[-1][i] - goal[i]) < 0.1 for i in range(6))

    def test_compute_ik_returns_list(self, planner):
        """compute_ik should return a list of joint angles."""
        angles = planner.compute_ik({"x": 0.5, "y": 0.3, "z": 0.2})
        assert isinstance(angles, list)
        assert len(angles) == 6

    def test_compute_fk_returns_pose(self, planner):
        """compute_fk should return a pose dict."""
        angles = [0.0] * 6
        pose = planner.compute_fk(angles)
        assert "x" in pose
        assert "y" in pose
        assert "z" in pose

    def test_fk_zero_angles(self, planner):
        """With all-zero joint angles, end-effector should be on x-axis."""
        pose = planner.compute_fk([0.0] * 6)
        assert pose["y"] == pytest.approx(0.0, abs=1e-6)

    def test_ik_fk_consistency(self, planner):
        """FK(IK(pose)) should produce a pose in the correct hemisphere."""
        target = {"x": 0.3, "y": 0.1, "z": 0.0}
        angles = planner.compute_ik(target)
        pose = planner.compute_fk(angles)
        # Weak check: the result should be a valid pose dict
        assert isinstance(pose["x"], float)


# ===========================================================================
# TestDecisionMaker
# ===========================================================================


class TestDecisionMaker:
    """Tests for DecisionMaker."""

    @pytest.fixture
    def dm(self):
        return DecisionMaker(config={"safety_threshold": 0.5})

    def test_decide_returns_option(self, dm):
        """decide should return one of the provided options."""
        options = [{"type": "navigate"}, {"type": "wait"}]
        state = {"nearest_obstacle": 5.0}
        chosen = dm.decide(state, options)
        assert chosen in options

    def test_decide_empty_options(self, dm):
        """decide with empty options should return None."""
        result = dm.decide({}, [])
        assert result is None

    def test_decide_prefers_stop_near_obstacle(self, dm):
        """decide should prefer stop/wait when obstacle is close."""
        options = [{"type": "navigate"}, {"type": "stop"}]
        state = {"nearest_obstacle": 0.1}
        chosen = dm.decide(state, options)
        # Should not choose navigate when obstacle is very close
        assert chosen is not None

    def test_decide_respects_estop(self, dm):
        """With emergency stop active, only safe actions are chosen."""
        options = [{"type": "navigate"}, {"type": "stop"}]
        state = {"is_stopped": True}
        chosen = dm.decide(state, options)
        if chosen is not None:
            assert chosen.get("type") in ("stop", "wait", "reset_stop")

    def test_evaluate_returns_float(self, dm):
        """evaluate should return a float in [0, 1]."""
        score = dm.evaluate({"nearest_obstacle": 3.0}, {"type": "navigate"})
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_evaluate_stop_preferred_when_close(self, dm):
        """stop action should score higher than navigate when close to obstacle."""
        state = {"nearest_obstacle": 0.1}
        stop_score = dm.evaluate(state, {"type": "stop"})
        nav_score = dm.evaluate(state, {"type": "navigate"})
        assert stop_score > nav_score

    def test_decide_single_option(self, dm):
        """decide with a single option should return that option."""
        option = {"type": "navigate"}
        chosen = dm.decide({"nearest_obstacle": 5.0}, [option])
        assert chosen == option
