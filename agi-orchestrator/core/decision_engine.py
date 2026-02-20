"""AGI Decision Engine – meta-learning multi-level decision maker.

Decisions are grouped into three levels:

* **Strategic** – long-horizon portfolio and regime decisions.
* **Tactical** – medium-horizon allocation and entry/exit timing.
* **Operational** – short-horizon execution and order management.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


class DecisionLevel(Enum):
    """Granularity tier for a decision."""

    STRATEGIC = auto()
    TACTICAL = auto()
    OPERATIONAL = auto()


@dataclass
class Signal:
    """A single named signal with an associated numeric value and metadata.

    Attributes:
        name: Human-readable signal identifier.
        value: Numeric magnitude of the signal.
        source: Originating sub-system or agent.
        metadata: Arbitrary extra key-value pairs.
    """

    name: str
    value: float
    source: str = "unknown"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """An output decision produced by the engine.

    Attributes:
        level: The decision tier this belongs to.
        action: Short action descriptor (e.g. ``"buy"``, ``"rebalance"``).
        confidence: Probability-like confidence in [0, 1].
        rationale: Human-readable explanation.
        metadata: Arbitrary supporting data.
    """

    level: DecisionLevel
    action: str
    confidence: float
    rationale: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class AGIDecisionEngine:
    """Meta-learning decision maker with three-level decision architecture.

    The engine processes raw signals, synthesises them into a unified view,
    and produces decisions at strategic, tactical, and operational levels.

    Attributes:
        state_manager: Shared :class:`GlobalStateManager` instance (optional).
        _signal_buffer: Accumulated signals awaiting processing.
        _strategy_weights: Per-level numeric weight used during synthesis.
    """

    def __init__(self, state_manager: Any | None = None) -> None:
        """Initialise the decision engine.

        Args:
            state_manager: Optional shared state store injected at runtime.
        """
        self.state_manager = state_manager
        self._signal_buffer: list[Signal] = []
        self._strategy_weights: dict[DecisionLevel, float] = {
            DecisionLevel.STRATEGIC: 0.5,
            DecisionLevel.TACTICAL: 0.3,
            DecisionLevel.OPERATIONAL: 0.2,
        }
        log.info("AGIDecisionEngine initialised")

    async def process_signals(self, signals: list[Signal]) -> None:
        """Buffer incoming signals for the next decision cycle.

        Args:
            signals: List of :class:`Signal` objects to accumulate.

        Raises:
            TypeError: If *signals* is not a list.
        """
        if not isinstance(signals, list):
            raise TypeError(f"signals must be a list, got {type(signals).__name__}")
        self._signal_buffer.extend(signals)
        log.debug("Buffered signals", count=len(signals), total=len(self._signal_buffer))

    async def synthesize(self) -> dict[str, Any]:
        """Aggregate the current signal buffer into a unified market view.

        Clears the buffer after synthesis.

        Returns:
            A mapping with keys ``signal_count``, ``net_value``, and
            ``sources`` summarising the buffered signals.
        """
        if not self._signal_buffer:
            log.debug("synthesize called with empty buffer")
            return {"signal_count": 0, "net_value": 0.0, "sources": []}

        net_value = sum(s.value for s in self._signal_buffer)
        sources = list({s.source for s in self._signal_buffer})
        result = {
            "signal_count": len(self._signal_buffer),
            "net_value": net_value,
            "sources": sources,
        }
        self._signal_buffer.clear()
        log.debug("Synthesised signals", **result)
        return result

    async def make_decision(
        self,
        context: dict[str, Any],
        level: DecisionLevel = DecisionLevel.TACTICAL,
    ) -> Decision:
        """Produce a decision for the requested level given the current context.

        The method synthesises any buffered signals, then applies level-specific
        heuristics to determine the best action and a confidence score.

        Args:
            context: Ambient information dict (e.g. market regime, portfolio
                state) made available by the caller.
            level: Decision tier to target. Defaults to
                :attr:`DecisionLevel.TACTICAL`.

        Returns:
            A :class:`Decision` describing the recommended action.

        Raises:
            ValueError: If *context* is not a dict.
        """
        if not isinstance(context, dict):
            raise ValueError(f"context must be a dict, got {type(context).__name__}")

        synthesis = await self.synthesize()
        weight = self._strategy_weights[level]

        net = synthesis.get("net_value", 0.0)
        confidence = min(abs(net) * weight, 1.0)
        action = "buy" if net > 0 else ("sell" if net < 0 else "hold")

        decision = Decision(
            level=level,
            action=action,
            confidence=confidence,
            rationale=f"net_signal={net:.4f} weight={weight}",
            metadata={"synthesis": synthesis, "context_keys": list(context.keys())},
        )
        log.info(
            "Decision made",
            level=level.name,
            action=action,
            confidence=f"{confidence:.3f}",
        )
        return decision
