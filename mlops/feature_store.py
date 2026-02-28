"""Centralized feature store for ML feature engineering and storage."""
from __future__ import annotations

import hashlib
import json
import logging
import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FeatureDefinition:
    feature_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    entity_type: str = ""          # e.g. "user", "model", "service"
    dtype: str = "float"           # "float" | "int" | "str" | "bool"
    description: str = ""
    transformation: Optional[str] = None  # description of transformation applied
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FeatureValue:
    feature_name: str
    entity_id: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    ttl_seconds: Optional[int] = None


@dataclass
class FeatureVector:
    entity_id: str
    features: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureStats:
    feature_name: str
    count: int = 0
    mean: float = 0.0
    std: float = 0.0
    min_val: float = 0.0
    max_val: float = 0.0
    null_rate: float = 0.0
    computed_at: datetime = field(default_factory=datetime.utcnow)


class FeatureTransformer:
    """Common feature transformations."""

    @staticmethod
    def normalize(values: List[float]) -> List[float]:
        min_v, max_v = min(values), max(values)
        span = max_v - min_v
        if span == 0:
            return [0.0] * len(values)
        return [(v - min_v) / span for v in values]

    @staticmethod
    def standardize(values: List[float]) -> List[float]:
        if len(values) < 2:
            return [0.0] * len(values)
        mean = statistics.mean(values)
        std = statistics.stdev(values)
        if std == 0:
            return [0.0] * len(values)
        return [(v - mean) / std for v in values]

    @staticmethod
    def log_transform(values: List[float], base: float = 10.0) -> List[float]:
        import math
        return [math.log(max(v, 1e-9), base) for v in values]

    @staticmethod
    def one_hot(value: str, categories: List[str]) -> Dict[str, int]:
        return {f"is_{cat}": int(value == cat) for cat in categories}

    @staticmethod
    def bucket(value: float, boundaries: List[float]) -> int:
        for i, boundary in enumerate(boundaries):
            if value < boundary:
                return i
        return len(boundaries)


class OfflineStore:
    """Batch feature storage for training."""

    def __init__(self) -> None:
        self._store: Dict[str, List[FeatureValue]] = {}  # feature_name -> values

    def write(self, feature_value: FeatureValue) -> None:
        self._store.setdefault(feature_value.feature_name, []).append(feature_value)

    def read(self, feature_name: str, entity_id: Optional[str] = None,
             start_time: Optional[datetime] = None) -> List[FeatureValue]:
        values = self._store.get(feature_name, [])
        if entity_id:
            values = [v for v in values if v.entity_id == entity_id]
        if start_time:
            values = [v for v in values if v.timestamp >= start_time]
        return values

    def get_latest(self, feature_name: str, entity_id: str) -> Optional[FeatureValue]:
        values = self.read(feature_name, entity_id=entity_id)
        return max(values, key=lambda v: v.timestamp) if values else None

    def compute_stats(self, feature_name: str) -> Optional[FeatureStats]:
        values = [v.value for v in self._store.get(feature_name, [])
                  if isinstance(v.value, (int, float))]
        if not values:
            return None
        return FeatureStats(
            feature_name=feature_name,
            count=len(values),
            mean=statistics.mean(values),
            std=statistics.stdev(values) if len(values) > 1 else 0.0,
            min_val=min(values),
            max_val=max(values),
            null_rate=0.0,
        )


class OnlineStore:
    """Low-latency feature serving for inference."""

    def __init__(self) -> None:
        self._cache: Dict[Tuple[str, str], FeatureValue] = {}

    def write(self, fv: FeatureValue) -> None:
        self._cache[(fv.feature_name, fv.entity_id)] = fv

    def read(self, feature_name: str, entity_id: str) -> Optional[Any]:
        fv = self._cache.get((feature_name, entity_id))
        if fv is None:
            return None
        if fv.ttl_seconds is not None:
            age = (datetime.utcnow() - fv.timestamp).total_seconds()
            if age > fv.ttl_seconds:
                del self._cache[(feature_name, entity_id)]
                return None
        return fv.value

    def evict_expired(self) -> int:
        now = datetime.utcnow()
        expired = [k for k, v in self._cache.items()
                   if v.ttl_seconds and (now - v.timestamp).total_seconds() > v.ttl_seconds]
        for k in expired:
            del self._cache[k]
        return len(expired)


class FeatureStore:
    """
    Centralized feature store with offline (batch) and online (serving)
    storage, feature registration, transformation pipelines, and point-in-time joins.
    """

    def __init__(self) -> None:
        self._definitions: Dict[str, FeatureDefinition] = {}
        self._offline = OfflineStore()
        self._online = OnlineStore()
        self._transformers: Dict[str, Callable] = {}
        self.transformer = FeatureTransformer()
        logger.info("FeatureStore initialized")

    def register_feature(self, name: str, entity_type: str, dtype: str = "float",
                          description: str = "", tags: Optional[List[str]] = None) -> FeatureDefinition:
        fd = FeatureDefinition(name=name, entity_type=entity_type, dtype=dtype,
                               description=description, tags=tags or [])
        self._definitions[name] = fd
        logger.debug("Registered feature '%s' (%s)", name, entity_type)
        return fd

    def register_transformer(self, feature_name: str, func: Callable) -> None:
        self._transformers[feature_name] = func

    def ingest(self, feature_name: str, entity_id: str, value: Any,
               ttl_seconds: Optional[int] = None) -> None:
        """Write a feature value to both online and offline stores."""
        transformer = self._transformers.get(feature_name)
        if transformer and isinstance(value, (int, float)):
            value = transformer(value)
        fv = FeatureValue(feature_name=feature_name, entity_id=entity_id,
                          value=value, ttl_seconds=ttl_seconds)
        self._offline.write(fv)
        self._online.write(fv)

    def get_online_features(self, entity_id: str, feature_names: List[str]) -> FeatureVector:
        features = {}
        for name in feature_names:
            val = self._online.read(name, entity_id)
            if val is not None:
                features[name] = val
        return FeatureVector(entity_id=entity_id, features=features)

    def get_training_dataset(self, entity_ids: List[str],
                              feature_names: List[str],
                              start_time: Optional[datetime] = None) -> List[FeatureVector]:
        dataset: List[FeatureVector] = []
        for entity_id in entity_ids:
            features: Dict[str, Any] = {}
            for name in feature_names:
                fv = self._offline.get_latest(name, entity_id)
                if fv:
                    features[name] = fv.value
            dataset.append(FeatureVector(entity_id=entity_id, features=features))
        return dataset

    def compute_stats(self, feature_name: str) -> Optional[FeatureStats]:
        return self._offline.compute_stats(feature_name)

    def list_features(self, entity_type: Optional[str] = None) -> List[FeatureDefinition]:
        if entity_type:
            return [fd for fd in self._definitions.values() if fd.entity_type == entity_type]
        return list(self._definitions.values())

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "registered_features": len(self._definitions),
            "online_cache_size": len(self._online._cache),
            "offline_features": list(self._offline._store.keys()),
        }
