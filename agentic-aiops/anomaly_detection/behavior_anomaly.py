"""Behavioral anomaly detection using baseline comparison."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class BehaviorProfile:
    """Baseline behavioral profile for a user or system component.

    Attributes:
        entity_id: Identifier for the user/component being profiled.
        feature_means: Per-feature mean values from baseline.
        feature_stds: Per-feature standard deviations from baseline.
        feature_names: Ordered list of feature names.
        n_samples: Number of samples used to build the baseline.
        built_at: UTC timestamp when the baseline was built.
    """

    entity_id: str
    feature_means: np.ndarray
    feature_stds: np.ndarray
    feature_names: list[str]
    n_samples: int
    built_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BehaviorAnomalyResult:
    """Result of a behavioral anomaly check.

    Attributes:
        entity_id: Checked entity identifier.
        is_anomaly: Whether anomalous behaviour was detected.
        anomaly_score: Overall anomaly score (0–1, higher = more anomalous).
        anomalous_features: Features that contributed to the detection.
        feature_scores: Per-feature anomaly scores.
        detected_at: UTC timestamp.
    """

    entity_id: str
    is_anomaly: bool
    anomaly_score: float
    anomalous_features: list[str]
    feature_scores: dict[str, float] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BehaviorAnomaly:
    """Behavioral anomaly detection using baseline comparison.

    Builds per-entity baseline profiles and flags new observations that
    deviate significantly using a Mahalanobis-inspired distance metric.

    Attributes:
        profiles: Baseline profiles keyed by entity_id.
        detection_history: All past anomaly results.
        _zscore_threshold: Feature Z-score threshold.
        _global_threshold: Global anomaly score threshold (0–1).
    """

    def __init__(
        self,
        zscore_threshold: float = 3.0,
        global_threshold: float = 0.7,
    ) -> None:
        """Initialise the behavioral anomaly detector.

        Args:
            zscore_threshold: Per-feature Z-score above which a feature is
                flagged.
            global_threshold: Overall anomaly score threshold for declaring
                anomalous behaviour.
        """
        self.profiles: dict[str, BehaviorProfile] = {}
        self.detection_history: list[BehaviorAnomalyResult] = []
        self._zscore_threshold = zscore_threshold
        self._global_threshold = global_threshold
        logger.info(
            "BehaviorAnomaly initialised (zscore={}, global={})",
            zscore_threshold,
            global_threshold,
        )

    def build_profile(
        self,
        entity_id: str,
        observations: np.ndarray,
        feature_names: list[str] | None = None,
    ) -> BehaviorProfile:
        """Build a baseline behavioral profile for an entity.

        Args:
            entity_id: Entity identifier.
            observations: 2-D array of shape (n_samples, n_features).
            feature_names: Optional feature labels.

        Returns:
            The built :class:`BehaviorProfile`.

        Raises:
            ValueError: If ``observations`` has fewer than 10 samples.
            ValueError: If ``observations`` is not 2-D.
        """
        observations = np.atleast_2d(np.asarray(observations, dtype=float))
        if observations.ndim != 2:
            raise ValueError("observations must be 2-D (n_samples × n_features)")
        n_samples, n_features = observations.shape
        if n_samples < 10:
            raise ValueError(f"Baseline requires ≥10 samples, got {n_samples}")

        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(n_features)]
        if len(feature_names) != n_features:
            raise ValueError(
                f"feature_names length {len(feature_names)} != n_features {n_features}"
            )

        means = np.mean(observations, axis=0)
        stds = np.std(observations, axis=0, ddof=1) + 1e-10

        profile = BehaviorProfile(
            entity_id=entity_id,
            feature_means=means,
            feature_stds=stds,
            feature_names=feature_names,
            n_samples=n_samples,
        )
        self.profiles[entity_id] = profile
        logger.info(
            "Behavior profile built for '{}': {} features, {} samples",
            entity_id,
            n_features,
            n_samples,
        )
        return profile

    def detect(
        self,
        entity_id: str,
        observation: np.ndarray,
    ) -> BehaviorAnomalyResult:
        """Compare a new observation against the entity's baseline profile.

        Args:
            entity_id: Entity to check.
            observation: 1-D feature vector (must match profile dimensions).

        Returns:
            :class:`BehaviorAnomalyResult` with anomaly classification.

        Raises:
            KeyError: If no profile exists for ``entity_id``.
            ValueError: If ``observation`` has the wrong number of features.
        """
        profile = self._get_profile(entity_id)
        observation = np.asarray(observation, dtype=float).ravel()

        if len(observation) != len(profile.feature_means):
            raise ValueError(
                f"observation has {len(observation)} features, "
                f"profile expects {len(profile.feature_means)}"
            )

        z_scores = np.abs((observation - profile.feature_means) / profile.feature_stds)
        anomalous_features: list[str] = []
        feature_scores: dict[str, float] = {}

        for i, (name, z) in enumerate(zip(profile.feature_names, z_scores)):
            score = float(min(1.0, z / (self._zscore_threshold * 2 + 1e-10)))
            feature_scores[name] = round(score, 4)
            if z > self._zscore_threshold:
                anomalous_features.append(name)

        # Global score = fraction of features exceeding threshold, weighted by score
        global_score = float(np.mean(list(feature_scores.values())))
        is_anomaly = (
            global_score >= self._global_threshold
            or len(anomalous_features) / max(len(profile.feature_names), 1) > 0.5
        )

        result = BehaviorAnomalyResult(
            entity_id=entity_id,
            is_anomaly=is_anomaly,
            anomaly_score=round(global_score, 4),
            anomalous_features=anomalous_features,
            feature_scores=feature_scores,
        )
        self.detection_history.append(result)

        if is_anomaly:
            logger.warning(
                "Behavioral anomaly for '{}': score={:.4f}, features={}",
                entity_id,
                global_score,
                anomalous_features,
            )
        else:
            logger.debug("Behavior check OK for '{}' (score={:.4f})", entity_id, global_score)

        return result

    def batch_detect(
        self,
        entity_id: str,
        observations: np.ndarray,
    ) -> list[BehaviorAnomalyResult]:
        """Detect anomalies across multiple observations.

        Args:
            entity_id: Entity to check.
            observations: 2-D array of shape (n_obs, n_features).

        Returns:
            List of :class:`BehaviorAnomalyResult` for each observation.
        """
        observations = np.atleast_2d(np.asarray(observations, dtype=float))
        return [self.detect(entity_id, obs) for obs in observations]

    def _get_profile(self, entity_id: str) -> BehaviorProfile:
        """Retrieve a profile, raising KeyError if not found.

        Args:
            entity_id: Entity identifier.

        Returns:
            The :class:`BehaviorProfile`.

        Raises:
            KeyError: If no profile has been built.
        """
        if entity_id not in self.profiles:
            raise KeyError(
                f"No baseline profile for entity '{entity_id}'. "
                "Call build_profile() first."
            )
        return self.profiles[entity_id]
