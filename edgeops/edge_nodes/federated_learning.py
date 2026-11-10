"""Federated learning coordination for distributed edge model training."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class ClientUpdate:
    """A model update submitted by a federated learning client.

    Attributes:
        client_id: Identifier of the contributing edge device.
        gradients: Gradient arrays keyed by layer name.
        n_samples: Number of local training samples.
        local_loss: Training loss on the client's local dataset.
        round_number: Federated round this update belongs to.
        submitted_at: UTC submission timestamp.
    """

    client_id: str
    gradients: dict[str, np.ndarray]
    n_samples: int
    local_loss: float
    round_number: int
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AggregationResult:
    """Result of a gradient aggregation step.

    Attributes:
        round_number: Federated learning round.
        aggregated_gradients: Sample-weighted averaged gradients.
        participating_clients: IDs of clients included.
        total_samples: Total training samples across all clients.
        weighted_loss: Sample-weighted mean local loss.
        aggregated_at: UTC timestamp.
    """

    round_number: int
    aggregated_gradients: dict[str, np.ndarray]
    participating_clients: list[str]
    total_samples: int
    weighted_loss: float
    aggregated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FederatedRoundResult:
    """Summary of a completed federated learning round.

    Attributes:
        round_number: Completed round index.
        n_clients: Number of participating clients.
        global_loss: Aggregated loss after this round.
        model_version: New global model version string.
        duration_s: Wall-clock round duration in seconds.
    """

    round_number: int
    n_clients: int
    global_loss: float
    model_version: str
    duration_s: float


class FederatedLearning:
    """Distributed federated learning coordinator for edge devices.

    Implements FedAvg (Federated Averaging) with optional differential
    privacy noise injection.  Coordinates rounds, aggregates gradients,
    and distributes updated global model parameters.

    Attributes:
        current_round: Current federated round number.
        round_history: Completed round summaries.
        _pending_updates: Collected client updates awaiting aggregation.
        _global_model_version: Current global model version counter.
        _min_clients: Minimum clients required per round.
    """

    def __init__(self, min_clients: int = 3) -> None:
        """Initialise the federated learning coordinator.

        Args:
            min_clients: Minimum number of client updates required to
                proceed with aggregation.
        """
        self.current_round: int = 0
        self.round_history: list[FederatedRoundResult] = []
        self._pending_updates: list[ClientUpdate] = []
        self._global_model_version: int = 0
        self._min_clients = min_clients
        logger.info("FederatedLearning coordinator initialised (min_clients={})", min_clients)

    def submit_update(self, update: ClientUpdate) -> None:
        """Accept a client gradient update.

        Args:
            update: Client update from a federated participant.

        Raises:
            ValueError: If ``update.round_number`` does not match the
                current round.
        """
        if update.round_number != self.current_round:
            raise ValueError(
                f"Update is for round {update.round_number}, "
                f"but current round is {self.current_round}"
            )
        self._pending_updates.append(update)
        logger.debug(
            "Received update from client '{}' (round={}, samples={})",
            update.client_id,
            update.round_number,
            update.n_samples,
        )

    def aggregate_gradients(
        self,
        updates: list[ClientUpdate] | None = None,
        *,
        dp_noise_scale: float = 0.0,
    ) -> AggregationResult:
        """Aggregate client updates using FedAvg (sample-weighted mean).

        Args:
            updates: Updates to aggregate; defaults to pending buffer.
            dp_noise_scale: Standard deviation of Gaussian noise added for
                differential privacy (0 = no DP noise).

        Returns:
            :class:`AggregationResult` with averaged gradients.

        Raises:
            RuntimeError: If fewer than ``min_clients`` updates are available.
        """
        updates = updates or self._pending_updates
        if len(updates) < self._min_clients:
            raise RuntimeError(
                f"Insufficient updates: {len(updates)}, need {self._min_clients}"
            )

        total_samples = sum(u.n_samples for u in updates)
        layer_names = list(updates[0].gradients.keys())
        aggregated: dict[str, np.ndarray] = {}

        for layer in layer_names:
            weighted_sum = sum(
                u.gradients[layer] * u.n_samples
                for u in updates
                if layer in u.gradients
            )
            avg = weighted_sum / (total_samples + 1e-10)

            if dp_noise_scale > 0:
                rng = np.random.default_rng()
                avg = avg + rng.normal(0, dp_noise_scale, size=avg.shape)

            aggregated[layer] = avg

        weighted_loss = sum(u.local_loss * u.n_samples for u in updates) / (total_samples + 1e-10)
        result = AggregationResult(
            round_number=self.current_round,
            aggregated_gradients=aggregated,
            participating_clients=[u.client_id for u in updates],
            total_samples=total_samples,
            weighted_loss=round(float(weighted_loss), 4),
        )
        logger.info(
            "Aggregated {} clients, {} samples, weighted_loss={:.4f}",
            len(updates),
            total_samples,
            weighted_loss,
        )
        return result

    def federated_average(
        self,
        model_weights: list[dict[str, np.ndarray]],
        sample_counts: list[int],
    ) -> dict[str, np.ndarray]:
        """Compute the sample-weighted average of model weight dictionaries.

        Args:
            model_weights: List of model weight dicts from each client.
            sample_counts: Corresponding sample counts.

        Returns:
            Averaged model weight dictionary.

        Raises:
            ValueError: If ``model_weights`` and ``sample_counts`` lengths differ.
        """
        if len(model_weights) != len(sample_counts):
            raise ValueError(
                f"Lengths differ: {len(model_weights)} models, {len(sample_counts)} counts"
            )

        total = sum(sample_counts) + 1e-10
        layer_names = list(model_weights[0].keys())
        averaged: dict[str, np.ndarray] = {}

        for layer in layer_names:
            averaged[layer] = sum(
                w[layer] * n for w, n in zip(model_weights, sample_counts)
            ) / total

        logger.debug("FedAvg computed for {} layers", len(layer_names))
        return averaged

    async def coordinate_round(
        self,
        client_ids: list[str],
        simulate_updates: bool = True,
    ) -> FederatedRoundResult:
        """Coordinate a complete federated learning round.

        Collects updates from clients, runs FedAvg, and increments the round
        counter.

        Args:
            client_ids: List of participating client identifiers.
            simulate_updates: Generate synthetic updates when ``True``.

        Returns:
            :class:`FederatedRoundResult` summarising the round.

        Raises:
            RuntimeError: If fewer clients than ``min_clients`` are specified.
        """
        if len(client_ids) < self._min_clients:
            raise RuntimeError(
                f"Need ≥{self._min_clients} clients, got {len(client_ids)}"
            )

        import time
        start = time.monotonic()
        logger.info("Starting federated round {} with {} clients", self.current_round, len(client_ids))

        if simulate_updates:
            self._pending_updates.clear()
            for client_id in client_ids:
                update = self._simulate_client_update(client_id)
                self._pending_updates.append(update)

        await asyncio.sleep(0)
        aggregation = self.aggregate_gradients()

        self._global_model_version += 1
        duration = time.monotonic() - start

        result = FederatedRoundResult(
            round_number=self.current_round,
            n_clients=len(client_ids),
            global_loss=aggregation.weighted_loss,
            model_version=f"global_v{self._global_model_version}",
            duration_s=round(duration, 4),
        )
        self.round_history.append(result)
        self.current_round += 1
        self._pending_updates.clear()

        logger.info(
            "Federated round {} complete: loss={:.4f}, version={}",
            result.round_number,
            result.global_loss,
            result.model_version,
        )
        return result

    def _simulate_client_update(self, client_id: str) -> ClientUpdate:
        """Generate a synthetic client update for testing.

        Args:
            client_id: Client identifier.

        Returns:
            Simulated :class:`ClientUpdate`.
        """
        rng = np.random.default_rng(seed=hash(client_id + str(self.current_round)) % (2**32))
        return ClientUpdate(
            client_id=client_id,
            gradients={
                "layer_1": rng.normal(0, 0.01, size=(64, 32)),
                "layer_2": rng.normal(0, 0.01, size=(32, 16)),
                "output": rng.normal(0, 0.01, size=(16, 1)),
            },
            n_samples=int(rng.integers(100, 1000)),
            local_loss=float(rng.uniform(0.1, 1.0)),
            round_number=self.current_round,
        )
