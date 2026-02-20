"""
Gazebo simulation environment for the rag7 AGI Robotics Framework.

Provides an OpenAI Gym-compatible interface for simulated robot
environments.  When Gazebo is not installed, the environment runs in
pure mock mode enabling development and testing without a simulator.
"""

import logging
import random
from typing import Any, Dict, Optional, Tuple

import numpy as np


class GazeboEnv:
    """Gazebo-backed (or mock) robot simulation environment.

    Implements a Gym-style interface (reset / step / render / close) for
    testing robot policies in simulation.

    Args:
        world_name: Gazebo world file name (without path or extension).
        robot_name: Name of the robot model in the simulation.
        headless: If True, run without a graphical display.
    """

    def __init__(
        self,
        world_name: str = "empty",
        robot_name: str = "robot",
        headless: bool = True,
    ) -> None:
        """Initialize the Gazebo environment."""
        self._logger = logging.getLogger("rag7.simulation.gazebo")
        self._world_name = world_name
        self._robot_name = robot_name
        self._headless = headless
        self._is_running = False
        self._step_count = 0
        self._max_steps = 1000

        # Internal mock robot state
        self._robot_state: Dict[str, Any] = {
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            "velocity": {"linear": 0.0, "angular": 0.0},
        }
        self._goal: Dict[str, float] = {"x": 5.0, "y": 5.0}
        self._logger.info(
            "GazeboEnv initialised (world='%s', headless=%s).",
            world_name,
            headless,
        )

    # ------------------------------------------------------------------
    # Gym-style interface
    # ------------------------------------------------------------------

    def reset(self) -> Dict[str, Any]:
        """Reset the environment to its initial state.

        Returns:
            Initial observation dictionary.
        """
        self._step_count = 0
        self._is_running = True
        self._robot_state = {
            "position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "orientation": {"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            "velocity": {"linear": 0.0, "angular": 0.0},
        }
        self._logger.debug("Environment reset.")
        return self._get_observation()

    def step(
        self, action: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """Execute one simulation step.

        Args:
            action: Action dictionary with optional ``linear_velocity``
                and ``angular_velocity`` keys.

        Returns:
            Tuple of (observation, reward, done, info).
        """
        if not self._is_running:
            self._logger.warning("step() called before reset().")
            return self._get_observation(), 0.0, True, {}

        self._step_count += 1
        self._apply_action(action)
        obs = self._get_observation()
        reward = self._compute_reward(self._robot_state, action)
        done = self._is_terminal()
        info = {"step": self._step_count, "world": self._world_name}
        return obs, reward, done, info

    def render(self) -> Optional[np.ndarray]:
        """Render the environment.

        Returns:
            Mock RGB image array if headless, else None.
        """
        if self._headless:
            return np.zeros((480, 640, 3), dtype=np.uint8)
        # In a real implementation this would trigger a Gazebo camera capture
        return None

    def close(self) -> None:
        """Shut down the environment."""
        self._is_running = False
        self._logger.info("GazeboEnv closed.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_observation(self) -> Dict[str, Any]:
        """Build an observation dictionary from the current robot state.

        Returns:
            Observation dict with camera image, LiDAR, and state info.
        """
        # Mock camera image
        camera = np.zeros((480, 640, 3), dtype=np.uint8)
        # Mock LiDAR: 360 rays, all beyond range
        lidar = np.full(360, 5.0, dtype=np.float32)
        lidar[0] = random.uniform(0.5, 3.0)  # Introduce one obstacle

        return {
            "camera": camera,
            "lidar": lidar,
            "state": dict(self._robot_state),
            "goal": dict(self._goal),
        }

    def _compute_reward(
        self, state: Dict[str, Any], action: Dict[str, Any]
    ) -> float:
        """Compute the reward signal for the current transition.

        Args:
            state: Current robot state.
            action: Action taken.

        Returns:
            Scalar reward value.
        """
        pos = state["position"]
        dx = self._goal["x"] - pos["x"]
        dy = self._goal["y"] - pos["y"]
        distance = (dx**2 + dy**2) ** 0.5
        reward = -0.01 * distance  # Dense distance reward

        if distance < 0.5:
            reward += 10.0  # Goal bonus

        return float(reward)

    def _apply_action(self, action: Dict[str, Any]) -> None:
        """Apply an action to update the mock robot state.

        Args:
            action: Action dictionary.
        """
        v = float(action.get("linear_velocity", 0.0))
        w = float(action.get("angular_velocity", 0.0))
        yaw = self._robot_state["orientation"]["yaw"]

        import math

        dt = 0.1  # 10 Hz simulation step
        self._robot_state["position"]["x"] += v * math.cos(yaw) * dt
        self._robot_state["position"]["y"] += v * math.sin(yaw) * dt
        self._robot_state["orientation"]["yaw"] += w * dt
        self._robot_state["velocity"] = {"linear": v, "angular": w}

    def _is_terminal(self) -> bool:
        """Determine whether the episode has ended.

        Returns:
            True if the goal is reached or the step limit is exceeded.
        """
        pos = self._robot_state["position"]
        dx = self._goal["x"] - pos["x"]
        dy = self._goal["y"] - pos["y"]
        if (dx**2 + dy**2) ** 0.5 < 0.5:
            return True
        return self._step_count >= self._max_steps
