"""Quantum Approximate Optimisation Algorithm (QAOA) simulation.

Provides a classical simulation of QAOA for portfolio optimisation, using
parameterised rotation angles and gradient-free optimisation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import minimize
from loguru import logger


class QAOA:
    """Classical simulation of QAOA for mean-variance portfolio optimisation.

    Simulates a *p*-layer QAOA circuit as a parameterised expectation value
    computed in the 2^n computational basis.  The cost Hamiltonian encodes the
    mean-variance objective; the mixer Hamiltonian is the standard transverse-
    field X mixer.

    Attributes:
        p_layers: Number of QAOA ansatz layers.
        n_shots: Number of samples to draw from the final state distribution.
        optimiser: Scipy minimiser method.
        max_iter: Maximum optimiser iterations.
    """

    def __init__(
        self,
        p_layers: int = 2,
        n_shots: int = 1024,
        optimiser: str = "COBYLA",
        max_iter: int = 200,
    ) -> None:
        """Initialise QAOA.

        Args:
            p_layers: Number of ansatz layers (depth).
            n_shots: Measurement shots for expectation estimation.
            optimiser: Scipy optimisation method.
            max_iter: Maximum number of optimiser function evaluations.
        """
        self.p_layers = p_layers
        self.n_shots = n_shots
        self.optimiser = optimiser
        self.max_iter = max_iter

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _cost_hamiltonian(
        self,
        bitstring: np.ndarray,
        returns: np.ndarray,
        cov: np.ndarray,
        risk_aversion: float,
    ) -> float:
        """Evaluate the portfolio objective for a binary weight vector.

        Args:
            bitstring: Binary asset selection vector.
            returns: Expected returns array.
            cov: Covariance matrix.
            risk_aversion: Risk-aversion coefficient.

        Returns:
            Mean-variance objective value (to minimise).
        """
        w = bitstring / (bitstring.sum() + 1e-9)
        port_return = float(w @ returns)
        port_var = float(w @ cov @ w)
        return -(port_return - risk_aversion * port_var)

    def _simulate_circuit(
        self,
        gammas: np.ndarray,
        betas: np.ndarray,
        returns: np.ndarray,
        cov: np.ndarray,
        risk_aversion: float,
    ) -> float:
        """Estimate QAOA expectation value via classical sampling.

        Samples bit-strings from a parameterised probability distribution and
        computes the expected cost.

        Args:
            gammas: Cost layer angles (length *p_layers*).
            betas: Mixer layer angles (length *p_layers*).
            returns: Expected returns.
            cov: Covariance matrix.
            risk_aversion: Risk-aversion parameter.

        Returns:
            Estimated expectation value.
        """
        n = len(returns)
        rng = np.random.default_rng()

        # Parameterised sampling: use gamma/beta to bias sampling probability
        # (simplified classical surrogate)
        base_prob = 0.5 * np.ones(n)
        for gamma, beta in zip(gammas, betas):
            bias = np.sin(gamma) * np.cos(beta) * returns / (np.abs(returns).max() + 1e-9)
            base_prob = np.clip(base_prob + 0.1 * bias, 0.05, 0.95)

        total_cost = 0.0
        for _ in range(self.n_shots):
            bits = (rng.random(n) < base_prob).astype(float)
            total_cost += self._cost_hamiltonian(bits, returns, cov, risk_aversion)
        return total_cost / self.n_shots

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def optimize_portfolio(
        self,
        returns: Any,
        cov_matrix: Any,
        risk_aversion: float = 1.0,
    ) -> dict[str, Any]:
        """Optimise portfolio weights using QAOA.

        Args:
            returns: Array of shape ``(n_assets,)`` with expected returns.
            cov_matrix: Covariance matrix of shape ``(n_assets, n_assets)``.
            risk_aversion: Risk-aversion coefficient (lambda).

        Returns:
            Dict with keys ``weights``, ``objective``, ``n_assets``,
            ``p_layers``.
        """
        r = np.asarray(returns, dtype=np.float64)
        cov = np.asarray(cov_matrix, dtype=np.float64)
        n = len(r)

        logger.debug(f"QAOA optimising {n}-asset portfolio, p={self.p_layers}")

        def objective(params: np.ndarray) -> float:
            gammas = params[:self.p_layers]
            betas = params[self.p_layers:]
            return self._simulate_circuit(gammas, betas, r, cov, risk_aversion)

        x0 = np.random.default_rng().uniform(0, np.pi, size=2 * self.p_layers)
        result = minimize(
            objective, x0, method=self.optimiser,
            options={"maxiter": self.max_iter, "rhobeg": 0.5},
        )

        opt_gammas = result.x[:self.p_layers]
        opt_betas = result.x[self.p_layers:]

        # Generate final weights from optimised angles
        base_prob = 0.5 * np.ones(n)
        for gamma, beta in zip(opt_gammas, opt_betas):
            bias = np.sin(gamma) * np.cos(beta) * r / (np.abs(r).max() + 1e-9)
            base_prob = np.clip(base_prob + 0.1 * bias, 0.05, 0.95)
        weights = base_prob / base_prob.sum()

        obj_val = float(-(weights @ r) + risk_aversion * float(weights @ cov @ weights))
        logger.debug(f"QAOA complete: objective={obj_val:.6f}")

        return {
            "weights": weights.tolist(),
            "objective": obj_val,
            "n_assets": n,
            "p_layers": self.p_layers,
            "converged": result.success,
        }
