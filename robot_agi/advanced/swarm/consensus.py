"""Consensus algorithm for distributed multi-robot agreement."""
import logging
import random

logger = logging.getLogger(__name__)


class ConsensusAlgorithm:
    """Iterative average consensus for distributed robot coordination."""

    def __init__(self, convergence_threshold: float = 0.01) -> None:
        """Initialize ConsensusAlgorithm."""
        self.convergence_threshold = convergence_threshold

    def run(self, robot_states: list, max_iterations: int = 100) -> dict:
        """Run iterative consensus algorithm until convergence or max iterations.

        Args:
            robot_states: List of robot state dicts with 'value' fields.
            max_iterations: Maximum number of consensus iterations.

        Returns:
            Dict with final consensus value, convergence info, and iteration count.
        """
        logger.info("Running consensus for %d robots, max_iter=%d", len(robot_states), max_iterations)
        if not robot_states:
            return {"status": "empty", "consensus_value": 0.0, "iterations": 0, "converged": False}

        values = [float(s.get("value", random.uniform(0, 1))) for s in robot_states]
        iterations = 0
        converged = False

        for iteration in range(max_iterations):
            iterations = iteration + 1
            new_values = []
            for i, v in enumerate(values):
                neighbors = [values[j] for j in range(len(values)) if j != i]
                if neighbors:
                    new_val = 0.5 * v + 0.5 * (sum(neighbors) / len(neighbors))
                else:
                    new_val = v
                new_values.append(new_val)

            max_change = max(abs(new_values[i] - values[i]) for i in range(len(values)))
            values = new_values

            if max_change < self.convergence_threshold:
                converged = True
                break

        consensus_value = sum(values) / len(values)
        return {
            "status": "converged" if converged else "max_iterations_reached",
            "consensus_value": consensus_value,
            "iterations": iterations,
            "converged": converged,
            "final_values": values,
            "max_deviation": max(abs(v - consensus_value) for v in values),
        }
