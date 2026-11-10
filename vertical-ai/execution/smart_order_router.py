"""Smart order routing: optimal execution path selection.

Provides :class:`SmartOrderRouter` which selects and sequences execution
venues to minimise market impact and transaction costs.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class Venue:
    """Represents a trading venue or liquidity pool.

    Attributes:
        name: Venue identifier.
        available_liquidity: Available shares / contracts at this venue.
        fee_bps: Transaction fee in basis points.
        latency_ms: Estimated round-trip latency in milliseconds.
        fill_probability: Empirical probability of order fill at this venue.
    """

    name: str
    available_liquidity: float
    fee_bps: float
    latency_ms: float
    fill_probability: float = 0.95


@dataclass
class RoutingPlan:
    """Describes how an order should be split across venues.

    Attributes:
        venues: Ordered list of venues to use.
        allocations: Shares to send to each venue (same order as venues).
        estimated_cost_bps: Expected total transaction cost in basis points.
        estimated_fill_rate: Expected fraction of order filled.
    """

    venues: list[str]
    allocations: list[float]
    estimated_cost_bps: float
    estimated_fill_rate: float
    metadata: dict[str, Any] = field(default_factory=dict)


class SmartOrderRouter:
    """Route orders optimally across available trading venues.

    Uses a simple cost-minimisation heuristic that balances transaction fees,
    market impact, and fill probability to construct a routing plan.

    Attributes:
        venues: Registered trading venues.
        impact_coefficient: Coefficient for the linear market-impact penalty.
        max_venues: Maximum number of venues to include in a routing plan.
    """

    def __init__(
        self,
        venues: list[dict[str, Any]] | None = None,
        impact_coefficient: float = 0.1,
        max_venues: int = 3,
    ) -> None:
        """Initialise SmartOrderRouter.

        Args:
            venues: List of venue configuration dicts.  Each dict should
                contain keys matching :class:`Venue` field names.
            impact_coefficient: Linear market-impact cost coefficient.
            max_venues: Maximum venues to split an order across.
        """
        default_venues = [
            Venue("PRIMARY", 100_000, 0.5, 1.0, 0.98),
            Venue("DARK_POOL", 50_000, 0.2, 5.0, 0.80),
            Venue("ECN_1", 75_000, 0.3, 2.0, 0.92),
            Venue("ECN_2", 60_000, 0.35, 2.5, 0.90),
        ]
        if venues:
            self.venues: list[Venue] = [Venue(**v) for v in venues]
        else:
            self.venues = default_venues

        self.impact_coefficient = impact_coefficient
        self.max_venues = max_venues

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _venue_cost_score(
        self, venue: Venue, order_fraction: float
    ) -> float:
        """Compute a cost score for sending *order_fraction* to *venue*.

        Lower scores are better.

        Args:
            venue: Venue object.
            order_fraction: Fraction of total order (0–1).

        Returns:
            Cost score (bps equivalent).
        """
        fee = venue.fee_bps
        impact = self.impact_coefficient * order_fraction * 100
        fill_penalty = (1 - venue.fill_probability) * 50
        latency_penalty = venue.latency_ms * 0.01
        return fee + impact + fill_penalty + latency_penalty

    def _allocate(
        self, order_size: float, eligible_venues: list[Venue]
    ) -> list[float]:
        """Greedy allocation: fill venues in order of available liquidity.

        Args:
            order_size: Total order size.
            eligible_venues: Venues sorted by preference.

        Returns:
            List of allocation amounts matching venue order.
        """
        allocations: list[float] = []
        remaining = order_size
        for v in eligible_venues:
            alloc = min(remaining, v.available_liquidity)
            allocations.append(alloc)
            remaining -= alloc
            if remaining <= 0:
                break
        while len(allocations) < len(eligible_venues):
            allocations.append(0.0)
        return allocations

    # ------------------------------------------------------------------
    # Public async interface
    # ------------------------------------------------------------------

    async def route(
        self,
        order_size: float,
        side: str,
        urgency: str = "normal",
        market_conditions: dict[str, Any] | None = None,
    ) -> RoutingPlan:
        """Compute an optimal routing plan for an order.

        Args:
            order_size: Order size in shares / contracts.
            side: ``"buy"`` or ``"sell"``.
            urgency: ``"low"``, ``"normal"``, or ``"high"``.  Higher urgency
                favours low-latency venues even if they cost more.
            market_conditions: Optional dict with keys like ``volatility`` and
                ``spread_bps`` to adjust impact estimates.

        Returns:
            :class:`RoutingPlan` with venue allocations and cost estimates.

        Raises:
            ValueError: If side is not ``"buy"`` or ``"sell"``.
        """
        if side not in ("buy", "sell"):
            raise ValueError("side must be 'buy' or 'sell'.")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._compute_plan, order_size, side, urgency, market_conditions or {}
        )

    def _compute_plan(
        self,
        order_size: float,
        side: str,
        urgency: str,
        market_conditions: dict[str, Any],
    ) -> RoutingPlan:
        """Synchronous routing plan computation.

        Args:
            order_size: Order size.
            side: Order side.
            urgency: Urgency level.
            market_conditions: Market context dict.

        Returns:
            Routing plan.
        """
        logger.debug(f"Routing {side} order size={order_size}, urgency={urgency}")

        vol = market_conditions.get("volatility", 0.01)
        spread_bps = market_conditions.get("spread_bps", 5.0)

        # Sort venues by cost score; use latency tie-break for high urgency
        scored: list[tuple[float, Venue]] = []
        for v in self.venues:
            if v.available_liquidity <= 0:
                continue
            frac = min(order_size, v.available_liquidity) / (order_size + 1e-9)
            score = self._venue_cost_score(v, frac)
            if urgency == "high":
                score += v.latency_ms * 0.1
            scored.append((score, v))

        scored.sort(key=lambda x: x[0])
        eligible = [v for _, v in scored[: self.max_venues]]

        allocations = self._allocate(order_size, eligible)
        total_allocated = sum(allocations)

        # Estimated costs
        total_cost_bps = sum(
            self._venue_cost_score(v, alloc / (order_size + 1e-9))
            for v, alloc in zip(eligible, allocations)
            if alloc > 0
        )
        fill_probs = [
            v.fill_probability for v, alloc in zip(eligible, allocations) if alloc > 0
        ]
        est_fill_rate = float(np.mean(fill_probs)) if fill_probs else 0.0

        plan = RoutingPlan(
            venues=[v.name for v in eligible],
            allocations=allocations,
            estimated_cost_bps=round(total_cost_bps, 4),
            estimated_fill_rate=round(est_fill_rate, 4),
            metadata={
                "total_allocated": total_allocated,
                "unfilled": max(0.0, order_size - total_allocated),
                "volatility": vol,
                "spread_bps": spread_bps,
            },
        )
        logger.debug(f"Routing plan: {plan.venues}, cost={plan.estimated_cost_bps:.2f}bps")
        return plan
