"""Variational Quantum Eigensolver (VQE) simulation.

Provides a classical simulation of VQE for finding optimal portfolio weights
by minimising a parameterised quantum circuit's energy.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import minimize
from loguru import logger


class VQE:
    """Classical simulation of VQE for portfolio weight optimisation.

    VQE uses a parameterised quantum circuit (ansatz) to prepare trial states
    and minimises the expectation value of the cost Hamiltonian.  This
    classical simulation encodes portfolio mean-variance as the Hamiltonian.

    Attributes:
        n_layers: Depth of the parameterised ansatz circuit.
        optimiser: Scipy optimiser method.
        max_iter: Maximum optimiser iterations.
        convergence_tol: Gradient norm tolerance for convergence.
    """

    def __init__(
        self,
        n_layers: int = 3,
        optimiser: str = "L-BFGS-B",
        max_iter: int = 500,
        convergence_tol: float = 1e-6,
    ) -> None:
        """Initialise VQE.

        Args:
            n_layers: Number of variational layers.
            optimiser: Scipy minimiser method.
            max_iter: Maximum function evaluations.
            convergence_tol: Convergence tolerance.
        """
        self.n_layers = n_layers
        self.optimiser = optimiser
        self.max_iter = max_iter
        self.convergence_tol = convergence_tol

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ansatz(self, params: np.ndarray, n: int) -> np.ndarray:
        """Evaluate the parameterised ansatz to produce portfolio weights.

        The ansatz applies alternating Ry and CNOT-like mixing layers.
        Weights are derived as |<0|U(theta)|0>|^2 normalised.

        Args:
            params: Flat parameter array of length ``n_layers * n``.
            n: Number of assets (qubits).

        Returns:
            Portfolio weight vector summing to 1.
        """
        # Reshape to (n_layers, n)
        thetas = params.reshape(self.n_layers, n)
        # Simulate Ry rotations: amplitude = sin(theta/2)
        amplitudes = np.ones(n)
        for layer_thetas in thetas:
            amplitudes = amplitudes * np.cos(layer_thetas / 2) + np.sin(layer_thetas / 2)
        probs = np.abs(amplitudes) ** 2
        return probs / (probs.sum() + 1e-12)

    def _energy(
        self,
        params: np.ndarray,
        n: int,
        returns: np.ndarray,
        cov: np.ndarray,
        risk_aversion: float,
    ) -> float:
        """Compute Hamiltonian expectation value (mean-variance objective).

        Args:
            params: Ansatz parameters.
            n: Number of assets.
            returns: Expected returns.
            cov: Covariance matrix.
            risk_aversion: Risk-aversion coefficient.

        Returns:
            Objective value (to minimise).
        """
        w = self._ansatz(params, n)
        port_return = float(w @ returns)
        port_var = float(w @ cov @ w)
        return -(port_return - risk_aversion * port_var)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def find_optimal_weights(
        self,
        returns: Any,
        cov_matrix: Any,
        risk_aversion: float = 1.0,
    ) -> dict[str, Any]:
        """Find optimal portfolio weights using VQE simulation.

        Args:
            returns: Array of shape ``(n_assets,)`` with expected returns.
            cov_matrix: Covariance matrix of shape ``(n_assets, n_assets)``.
            risk_aversion: Risk-aversion coefficient.

        Returns:
            Dict with keys ``weights``, ``objective``, ``n_assets``,
            ``n_layers``, ``converged``.
        """
        r = np.asarray(returns, dtype=np.float64)
        cov = np.asarray(cov_matrix, dtype=np.float64)
        n = len(r)

        logger.debug(f"VQE optimising {n}-asset portfolio, layers={self.n_layers}")

        n_params = self.n_layers * n
        x0 = np.random.default_rng().uniform(0, 2 * np.pi, size=n_params)
        bounds = [(0, 2 * np.pi)] * n_params

        result = minimize(
            self._energy,
            x0,
            args=(n, r, cov, risk_aversion),
            method=self.optimiser,
            bounds=bounds,
            options={"maxiter": self.max_iter, "ftol": self.convergence_tol},
        )

        weights = self._ansatz(result.x, n)
        obj_val = float(-(weights @ r) + risk_aversion * float(weights @ cov @ weights))

        logger.debug(f"VQE complete: objective={obj_val:.6f}, converged={result.success}")
        return {
            "weights": weights.tolist(),
            "objective": obj_val,
            "n_assets": n,
            "n_layers": self.n_layers,
            "converged": result.success,
        }

    def ground_state_energy(
        self,
        hamiltonian_matrix: Any,
    ) -> dict[str, Any]:
        """Find the ground state energy of an arbitrary Hamiltonian matrix.

        Uses the Rayleigh-Ritz variational principle.

        Args:
            hamiltonian_matrix: Hermitian matrix of shape ``(d, d)``.

        Returns:
            Dict with ``ground_state_energy``, ``ground_state_vector``.
        """
        H = np.asarray(hamiltonian_matrix, dtype=np.complex128)
        eigenvalues, eigenvectors = np.linalg.eigh(H)
        idx = int(np.argmin(eigenvalues))
        return {
            "ground_state_energy": float(np.real(eigenvalues[idx])),
            "ground_state_vector": eigenvectors[:, idx].tolist(),
        }
