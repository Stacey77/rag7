"""Quantum AI – quantum-inspired optimisation and simulation module.

Exposes the :class:`QuantumAI` orchestrator which wires together QAOA, VQE,
quantum annealing, Grover search, hybrid classical-quantum computation, and
quantum circuit simulation sub-systems.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger

from quantum_ai.algorithms.qaoa import QAOA
from quantum_ai.algorithms.vqe import VQE
from quantum_ai.algorithms.quantum_annealing import QuantumAnnealing
from quantum_ai.algorithms.grover_search import GroverSearch
from quantum_ai.hybrid.quantum_classical_hybrid import QuantumClassicalHybrid
from quantum_ai.hybrid.quantum_neural_network import QuantumNeuralNetwork
from quantum_ai.simulators.quantum_simulator import QuantumSimulator
from quantum_ai.simulators.noise_model import NoiseModel


class QuantumAI:
    """Top-level orchestrator for quantum-inspired trading optimisation.

    Attributes:
        qaoa: Quantum Approximate Optimisation Algorithm engine.
        vqe: Variational Quantum Eigensolver engine.
        annealer: Simulated quantum annealer.
        grover: Grover-search pattern matcher.
        hybrid: Quantum-classical hybrid computation engine.
        qnn: Quantum-inspired neural network.
        simulator: Classical quantum-circuit simulator.
        noise_model: Quantum noise model.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialise QuantumAI and all sub-systems.

        Args:
            config: Optional configuration overrides keyed by sub-system name.
        """
        cfg = config or {}
        logger.info("Initialising QuantumAI")

        self.qaoa = QAOA(**cfg.get("qaoa", {}))
        self.vqe = VQE(**cfg.get("vqe", {}))
        self.annealer = QuantumAnnealing(**cfg.get("annealing", {}))
        self.grover = GroverSearch(**cfg.get("grover", {}))

        self.hybrid = QuantumClassicalHybrid(**cfg.get("hybrid", {}))
        self.qnn = QuantumNeuralNetwork(**cfg.get("qnn", {}))

        self.simulator = QuantumSimulator(**cfg.get("simulator", {}))
        self.noise_model = NoiseModel(**cfg.get("noise_model", {}))

        logger.info("QuantumAI initialised successfully")

    def optimise_portfolio(
        self,
        returns: np.ndarray,
        cov_matrix: np.ndarray,
        risk_aversion: float = 1.0,
    ) -> dict[str, Any]:
        """Run quantum-inspired portfolio optimisation.

        Runs QAOA and VQE in parallel (classical simulation) and returns the
        best weights found by either algorithm.

        Args:
            returns: Array of shape ``(n_assets,)`` with expected returns.
            cov_matrix: Covariance matrix of shape ``(n_assets, n_assets)``.
            risk_aversion: Risk-aversion coefficient (lambda) for the
                mean-variance objective.

        Returns:
            Dict with keys ``weights`` (optimal asset weights), ``method``
            (winning algorithm name), and ``objective`` (objective value).
        """
        logger.info("Running quantum-inspired portfolio optimisation")
        qaoa_result = self.qaoa.optimize_portfolio(
            returns, cov_matrix, risk_aversion=risk_aversion
        )
        vqe_result = self.vqe.find_optimal_weights(
            returns, cov_matrix, risk_aversion=risk_aversion
        )

        if qaoa_result["objective"] <= vqe_result["objective"]:
            winner = {**qaoa_result, "method": "QAOA"}
        else:
            winner = {**vqe_result, "method": "VQE"}

        logger.info(f"Best method: {winner['method']}, objective={winner['objective']:.6f}")
        return winner


__all__ = ["QuantumAI"]
