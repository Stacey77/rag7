"""Adversarial data generation: edge-case and stress-test event simulation.

Provides :class:`AdversarialGenerator` for creating extreme market events such
as flash crashes, liquidity crises, and gap events for stress testing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class EdgeEvent:
    """Parameterises an extreme market event.

    Attributes:
        name: Event identifier.
        price_shock: Instantaneous log-price shock.
        vol_spike_factor: Volatility multiplier during the event.
        duration_steps: Number of steps the event lasts.
        recovery_halflife: Steps for mean-reversion after shock.
    """

    name: str
    price_shock: float
    vol_spike_factor: float
    duration_steps: int
    recovery_halflife: int


_BUILT_IN_EVENTS: dict[str, EdgeEvent] = {
    "flash_crash": EdgeEvent(
        "flash_crash",
        price_shock=-0.10,
        vol_spike_factor=8.0,
        duration_steps=5,
        recovery_halflife=3,
    ),
    "liquidity_crisis": EdgeEvent(
        "liquidity_crisis",
        price_shock=-0.25,
        vol_spike_factor=5.0,
        duration_steps=20,
        recovery_halflife=15,
    ),
    "gap_up": EdgeEvent(
        "gap_up",
        price_shock=0.08,
        vol_spike_factor=2.0,
        duration_steps=2,
        recovery_halflife=5,
    ),
    "gap_down": EdgeEvent(
        "gap_down",
        price_shock=-0.08,
        vol_spike_factor=2.5,
        duration_steps=2,
        recovery_halflife=5,
    ),
    "short_squeeze": EdgeEvent(
        "short_squeeze",
        price_shock=0.40,
        vol_spike_factor=6.0,
        duration_steps=3,
        recovery_halflife=10,
    ),
    "black_swan": EdgeEvent(
        "black_swan",
        price_shock=-0.50,
        vol_spike_factor=15.0,
        duration_steps=30,
        recovery_halflife=60,
    ),
}


class AdversarialGenerator:
    """Generate adversarial market scenarios for stress testing.

    Injects extreme events (flash crashes, liquidity crises, gap events) into
    a base GBM price path to create worst-case training/testing data.

    Attributes:
        seed: Random seed.
        base_mu: Base drift for background GBM.
        base_sigma: Base volatility for background GBM.
    """

    def __init__(
        self,
        seed: int | None = None,
        base_mu: float = 0.0,
        base_sigma: float = 0.20,
    ) -> None:
        """Initialise AdversarialGenerator.

        Args:
            seed: NumPy random seed.
            base_mu: Annual drift of the background process.
            base_sigma: Annual volatility of the background process.
        """
        self.base_mu = base_mu
        self.base_sigma = base_sigma
        self._rng = np.random.default_rng(seed)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _gbm_step(self, price: float, mu: float, sigma: float, dt: float) -> float:
        """Compute one GBM step.

        Args:
            price: Current price.
            mu: Annual drift.
            sigma: Annual volatility.
            dt: Step size in years.

        Returns:
            Next price.
        """
        z = self._rng.standard_normal()
        log_ret = (mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * z
        return float(price * np.exp(log_ret))

    def _apply_event(
        self,
        prices: np.ndarray,
        event: EdgeEvent,
        inject_at: int,
        dt: float,
    ) -> np.ndarray:
        """Inject an edge event into a price series.

        Args:
            prices: Existing price array (modified in-place clone).
            event: Edge event specification.
            inject_at: Step index at which the event begins.
            dt: Step size in years.

        Returns:
            Modified price array.
        """
        result = prices.copy()
        n = len(result)

        # Instant shock
        if inject_at < n:
            result[inject_at] *= np.exp(event.price_shock)

        # High-vol drift during event duration
        event_sigma = self.base_sigma * event.vol_spike_factor
        for i in range(inject_at + 1, min(inject_at + event.duration_steps + 1, n)):
            result[i] = self._gbm_step(result[i - 1], self.base_mu, event_sigma, dt)

        # Mean-reversion recovery
        recovery_end = min(inject_at + event.duration_steps + event.recovery_halflife, n)
        for i in range(inject_at + event.duration_steps + 1, recovery_end):
            decay = np.exp(-1.0 / event.recovery_halflife)
            recovery_sigma = self.base_sigma * (
                1.0 + (event.vol_spike_factor - 1.0) * decay
            )
            result[i] = self._gbm_step(result[i - 1], self.base_mu, recovery_sigma, dt)

        return result

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def generate(
        self,
        event_name: str,
        s0: float = 100.0,
        n_steps: int = 252,
        dt: float = 1 / 252,
        inject_at: int | None = None,
    ) -> dict[str, Any]:
        """Generate a price path with an injected edge event.

        Args:
            event_name: Name of the event (must be in built-in set or
                registered via :meth:`register_event`).
            s0: Initial price.
            n_steps: Total number of steps.
            dt: Step size in years.
            inject_at: Step at which the event is injected; defaults to 25% of
                the way through the path.

        Returns:
            Dict with keys ``event``, ``prices``, ``returns``,
            ``inject_at``, ``max_drawdown``.

        Raises:
            KeyError: If *event_name* is not registered.
        """
        if event_name not in _BUILT_IN_EVENTS:
            raise KeyError(
                f"Unknown event '{event_name}'. Available: {list(_BUILT_IN_EVENTS)}"
            )

        event = _BUILT_IN_EVENTS[event_name]
        step = inject_at if inject_at is not None else n_steps // 4

        # Base GBM path
        prices = np.empty(n_steps + 1)
        prices[0] = s0
        for i in range(1, n_steps + 1):
            prices[i] = self._gbm_step(prices[i - 1], self.base_mu, self.base_sigma, dt)

        prices = self._apply_event(prices, event, step, dt)

        # Max drawdown from peak
        cum = prices
        running_max = np.maximum.accumulate(cum)
        drawdowns = (cum - running_max) / running_max
        max_dd = float(np.min(drawdowns))

        returns = list(np.diff(prices) / prices[:-1])
        logger.debug(
            f"Adversarial '{event_name}': inject_at={step}, max_dd={max_dd:.2%}"
        )
        return {
            "event": event_name,
            "prices": prices.tolist(),
            "returns": returns,
            "inject_at": step,
            "max_drawdown": max_dd,
            "price_shock": event.price_shock,
        }

    def register_event(self, name: str, event: EdgeEvent) -> None:
        """Register a custom edge event.

        Args:
            name: Event identifier.
            event: :class:`EdgeEvent` specification.
        """
        _BUILT_IN_EVENTS[name] = event
        logger.debug(f"Registered adversarial event: {name}")

    def list_events(self) -> list[str]:
        """Return names of all registered events.

        Returns:
            Sorted list of event name strings.
        """
        return sorted(_BUILT_IN_EVENTS.keys())
