"""Multi-agent market simulation: market makers and trend followers.

Provides :class:`AgentSimulation` for simulating price discovery through
heterogeneous agent interactions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class Agent:
    """Base class representing a market participant.

    Attributes:
        agent_id: Unique agent identifier.
        cash: Current cash balance.
        inventory: Current position (shares held).
        agent_type: ``"market_maker"``, ``"trend_follower"``, or
            ``"noise_trader"``.
    """

    agent_id: str
    cash: float
    inventory: float
    agent_type: str
    params: dict[str, Any] = field(default_factory=dict)


class AgentSimulation:
    """Simulate a multi-agent market with heterogeneous trading strategies.

    Agents interact through a simple limit-order book clearing mechanism.
    Three agent types are supported:

    * **Market maker** – quotes bid/ask around fundamental value; earns spread.
    * **Trend follower** – trades in the direction of recent price momentum.
    * **Noise trader** – submits random orders to add realistic microstructure
      noise.

    Attributes:
        n_market_makers: Number of market maker agents.
        n_trend_followers: Number of trend follower agents.
        n_noise_traders: Number of noise trader agents.
        tick_size: Minimum price increment.
        initial_price: Starting mid-price.
        seed: Random seed.
    """

    def __init__(
        self,
        n_market_makers: int = 3,
        n_trend_followers: int = 10,
        n_noise_traders: int = 20,
        tick_size: float = 0.01,
        initial_price: float = 100.0,
        seed: int | None = None,
    ) -> None:
        """Initialise AgentSimulation.

        Args:
            n_market_makers: Market maker count.
            n_trend_followers: Trend follower count.
            n_noise_traders: Noise trader count.
            tick_size: Minimum price step.
            initial_price: Initial equilibrium price.
            seed: NumPy random seed.
        """
        self.tick_size = tick_size
        self.initial_price = initial_price
        self._rng = np.random.default_rng(seed)
        self._agents: list[Agent] = []
        self._price_history: list[float] = [initial_price]
        self._volume_history: list[float] = [0.0]

        # Initialise agents
        for i in range(n_market_makers):
            self._agents.append(Agent(
                f"mm_{i}", cash=500_000.0, inventory=0.0, agent_type="market_maker",
                params={"spread_fraction": 0.002, "max_inventory": 1000.0},
            ))
        for i in range(n_trend_followers):
            self._agents.append(Agent(
                f"tf_{i}", cash=200_000.0, inventory=0.0, agent_type="trend_follower",
                params={"lookback": int(self._rng.integers(5, 30)),
                        "strength": float(self._rng.uniform(0.5, 2.0))},
            ))
        for i in range(n_noise_traders):
            self._agents.append(Agent(
                f"nt_{i}", cash=100_000.0, inventory=0.0, agent_type="noise_trader",
                params={"order_std": 10.0},
            ))

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _market_maker_order(
        self, agent: Agent, mid_price: float
    ) -> tuple[float, float]:
        """Generate market-maker bid/ask and net order.

        Market makers post symmetric quotes and earn the spread.

        Args:
            agent: Market maker agent.
            mid_price: Current mid-price.

        Returns:
            Tuple of (signed_order_size, price_impact).
        """
        spread = mid_price * agent.params["spread_fraction"]
        inventory_skew = -agent.inventory / (agent.params["max_inventory"] + 1e-9)
        target = inventory_skew * spread
        order_size = float(self._rng.normal(target, 5.0))
        price_impact = spread * 0.1 * np.sign(order_size)
        return order_size, float(price_impact)

    def _trend_follower_order(
        self, agent: Agent, price_history: list[float]
    ) -> tuple[float, float]:
        """Generate trend-follower order based on momentum signal.

        Args:
            agent: Trend follower agent.
            price_history: Full price history.

        Returns:
            Tuple of (signed_order_size, price_impact).
        """
        lookback = agent.params["lookback"]
        if len(price_history) < lookback + 1:
            return 0.0, 0.0

        recent = price_history[-lookback:]
        momentum = (recent[-1] - recent[0]) / (recent[0] + 1e-9)
        order_size = momentum * agent.params["strength"] * 100.0
        price_impact = abs(order_size) * 0.0001 * np.sign(order_size)
        return float(order_size), float(price_impact)

    def _noise_trader_order(self, agent: Agent) -> tuple[float, float]:
        """Generate random noise trader order.

        Args:
            agent: Noise trader agent.

        Returns:
            Tuple of (signed_order_size, price_impact).
        """
        order_size = float(self._rng.normal(0, agent.params["order_std"]))
        price_impact = abs(order_size) * 0.00005 * np.sign(order_size)
        return order_size, float(price_impact)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self, n_steps: int = 252) -> dict[str, Any]:
        """Run the multi-agent market simulation.

        Args:
            n_steps: Number of simulation steps (e.g., trading days).

        Returns:
            Dict with keys ``prices`` (list), ``volumes`` (list),
            ``agent_pnl`` (dict of agent_id → float),
            ``market_stats`` (dict of summary statistics).
        """
        logger.info(
            f"Starting agent simulation: {len(self._agents)} agents, {n_steps} steps"
        )
        prices = self._price_history.copy()
        volumes = self._volume_history.copy()

        for step in range(n_steps):
            mid = prices[-1]
            total_impact = 0.0
            total_volume = 0.0

            for agent in self._agents:
                if agent.agent_type == "market_maker":
                    order, impact = self._market_maker_order(agent, mid)
                elif agent.agent_type == "trend_follower":
                    order, impact = self._trend_follower_order(agent, prices)
                else:
                    order, impact = self._noise_trader_order(agent)

                fill_price = mid + impact
                fill_price = max(self.tick_size, fill_price)
                trade_value = abs(order) * fill_price

                if agent.cash >= trade_value or order < 0:
                    agent.inventory += order
                    agent.cash -= order * fill_price
                    total_impact += impact * abs(order) / (abs(order) + 1e-9)
                    total_volume += abs(order)

            # New price = mid + volume-weighted average impact + mean-reversion noise
            noise = float(self._rng.normal(0, mid * 0.001))
            new_price = max(self.tick_size, mid + total_impact * 0.01 + noise)
            prices.append(round(new_price, 4))
            volumes.append(round(total_volume, 2))

        # Compute agent PnL at final price
        final_price = prices[-1]
        agent_pnl = {
            a.agent_id: round(a.cash + a.inventory * final_price - (
                200_000.0 if a.agent_type == "trend_follower" else
                (100_000.0 if a.agent_type == "noise_trader" else 500_000.0)
            ), 2)
            for a in self._agents
        }

        price_arr = np.array(prices[1:])
        returns = np.diff(price_arr) / price_arr[:-1]
        market_stats = {
            "final_price": final_price,
            "total_return": float((prices[-1] / prices[0]) - 1.0),
            "volatility": float(np.std(returns, ddof=1)) * np.sqrt(252) if len(returns) > 1 else 0.0,
            "avg_daily_volume": float(np.mean(volumes[1:])),
            "n_agents": len(self._agents),
        }

        logger.info(
            f"Simulation complete: final_price={final_price:.2f}, "
            f"vol={market_stats['volatility']:.2%}"
        )
        return {
            "prices": prices,
            "volumes": volumes,
            "agent_pnl": agent_pnl,
            "market_stats": market_stats,
        }
