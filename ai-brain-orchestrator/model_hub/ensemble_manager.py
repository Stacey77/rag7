"""Ensemble Manager – multi-model coordination with weighted prediction aggregation.

Maintains a weighted pool of model references and combines their outputs
through configurable aggregation strategies (weighted average, majority vote).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")

# Inference callable: receives a feature dict, returns a prediction dict.
InferenceFn = Callable[[dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]


@dataclass
class EnsembleMember:
    """A single model participant in an ensemble.

    Attributes:
        model_id: Registry identifier for this model.
        weight: Relative contribution weight (will be normalised).
        infer: Async callable that runs the model.
        enabled: Whether this member participates in predictions.
    """

    model_id: str
    weight: float = 1.0
    infer: InferenceFn | None = field(default=None, repr=False)
    enabled: bool = True


class EnsembleManager:
    """Coordinates multiple models and aggregates their predictions.

    Attributes:
        registry: Optional :class:`ModelRegistry` for metadata look-ups.
        _members: Ordered list of :class:`EnsembleMember` objects.
    """

    def __init__(self, registry: Any | None = None) -> None:
        """Initialise with an optional model registry reference.

        Args:
            registry: Optional :class:`ModelRegistry` instance.
        """
        self.registry = registry
        self._members: list[EnsembleMember] = []
        log.info("EnsembleManager initialised")

    def add_model(
        self,
        model_id: str,
        weight: float = 1.0,
        infer: InferenceFn | None = None,
    ) -> None:
        """Add a model to the ensemble.

        Args:
            model_id: Registry identifier for the model.
            weight: Relative contribution weight. Defaults to ``1.0``.
            infer: Async inference callable. May be set later.

        Raises:
            ValueError: If a model with the same ``model_id`` already exists.
        """
        if any(m.model_id == model_id for m in self._members):
            raise ValueError(f"Model '{model_id}' is already in the ensemble")
        if weight <= 0:
            raise ValueError(f"weight must be positive, got {weight}")
        self._members.append(EnsembleMember(model_id=model_id, weight=weight, infer=infer))
        log.info("Ensemble member added", model_id=model_id, weight=weight)

    async def predict(self, features: dict[str, Any]) -> dict[str, Any]:
        """Run all enabled members concurrently and return the weighted ensemble output.

        Args:
            features: Feature dict forwarded to every member's ``infer`` callable.

        Returns:
            A dict with ``ensemble_prediction`` (weighted average of ``prediction``
            fields) and ``member_results`` (list of individual outputs).

        Raises:
            RuntimeError: If no enabled members with inference callables exist.
        """
        active = [m for m in self._members if m.enabled and m.infer is not None]
        if not active:
            raise RuntimeError("No active ensemble members with inference callables")

        async def _run(member: EnsembleMember) -> dict[str, Any]:
            try:
                result = await member.infer(features)  # type: ignore[misc]
                return {"model_id": member.model_id, "weight": member.weight, **result}
            except Exception as exc:  # noqa: BLE001
                log.error("Member inference failed", model_id=member.model_id, error=str(exc))
                return {"model_id": member.model_id, "weight": 0.0, "prediction": 0.0}

        raw_results = await asyncio.gather(*(_run(m) for m in active))
        ensemble_result = await self.weighted_ensemble(list(raw_results))
        log.info(
            "Ensemble prediction complete",
            member_count=len(raw_results),
            ensemble_prediction=ensemble_result.get("ensemble_prediction"),
        )
        return ensemble_result

    async def weighted_ensemble(
        self, member_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Aggregate member predictions using normalised weights.

        Args:
            member_results: List of per-member result dicts, each expected to
                carry ``prediction`` (float) and ``weight`` (float) keys.

        Returns:
            Dict with ``ensemble_prediction`` (float) and ``member_results``.
        """
        total_weight = sum(r.get("weight", 0.0) for r in member_results)
        if total_weight == 0:
            return {"ensemble_prediction": 0.0, "member_results": member_results}

        weighted_sum = sum(
            r.get("prediction", 0.0) * r.get("weight", 0.0) for r in member_results
        )
        ensemble_prediction = weighted_sum / total_weight
        return {
            "ensemble_prediction": ensemble_prediction,
            "member_results": member_results,
        }

    def remove_model(self, model_id: str) -> None:
        """Remove a model from the ensemble.

        Args:
            model_id: Identifier of the member to remove.

        Raises:
            KeyError: If *model_id* is not in the ensemble.
        """
        before = len(self._members)
        self._members = [m for m in self._members if m.model_id != model_id]
        if len(self._members) == before:
            raise KeyError(f"Model '{model_id}' not found in ensemble")
        log.info("Ensemble member removed", model_id=model_id)
