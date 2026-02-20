"""
Motion planner module for the rag7 planning system.

Provides trajectory planning and kinematic computations for
multi-DOF robot arms.
"""

import logging
import math
from typing import Any, Dict, List, Optional

import numpy as np


class MotionPlanner:
    """Trajectory planner for robot arm motion.

    Computes smooth joint trajectories and simplified kinematic
    solutions for a robot arm with configurable DOF.

    Args:
        dof: Degrees of freedom of the robot arm (default 6).
    """

    def __init__(self, dof: int = 6) -> None:
        """Initialize the motion planner."""
        self._logger = logging.getLogger("rag7.planning.motion")
        self._dof = dof
        self._link_lengths = [0.3] * dof  # Default uniform link lengths

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan_trajectory(
        self,
        start_config: List[float],
        goal_config: List[float],
        duration: float = 1.0,
        num_points: int = 50,
    ) -> Dict[str, Any]:
        """Plan a smooth joint-space trajectory.

        Uses cubic polynomial interpolation between start and goal
        configurations.

        Args:
            start_config: Starting joint angles in radians.
            goal_config: Goal joint angles in radians.
            duration: Total trajectory duration in seconds.
            num_points: Number of trajectory waypoints.

        Returns:
            Dictionary with:
                - ``trajectory``: List of joint configuration lists.
                - ``timestamps``: List of time values in seconds.
        """
        start = np.asarray(start_config, dtype=float)
        goal = np.asarray(goal_config, dtype=float)
        times = np.linspace(0.0, duration, num_points)

        # Cubic polynomial: q(t) = start + (goal-start) * (3τ² - 2τ³)
        # where τ = t / duration
        tau = times / duration
        blend = 3 * tau**2 - 2 * tau**3  # shape (num_points,)
        trajectory = [
            (start + (goal - start) * b).tolist() for b in blend
        ]

        return {"trajectory": trajectory, "timestamps": times.tolist()}

    def compute_ik(self, pose: Dict[str, float]) -> List[float]:
        """Compute simplified inverse kinematics for a target pose.

        This is a first-order approximation suitable for testing; a
        production system would use a full analytical or numerical IK
        solver.

        Args:
            pose: Target end-effector pose with ``x``, ``y``, ``z``
                keys (theta keys optional).

        Returns:
            List of joint angles in radians.
        """
        x = pose.get("x", 0.0)
        y = pose.get("y", 0.0)
        z = pose.get("z", 0.0)

        # Simplified: distribute the reach across joints uniformly
        total_reach = math.sqrt(x**2 + y**2 + z**2)
        reach_per_link = total_reach / max(self._dof, 1)
        target_angle = math.atan2(y, x)

        angles = []
        for i in range(self._dof):
            # Crude alternating-sign approximation
            angles.append(target_angle * ((-1) ** i) * (reach_per_link / 0.3))

        self._logger.debug("IK angles (simplified): %s", angles)
        return angles

    def compute_fk(self, joint_angles: List[float]) -> Dict[str, float]:
        """Compute forward kinematics for a given joint configuration.

        Uses a simplified planar chain model (sum of link projections).

        Args:
            joint_angles: List of joint angles in radians.

        Returns:
            End-effector pose dict with ``x``, ``y``, ``z`` keys.
        """
        x, y, z = 0.0, 0.0, 0.0
        cumulative_angle = 0.0

        for i, angle in enumerate(joint_angles):
            length = self._link_lengths[i] if i < len(self._link_lengths) else 0.3
            cumulative_angle += angle
            x += length * math.cos(cumulative_angle)
            y += length * math.sin(cumulative_angle)

        self._logger.debug("FK result: (%.3f, %.3f, %.3f)", x, y, z)
        return {"x": x, "y": y, "z": z}
