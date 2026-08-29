"""Scenario generation: bull, bear, crash, and rally market scenarios.

Provides :class:`ScenarioGenerator` for creating plausible what-if market
scenarios by modifying drift and volatility of a base price series.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from loguru import logger

try:
    from synthetic_ai.generators.market_simulator import MarketSimulator
except ImportError:
    from generators.market_simulator import MarketSimulator


@dataclass
class Scenario:
    """Describes a named market scenario.

    Attributes:
        name: Scenario label (e.g., ``"bear"``).
        drift_multiplier: Multiplier applied to the base drift.
        volatility_multiplier: Multiplier applied to the base volatility.
        shock: Optional one-time log-price shock applied at *shock_step*.
        shock_step: Index (0-based) at which the shock is applied.
        description: Human-readable description.
    """

    name: str
    drift_multiplier: float
    volatility_multiplier: float
    shock: float = 0.0
    shock_step: int | None = None
    description: str = ""


_BUILT_IN_SCENARIOS: dict[str, Scenario] = {
    "bull": Scenario(
        "bull", drift_multiplier=2.5, volatility_multiplier=0.8,
        description="Sustained upward trend with compressed volatility",
    ),
    "bear": Scenario(
        "bear", drift_multiplier=-1.5, volatility_multiplier=1.4,
        description="Sustained downward trend with elevated volatility",
    ),
    "crash": Scenario(
        "crash", drift_multiplier=-3.0, volatility_multiplier=3.0,
        shock=-0.20, shock_step=10,
        description="Sudden 20% gap-down followed by high-volatility recovery",
    ),
    "rally": Scenario(
        "rally", drift_multiplier=4.0, volatility_multiplier=1.2,
        shock=0.10, shock_step=5,
        description="10% gap-up followed by continued bullish momentum",
    ),
    "sideways": Scenario(
        "sideways", drift_multiplier=0.0, volatility_multiplier=0.6,
        description="Range-bound low-volatility consolidation",
    ),
    "high_vol": Scenario(
        "high_vol", drift_multiplier=0.5, volatility_multiplier=3.5,
        description="Elevated volatility with muted directional trend",
    ),
}


class ScenarioGenerator:
    """Generate what-if market scenarios from a base set of parameters.

    Attributes:
        simulator: Underlying :class:`MarketSimulator` instance.
        custom_scenarios: User-defined scenarios merged with built-ins.
    """

    def __init__(
        self,
        seed: int | None = None,
        custom_scenarios: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        """Initialise ScenarioGenerator.

        Args:
            seed: Random seed for reproducibility.
            custom_scenarios: Additional scenarios to register.  Each key is a
                scenario name and the value a dict of :class:`Scenario` fields.
        """
        self.simulator = MarketSimulator(seed=seed)
        self.custom_scenarios: dict[str, Scenario] = {**_BUILT_IN_SCENARIOS}
        if custom_scenarios:
            for name, cfg in custom_scenarios.items():
                self.custom_scenarios[name] = Scenario(name=name, **cfg)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(
        self,
        scenario_name: str,
        s0: float = 100.0,
        base_mu: float = 0.05,
        base_sigma: float = 0.20,
        n_steps: int = 252,
        dt: float = 1 / 252,
    ) -> dict[str, Any]:
        """Generate a single named scenario price path.

        Args:
            scenario_name: Name of the scenario (must be in
                :attr:`custom_scenarios`).
            s0: Initial price.
            base_mu: Base annual drift.
            base_sigma: Base annual volatility.
            n_steps: Number of time steps.
            dt: Step size in years.

        Returns:
            Dict with keys ``scenario``, ``prices`` (list), ``returns`` (list),
            ``final_price``, ``total_return``.

        Raises:
            KeyError: If *scenario_name* is not registered.
        """
        if scenario_name not in self.custom_scenarios:
            raise KeyError(
                f"Unknown scenario '{scenario_name}'. "
                f"Available: {list(self.custom_scenarios)}"
            )

        sc = self.custom_scenarios[scenario_name]
        adj_mu = base_mu * sc.drift_multiplier
        adj_sigma = base_sigma * sc.volatility_multiplier

        prices = self.simulator.simulate(
            s0=s0, mu=adj_mu, sigma=adj_sigma, n_steps=n_steps, dt=dt
        )

        # Apply one-time shock
        if sc.shock != 0.0 and sc.shock_step is not None:
            step = min(sc.shock_step, n_steps)
            prices[step:] *= np.exp(sc.shock)

        returns = list(np.diff(prices) / prices[:-1])
        total_return = float((prices[-1] / prices[0]) - 1.0)

        logger.debug(
            f"Scenario '{scenario_name}': total_return={total_return:.2%}, "
            f"final_price={prices[-1]:.2f}"
        )
        return {
            "scenario": scenario_name,
            "prices": prices.tolist(),
            "returns": returns,
            "final_price": float(prices[-1]),
            "total_return": total_return,
            "description": sc.description,
        }

    def generate_all(
        self,
        s0: float = 100.0,
        base_mu: float = 0.05,
        base_sigma: float = 0.20,
        n_steps: int = 252,
    ) -> dict[str, Any]:
        """Generate all registered scenarios.

        Args:
            s0: Initial price.
            base_mu: Base annual drift.
            base_sigma: Base annual volatility.
            n_steps: Number of steps.

        Returns:
            Dict mapping scenario names to their result dicts.
        """
        return {
            name: self.generate(name, s0, base_mu, base_sigma, n_steps)
            for name in self.custom_scenarios
        }

    def list_scenarios(self) -> list[dict[str, str]]:
        """List all available scenario names and descriptions.

        Returns:
            List of dicts with ``name`` and ``description`` keys.
        """
        return [
            {"name": sc.name, "description": sc.description}
            for sc in self.custom_scenarios.values()
        ]
