"""Synthetic AI – market simulation and synthetic data generation module.

Exposes the :class:`SyntheticAI` orchestrator which wires together price
simulation, scenario generation, backtesting, Monte Carlo analysis, and
data-validation sub-systems.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from loguru import logger

from synthetic_ai.generators.market_simulator import MarketSimulator
from synthetic_ai.generators.scenario_generator import ScenarioGenerator
from synthetic_ai.generators.adversarial_generator import AdversarialGenerator
from synthetic_ai.generators.synthetic_data_forge import SyntheticDataForge
from synthetic_ai.simulation.backtesting_engine import BacktestingEngine
from synthetic_ai.simulation.monte_carlo import MonteCarlo
from synthetic_ai.simulation.agent_simulation import AgentSimulation
from synthetic_ai.validation.reality_checker import RealityChecker
from synthetic_ai.validation.distribution_matcher import DistributionMatcher


class SyntheticAI:
    """Top-level orchestrator for synthetic data and market simulation.

    Attributes:
        simulator: Geometric Brownian Motion price simulator.
        scenario: Bull / bear / crash scenario generator.
        adversarial: Edge-case event generator.
        forge: Training data augmentation engine.
        backtester: Strategy back-testing engine.
        monte_carlo: Probabilistic scenario modeller.
        agents: Multi-agent market simulation.
        reality_checker: Synthetic-vs-real data validator.
        distribution_matcher: Statistical distribution validator.
    """

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        """Initialise SyntheticAI and all sub-systems.

        Args:
            config: Optional configuration overrides keyed by sub-system name.
        """
        cfg = config or {}
        logger.info("Initialising SyntheticAI")

        self.simulator = MarketSimulator(**cfg.get("simulator", {}))
        self.scenario = ScenarioGenerator(**cfg.get("scenario", {}))
        self.adversarial = AdversarialGenerator(**cfg.get("adversarial", {}))
        self.forge = SyntheticDataForge(**cfg.get("forge", {}))

        self.backtester = BacktestingEngine(**cfg.get("backtester", {}))
        self.monte_carlo = MonteCarlo(**cfg.get("monte_carlo", {}))
        self.agents = AgentSimulation(**cfg.get("agents", {}))

        self.reality_checker = RealityChecker(**cfg.get("reality_checker", {}))
        self.distribution_matcher = DistributionMatcher(
            **cfg.get("distribution_matcher", {})
        )

        logger.info("SyntheticAI initialised successfully")

    def generate_training_dataset(
        self,
        n_paths: int = 100,
        n_steps: int = 252,
        s0: float = 100.0,
        mu: float = 0.05,
        sigma: float = 0.20,
    ) -> dict[str, np.ndarray]:
        """Generate a synthetic training dataset of price paths.

        Args:
            n_paths: Number of independent price paths to simulate.
            n_steps: Number of time steps per path.
            s0: Initial asset price.
            mu: Annual drift (expected return).
            sigma: Annual volatility.

        Returns:
            Dict with key ``paths`` containing an array of shape
            ``(n_paths, n_steps + 1)``.
        """
        logger.info(f"Generating training dataset: {n_paths} paths × {n_steps} steps")
        paths = np.stack(
            [
                self.simulator.simulate(
                    s0=s0, mu=mu, sigma=sigma, n_steps=n_steps, dt=1 / 252
                )
                for _ in range(n_paths)
            ]
        )
        return {"paths": paths}


__all__ = ["SyntheticAI"]
