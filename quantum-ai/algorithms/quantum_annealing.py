"""Quantum annealing simulation: simulated annealing for combinatorial problems.

Provides :class:`QuantumAnnealing` which uses a quantum-inspired simulated
annealing schedule with transverse-field tunnelling for combinatorial
portfolio and allocation optimisation.
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np
from loguru import logger


class QuantumAnnealing:
    """Quantum-inspired simulated annealing for combinatorial optimisation.

    Enhances classical simulated annealing with a quantum tunnelling term
    (transverse field) that decays with the annealing schedule, allowing
    the solver to escape local minima more effectively at early stages.

    Attributes:
        n_sweeps: Total number of annealing sweeps.
        t_initial: Initial temperature.
        t_final: Final temperature.
        gamma_initial: Initial transverse-field strength (tunnelling).
        gamma_final: Final transverse-field strength.
        schedule: Temperature decay schedule (``"linear"`` or
            ``"exponential"``).
    """

    def __init__(
        self,
        n_sweeps: int = 1000,
        t_initial: float = 10.0,
        t_final: float = 0.01,
        gamma_initial: float = 2.0,
        gamma_final: float = 0.001,
        schedule: str = "exponential",
    ) -> None:
        """Initialise QuantumAnnealing.

        Args:
            n_sweeps: Number of Monte Carlo sweeps.
            t_initial: Starting temperature.
            t_final: Ending temperature.
            gamma_initial: Starting transverse-field strength.
            gamma_final: Ending transverse-field strength.
            schedule: Cooling schedule (``"linear"`` or ``"exponential"``).

        Raises:
            ValueError: If schedule is not recognised.
        """
        if schedule not in ("linear", "exponential"):
            raise ValueError("schedule must be 'linear' or 'exponential'.")
        self.n_sweeps = n_sweeps
        self.t_initial = t_initial
        self.t_final = t_final
        self.gamma_initial = gamma_initial
        self.gamma_final = gamma_final
        self.schedule = schedule

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _temperature(self, step: int) -> float:
        """Compute temperature at a given annealing step.

        Args:
            step: Current sweep index.

        Returns:
            Temperature value.
        """
        frac = step / max(self.n_sweeps - 1, 1)
        if self.schedule == "linear":
            return self.t_initial + frac * (self.t_final - self.t_initial)
        # exponential
        return self.t_initial * (self.t_final / self.t_initial) ** frac

    def _transverse_field(self, step: int) -> float:
        """Compute transverse-field strength at a given step.

        Args:
            step: Current sweep index.

        Returns:
            Gamma value.
        """
        frac = step / max(self.n_sweeps - 1, 1)
        if self.schedule == "linear":
            return self.gamma_initial + frac * (self.gamma_final - self.gamma_initial)
        return self.gamma_initial * (self.gamma_final / self.gamma_initial) ** frac

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def minimize(
        self,
        cost_fn: Callable[[np.ndarray], float],
        n_variables: int,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Minimise a binary combinatorial cost function.

        Args:
            cost_fn: Function mapping a binary array ``(n_variables,)`` to a
                scalar cost.
            n_variables: Number of binary decision variables.
            seed: Random seed.

        Returns:
            Dict with keys ``best_solution`` (binary array as list),
            ``best_cost``, ``cost_history``, ``n_sweeps``.
        """
        rng = np.random.default_rng(seed)
        state = rng.integers(0, 2, size=n_variables).astype(float)
        best_state = state.copy()
        best_cost = cost_fn(state)
        current_cost = best_cost
        cost_history: list[float] = [best_cost]

        logger.debug(
            f"Quantum annealing: {n_variables} variables, {self.n_sweeps} sweeps"
        )

        for sweep in range(self.n_sweeps):
            T = self._temperature(sweep)
            gamma = self._transverse_field(sweep)

            # Single spin-flip proposal
            flip_idx = int(rng.integers(0, n_variables))
            new_state = state.copy()
            new_state[flip_idx] = 1.0 - new_state[flip_idx]
            new_cost = cost_fn(new_state)

            delta = new_cost - current_cost
            # Quantum tunnelling term: effective acceptance boost for small barriers
            tunnel_boost = gamma * np.exp(-abs(delta) / (T + 1e-9))
            acceptance_prob = np.exp(-delta / (T + 1e-9)) + tunnel_boost

            if delta < 0 or rng.random() < min(acceptance_prob, 1.0):
                state = new_state
                current_cost = new_cost
                if current_cost < best_cost:
                    best_cost = current_cost
                    best_state = state.copy()

            if sweep % (self.n_sweeps // 10) == 0:
                cost_history.append(current_cost)

        logger.debug(f"Annealing complete: best_cost={best_cost:.6f}")
        return {
            "best_solution": best_state.astype(int).tolist(),
            "best_cost": best_cost,
            "cost_history": cost_history,
            "n_sweeps": self.n_sweeps,
        }

    def solve_qubo(
        self,
        Q: Any,
        seed: int | None = None,
    ) -> dict[str, Any]:
        """Solve a Quadratic Unconstrained Binary Optimisation (QUBO) problem.

        Args:
            Q: QUBO matrix of shape ``(n, n)``.  Cost = x^T Q x.
            seed: Random seed.

        Returns:
            Dict with ``best_solution``, ``best_cost``, ``cost_history``.
        """
        Q_arr = np.asarray(Q, dtype=np.float64)
        n = Q_arr.shape[0]

        def qubo_cost(x: np.ndarray) -> float:
            return float(x @ Q_arr @ x)

        return self.minimize(qubo_cost, n, seed=seed)
