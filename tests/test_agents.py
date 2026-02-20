"""
Unit tests for the agents module of the rag7 AGI Robotics Framework.
"""

import sys
import os

# Ensure the project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest

from agents.base_agent import AgentState, BaseAgent
from agents.communication_agent import CommunicationAgent
from agents.control_agent import ControlAgent
from agents.coordination_agent import CoordinationAgent
from agents.perception_agent import PerceptionAgent
from agents.planning_agent import PlanningAgent
from agents.robotics_agi import RoboticsAGI


# ---------------------------------------------------------------------------
# Concrete minimal subclass used to test BaseAgent in isolation
# ---------------------------------------------------------------------------


class _ConcreteAgent(BaseAgent):
    """Minimal concrete BaseAgent subclass for testing."""

    def perceive(self, observation):
        return observation

    def reason(self, context):
        return {"context": context}

    def act(self, action):
        return {"executed": action}


# ===========================================================================
# TestBaseAgent
# ===========================================================================


class TestBaseAgent:
    """Tests for BaseAgent abstract base class."""

    def test_instantiation(self):
        """Concrete subclass should instantiate without errors."""
        agent = _ConcreteAgent("test_agent", {})
        assert agent.name == "test_agent"

    def test_update_state(self):
        """update_state should store key-value pairs in state dict."""
        agent = _ConcreteAgent("a", {})
        agent.update_state("key", 42)
        assert agent.state["key"] == 42

    def test_add_and_get_memory(self):
        """Memory should store and return items in FIFO order."""
        agent = _ConcreteAgent("a", {})
        agent.add_to_memory("item1")
        agent.add_to_memory("item2")
        mem = agent.get_memory(n=2)
        assert "item1" in mem
        assert "item2" in mem

    def test_clear_memory(self):
        """clear_memory should remove all stored items."""
        agent = _ConcreteAgent("a", {})
        agent.add_to_memory("x")
        agent.clear_memory()
        assert agent.get_memory() == []

    def test_register_and_get_tools(self):
        """Registered tools should be retrievable via get_tools."""
        agent = _ConcreteAgent("a", {})

        def dummy_tool():
            pass

        agent.register_tool(dummy_tool)
        assert dummy_tool in agent.get_tools()

    def test_memory_capacity(self):
        """Memory should not exceed configured capacity."""
        agent = _ConcreteAgent("a", {"memory_capacity": 3})
        for i in range(10):
            agent.add_to_memory(i)
        assert len(agent.memory) <= 3


# ===========================================================================
# TestPerceptionAgent
# ===========================================================================


class TestPerceptionAgent:
    """Tests for PerceptionAgent."""

    @pytest.fixture
    def agent(self):
        return PerceptionAgent(config={"confidence_threshold": 0.5})

    def test_perceive_with_image(self, agent):
        """perceive should return detections when given a mock image."""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = agent.perceive({"image": image})
        assert "detections" in result
        assert isinstance(result["detections"], list)

    def test_perceive_with_lidar(self, agent):
        """perceive should return nearest_obstacle from LiDAR data."""
        lidar = [5.0, 3.0, 2.0, 1.5, 4.0]
        result = agent.perceive({"lidar": lidar})
        assert result["nearest_obstacle"] == pytest.approx(1.5)

    def test_perceive_with_imu(self, agent):
        """perceive should extract orientation from IMU data."""
        imu = {"roll": 0.1, "pitch": 0.2, "yaw": 0.3}
        result = agent.perceive({"imu": imu})
        assert result["orientation"]["yaw"] == pytest.approx(0.3)

    def test_perceive_empty_observation(self, agent):
        """perceive should return valid defaults for an empty observation."""
        result = agent.perceive({})
        assert "detections" in result
        assert "orientation" in result

    def test_reason(self, agent):
        """reason should return a scene description dict."""
        agent.perceive({"lidar": [5.0, 6.0, 7.0]})
        scene = agent.reason(None)
        assert "scene_description" in scene
        assert "safe_to_proceed" in scene

    def test_act_update_threshold(self, agent):
        """act should update the confidence threshold."""
        result = agent.act({"type": "update_threshold", "value": 0.8})
        assert result["status"] == "ok"


# ===========================================================================
# TestPlanningAgent
# ===========================================================================


class TestPlanningAgent:
    """Tests for PlanningAgent."""

    @pytest.fixture
    def agent(self):
        return PlanningAgent(config={})

    def test_create_plan_navigate(self, agent):
        """create_plan should return steps for a navigation task."""
        plan = agent.create_plan("navigate to the kitchen")
        assert isinstance(plan, list)
        assert len(plan) >= 2
        assert all("step_id" in s for s in plan)

    def test_create_plan_grasp(self, agent):
        """create_plan should return steps for a grasp task."""
        plan = agent.create_plan("grasp the bottle")
        assert isinstance(plan, list)
        assert len(plan) >= 2

    def test_plan_decomposition_generic(self, agent):
        """_decompose_task should return a non-empty generic plan."""
        steps = agent._decompose_task("unknown complex task")
        assert len(steps) >= 1

    def test_reason_returns_plan(self, agent):
        """reason should produce a plan dict with num_steps key."""
        result = agent.reason("navigate to room A")
        assert "plan" in result
        assert result["num_steps"] > 0

    def test_act_advances_plan(self, agent):
        """act should execute steps sequentially."""
        agent.reason("navigate somewhere")
        result = agent.act({})
        assert result["status"] in ("executing", "plan_complete", "no_plan")


# ===========================================================================
# TestControlAgent
# ===========================================================================


