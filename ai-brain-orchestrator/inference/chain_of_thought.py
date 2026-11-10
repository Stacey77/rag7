"""Chain of Thought – structured multi-step reasoning chain executor.

Builds an ordered chain of reasoning steps, executes them sequentially,
and validates the logical consistency of the derived conclusions.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Coroutine

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")

# Step handler: receives accumulated chain state, returns a step result dict.
StepHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]


class StepStatus(Enum):
    """Execution status of a reasoning step."""

    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class ReasoningStep:
    """A single step within a chain of thought.

    Attributes:
        step_id: Unique identifier.
        name: Short human-readable label.
        handler: Async callable that performs the reasoning step.
        result: Output produced after execution.
        status: Current lifecycle status.
        error: Error message if the step failed.
    """

    name: str
    handler: StepHandler
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    result: dict[str, Any] = field(default_factory=dict)
    status: StepStatus = StepStatus.PENDING
    error: str = ""


@dataclass
class Chain:
    """A complete reasoning chain.

    Attributes:
        chain_id: Unique identifier.
        steps: Ordered list of :class:`ReasoningStep` objects.
        state: Accumulated state passed between steps.
        conclusion: Final synthesised conclusion.
        valid: Whether the chain passed validation.
    """

    chain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    steps: list[ReasoningStep] = field(default_factory=list)
    state: dict[str, Any] = field(default_factory=dict)
    conclusion: dict[str, Any] = field(default_factory=dict)
    valid: bool = False


class ChainOfThought:
    """Builds and executes multi-step reasoning chains.

    Attributes:
        _chains: Registry of created chains keyed by ``chain_id``.
    """

    def __init__(self) -> None:
        """Initialise with an empty chain registry."""
        self._chains: dict[str, Chain] = {}
        log.info("ChainOfThought initialised")

    def build_chain(
        self,
        steps: list[dict[str, Any]],
        initial_state: dict[str, Any] | None = None,
    ) -> Chain:
        """Construct a new reasoning chain from a list of step specifications.

        Each step dict must carry a ``name`` key and a ``handler`` callable.

        Args:
            steps: List of step specification dicts.
            initial_state: Seed state for the chain execution. Defaults to ``{}``.

        Returns:
            The newly created :class:`Chain`.

        Raises:
            ValueError: If *steps* is empty or a step dict is missing ``name``
                or ``handler``.
        """
        if not steps:
            raise ValueError("steps must not be empty")

        reasoning_steps: list[ReasoningStep] = []
        for spec in steps:
            if "name" not in spec:
                raise ValueError("Each step must have a 'name' key")
            if "handler" not in spec or not callable(spec["handler"]):
                raise ValueError(f"Step '{spec.get('name')}' must have a callable 'handler'")
            reasoning_steps.append(
                ReasoningStep(name=spec["name"], handler=spec["handler"])
            )

        chain = Chain(steps=reasoning_steps, state=dict(initial_state or {}))
        self._chains[chain.chain_id] = chain
        log.info("Chain built", chain_id=chain.chain_id, steps=len(reasoning_steps))
        return chain

    async def execute_chain(self, chain: Chain) -> Chain:
        """Run each step in *chain* sequentially, accumulating state.

        Args:
            chain: The :class:`Chain` to execute. Modified in-place.

        Returns:
            The executed :class:`Chain` with updated step statuses and conclusion.
        """
        log.info("Executing chain", chain_id=chain.chain_id, steps=len(chain.steps))
        for step in chain.steps:
            try:
                step.result = await step.handler(chain.state)
                chain.state.update(step.result)
                step.status = StepStatus.COMPLETED
                log.debug("Step completed", chain_id=chain.chain_id, step=step.name)
            except Exception as exc:  # noqa: BLE001
                step.status = StepStatus.FAILED
                step.error = str(exc)
                log.error(
                    "Step failed",
                    chain_id=chain.chain_id,
                    step=step.name,
                    error=str(exc),
                )
                # Continue remaining steps with whatever state we have.

        chain.conclusion = {k: v for k, v in chain.state.items()}
        chain.valid = await self.validate_reasoning(chain)
        log.info(
            "Chain executed",
            chain_id=chain.chain_id,
            valid=chain.valid,
            failed_steps=sum(1 for s in chain.steps if s.status == StepStatus.FAILED),
        )
        return chain

    async def validate_reasoning(self, chain: Chain) -> bool:
        """Check whether the chain's reasoning is logically consistent.

        Validation passes when all steps completed successfully and the
        conclusion is non-empty.

        Args:
            chain: The :class:`Chain` to validate.

        Returns:
            ``True`` if the chain is considered valid.
        """
        all_completed = all(s.status == StepStatus.COMPLETED for s in chain.steps)
        non_empty_conclusion = bool(chain.conclusion)
        valid = all_completed and non_empty_conclusion
        log.debug(
            "Reasoning validated",
            chain_id=chain.chain_id,
            valid=valid,
            all_completed=all_completed,
        )
        return valid
