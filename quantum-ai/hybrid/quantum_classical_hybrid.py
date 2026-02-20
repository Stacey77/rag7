"""Quantum-classical hybrid computation engine.

Provides :class:`QuantumClassicalHybrid` which orchestrates a workflow that
combines quantum-inspired subroutines with classical ML-style post-processing.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import minimize
from loguru import logger

try:
    from quantum_ai.algorithms.qaoa import QAOA
    from quantum_ai.algorithms.vqe import VQE
    from quantum_ai.algorithms.quantum_annealing import QuantumAnnealing
except ImportError:
    from algorithms.qaoa import QAOA
    from algorithms.vqe import VQE
    from algorithms.quantum_annealing import QuantumAnnealing


class QuantumClassicalHybrid:
    """Hybrid computation combining quantum-inspired and classical algorithms.

    Implements a variational hybrid workflow:

    1. **Quantum phase** – QAOA / VQE produces an approximate solution.
    2. **Classical refinement** – classical gradient-based optimiser polishes
       the solution.
    3. **Ensemble** – multiple quantum runs are combined classically.

    Attributes:
        qaoa: QAOA sub-system.
        vqe: VQE sub-system.
        annealer: Quantum annealer sub-system.
        n_ensemble: Number of independent quantum runs to ensemble.
        classical_refinement_iter: Gradient-descent steps for refinement.
    """

    def __init__(
        self,
        n_ensemble: int = 5,
        classical_refinement_iter: int = 100,
        qaoa_params: dict[str, Any] | None = None,
        vqe_params: dict[str, Any] | None = None,
        annealing_params: dict[str, Any] | None = None,
    ) -> None:
        """Initialise QuantumClassicalHybrid.

        Args:
            n_ensemble: Number of quantum runs per optimisation call.
            classical_refinement_iter: Classical refinement iterations.
            qaoa_params: Keyword args for :class:`QAOA`.
            vqe_params: Keyword args for :class:`VQE`.
            annealing_params: Keyword args for :class:`QuantumAnnealing`.
        """
        self.n_ensemble = n_ensemble
        self.classical_refinement_iter = classical_refinement_iter
        self.qaoa = QAOA(**(qaoa_params or {}))
        self.vqe = VQE(**(vqe_params or {}))
        self.annealer = QuantumAnnealing(**(annealing_params or {}))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _classical_refine(
        self,
        initial_weights: np.ndarray,
        returns: np.ndarray,
        cov: np.ndarray,
        risk_aversion: float,
    ) -> np.ndarray:
        """Apply classical gradient-based refinement to portfolio weights.

        Args:
            initial_weights: Starting weight vector.
            returns: Expected returns.
            cov: Covariance matrix.
            risk_aversion: Risk-aversion coefficient.

        Returns:
            Refined weight vector (sums to 1, non-negative).
        """
        n = len(returns)

        def objective(w: np.ndarray) -> float:
            w_n = w / (w.sum() + 1e-12)
            return -(float(w_n @ returns) - risk_aversion * float(w_n @ cov @ w_n))

        constraints = {"type": "eq", "fun": lambda w: w.sum() - 1.0}
        bounds = [(0.0, 1.0)] * n

        result = minimize(
            objective, initial_weights, method="SLSQP",
            bounds=bounds, constraints=constraints,
            options={"maxiter": self.classical_refinement_iter, "ftol": 1e-8},
        )
        refined = result.x
        refined = np.clip(refined, 0, 1)
        refined /= refined.sum() + 1e-12
        return refined

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def hybrid_portfolio_optimize(
        self,
        returns: Any,
        cov_matrix: Any,
        risk_aversion: float = 1.0,
    ) -> dict[str, Any]:
        """Run hybrid quantum-classical portfolio optimisation.

        Runs multiple QAOA and VQE trials, ensembles the results, then
        applies classical refinement for precision.

        Args:
            returns: Expected returns array ``(n_assets,)``.
            cov_matrix: Covariance matrix ``(n_assets, n_assets)``.
            risk_aversion: Risk-aversion coefficient.

        Returns:
            Dict with keys ``weights``, ``objective``, ``method``,
            ``ensemble_results``.
        """
        r = np.asarray(returns, dtype=np.float64)
        cov = np.asarray(cov_matrix, dtype=np.float64)

        logger.info(
            f"Hybrid optimisation: {len(r)} assets, {self.n_ensemble} ensemble runs"
        )

        ensemble_weights: list[np.ndarray] = []
        ensemble_objectives: list[float] = []

        for i in range(self.n_ensemble):
            # Alternate between QAOA and VQE
            if i % 2 == 0:
                res = self.qaoa.optimize_portfolio(r, cov, risk_aversion)
            else:
                res = self.vqe.find_optimal_weights(r, cov, risk_aversion)
            w = np.asarray(res["weights"], dtype=np.float64)
            ensemble_weights.append(w)
            ensemble_objectives.append(res["objective"])

        # Ensemble: weighted average by inverse-objective
        objectives_arr = np.array(ensemble_objectives)
        # Lower objective = better; use softmax-like weighting on negated values
        scores = np.exp(-objectives_arr - objectives_arr.min())
        ensemble_w = np.array(ensemble_weights)
        mean_weights = (scores[:, None] * ensemble_w).sum(axis=0) / scores.sum()
        mean_weights /= mean_weights.sum() + 1e-12

        # Classical refinement
        refined = self._classical_refine(mean_weights, r, cov, risk_aversion)

        obj_val = float(-(refined @ r) + risk_aversion * float(refined @ cov @ refined))

        logger.info(f"Hybrid optimisation complete: objective={obj_val:.6f}")
        return {
            "weights": refined.tolist(),
            "objective": obj_val,
            "method": "QuantumClassicalHybrid",
            "ensemble_size": self.n_ensemble,
            "ensemble_objectives": ensemble_objectives,
        }

    def feature_map(
        self,
        data: Any,
        n_features: int | None = None,
    ) -> np.ndarray:
        """Apply a quantum-inspired feature map to classical data.

        Encodes classical features using angle encoding: maps each feature
        to a Pauli-Z expectation value via ``cos(pi * x)``.

        Args:
            data: 1-D or 2-D array-like of features.
            n_features: Target output dimension; defaults to input dimension.

        Returns:
            Feature-mapped array of the same shape.
        """
        arr = np.asarray(data, dtype=np.float64)
        mapped = np.cos(np.pi * arr)
        if n_features and n_features != arr.shape[-1]:
            # Random Fourier feature expansion
            rng = np.random.default_rng(42)
            W = rng.standard_normal((arr.shape[-1], n_features))
            mapped = np.cos(arr @ W / np.sqrt(n_features))
        return mapped