class TestControlAgent:
    """Tests for ControlAgent."""

    @pytest.fixture
    def agent(self):
        return ControlAgent(config={"position_tolerance": 0.05}, ros2_enabled=False)

    def test_navigate_to(self, agent):
        """navigate_to should return True and update position."""
        success = agent.navigate_to(3.0, 4.0, 0.0)
        assert success is True
        assert agent.state["position"]["x"] == pytest.approx(3.0)

    def test_execute_grasp(self, agent):
        """execute_grasp should return True and record the object."""
        success = agent.execute_grasp("bottle_01")
        assert success is True
        assert agent.state["grasped_object"] == "bottle_01"

    def test_emergency_stop(self, agent):
        """emergency_stop should set is_stopped flag."""
        agent.emergency_stop()
        assert agent._is_stopped is True

    def test_navigate_blocked_by_estop(self, agent):
        """navigate_to should fail when emergency stop is active."""
        agent.emergency_stop()
        success = agent.navigate_to(1.0, 1.0, 0.0)
        assert success is False

    def test_act_navigate(self, agent):
        """act with type=navigate should navigate successfully."""
        result = agent.act({"type": "navigate", "x": 1.0, "y": 2.0, "theta": 0.0})
        assert result["success"] is True

    def test_act_stop(self, agent):
        """act with type=stop should trigger emergency stop."""
        result = agent.act({"type": "stop"})
        assert result["success"] is True
        assert agent._is_stopped is True


# ===========================================================================
# TestCommunicationAgent
# ===========================================================================


class TestCommunicationAgent:
    """Tests for CommunicationAgent."""

    @pytest.fixture
    def agent(self):
        return CommunicationAgent(config={"max_dialog_history": 5})

    def test_parse_command_navigate(self, agent):
        """parse_command should detect navigate intent."""
        result = agent.parse_command("go to the warehouse")
        assert result["intent"] == "navigate"

    def test_parse_command_grasp(self, agent):
        """parse_command should detect grasp intent."""
        result = agent.parse_command("pick up the red box")
        assert result["intent"] == "grasp"

    def test_parse_command_stop(self, agent):
        """parse_command should detect stop intent."""
        result = agent.parse_command("emergency stop now")
        assert result["intent"] == "stop"

    def test_classify_intent_navigate(self, agent):
        """classify_intent should return 'navigate' for navigation text."""
        assert agent.classify_intent("move to position A") == "navigate"

    def test_classify_intent_query(self, agent):
        """classify_intent should return 'query' for status questions."""
        assert agent.classify_intent("what is the current status") == "query"

    def test_classify_intent_unknown(self, agent):
        """classify_intent should return 'unknown' for unrecognised input."""
        assert agent.classify_intent("xyzzy florp bloop") == "unknown"

    def test_generate_response(self, agent):
        """generate_response should return a non-empty string."""
        resp = agent.generate_response({"intent": "navigate"})
        assert isinstance(resp, str)
        assert len(resp) > 0


# ===========================================================================
# TestCoordinationAgent
# ===========================================================================


class TestCoordinationAgent:
    """Tests for CoordinationAgent."""

    @pytest.fixture
    def agent(self):
        return CoordinationAgent(config={"max_robots": 5})

    def test_register_agent(self, agent):
        """register_agent should add agents to the managed pool."""
        sub = _ConcreteAgent("sub1", {})
        agent.register_agent(sub)
        assert "sub1" in agent.get_agent_status()

    def test_max_capacity(self, agent):
        """Registering beyond max_robots should raise ValueError."""
        for i in range(5):
            agent.register_agent(_ConcreteAgent(f"r{i}", {}))
        with pytest.raises(ValueError):
            agent.register_agent(_ConcreteAgent("overflow", {}))

    def test_allocate_task(self, agent):
        """allocate_task should return one of the registered agents."""
        a1 = _ConcreteAgent("a1", {})
        a2 = _ConcreteAgent("a2", {})
        agent.register_agent(a1)
        agent.register_agent(a2)
        chosen = agent.allocate_task({"task_type": "navigate"}, [a1, a2])
        assert chosen in (a1, a2)

    def test_allocate_task_no_agents(self, agent):
        """allocate_task with empty pool should return None."""
        result = agent.allocate_task({"task_type": "navigate"}, [])
        assert result is None

    def test_coordinate(self, agent):
        """coordinate should return allocation dict for each task."""
        a1 = _ConcreteAgent("coord_a1", {})
        agent.register_agent(a1)
        tasks = [{"task_id": "t1", "task_type": "navigate"}]
        allocations = agent.coordinate(tasks)
        assert "t1" in allocations


# ===========================================================================
# TestRoboticsAGI
# ===========================================================================


class TestRoboticsAGI:
    """Tests for the top-level RoboticsAGI orchestrator."""

    @pytest.fixture
    def agi(self, tmp_path):
        """Create a RoboticsAGI instance pointing at the real config dir."""
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config"
        )
        return RoboticsAGI(config_path=config_path)

    def test_get_status(self, agi):
        """get_status should return a dict with 'system' key."""
        status = agi.get_status()
        assert isinstance(status, dict)
        assert status["system"] == "online"

    def test_create_task(self, agi):
        """create_task should return a dict with task_type."""
        task = agi.create_task("navigate", location={"x": 1.0, "y": 2.0})
        assert task["task_type"] == "navigate"
        assert task["location"] == {"x": 1.0, "y": 2.0}

    def test_execute_command_navigate(self, agi):
        """execute_command should handle a navigation command."""
        result = agi.execute_command("navigate to the storage area")
        assert "intent" in result
        assert result["intent"] == "navigate"

    def test_execute_command_stop(self, agi):
        """execute_command should handle a stop command."""
        result = agi.execute_command("emergency stop")
        assert result["success"] is True

    def test_execute_task_query(self, agi):
        """execute_task with type=query should return system status."""
        task = agi.create_task("query")
        result = agi.execute_task(task)
        assert result["success"] is True
