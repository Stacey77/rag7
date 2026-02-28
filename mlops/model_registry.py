"""Model versioning and registry."""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModelVersion:
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0.0"
    model_name: str = ""
    description: str = ""
    metrics: Dict[str, float] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    stage: str = "development"   # development | staging | production | archived
    artifact_path: Optional[str] = None
    checksum: Optional[str] = None
    created_by: str = "system"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RegisteredModel:
    model_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    versions: List[ModelVersion] = field(default_factory=list)
    latest_version: Optional[str] = None
    production_version: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ModelSearchResult:
    models: List[RegisteredModel] = field(default_factory=list)
    total: int = 0
    query: Dict[str, Any] = field(default_factory=dict)


def _compute_checksum(data: Dict[str, Any]) -> str:
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:16]


def _bump_version(current: str, part: str = "patch") -> str:
    parts = [int(x) for x in current.split(".")]
    while len(parts) < 3:
        parts.append(0)
    if part == "major":
        return f"{parts[0]+1}.0.0"
    if part == "minor":
        return f"{parts[0]}.{parts[1]+1}.0"
    return f"{parts[0]}.{parts[1]}.{parts[2]+1}"


class ModelRegistry:
    """
    Central model registry for versioning, staging, and lifecycle management.
    """

    def __init__(self) -> None:
        self._models: Dict[str, RegisteredModel] = {}      # name -> model
        self._version_index: Dict[str, ModelVersion] = {}  # version_id -> version
        logger.info("ModelRegistry initialized")

    def register_model(self, name: str, description: str = "") -> RegisteredModel:
        if name in self._models:
            logger.debug("Model '%s' already registered", name)
            return self._models[name]
        model = RegisteredModel(name=name, description=description)
        self._models[name] = model
        logger.info("Registered model: %s", name)
        return model

    def log_model(self, model_name: str, metrics: Dict[str, float],
                  parameters: Optional[Dict[str, Any]] = None,
                  tags: Optional[Dict[str, str]] = None,
                  description: str = "",
                  created_by: str = "system") -> ModelVersion:
        if model_name not in self._models:
            self.register_model(model_name)

        registered = self._models[model_name]
        existing_versions = registered.versions

        # Auto-increment version
        if existing_versions:
            latest_v = existing_versions[-1].version
            new_v = _bump_version(latest_v)
        else:
            new_v = "1.0.0"

        params = parameters or {}
        version = ModelVersion(
            version=new_v,
            model_name=model_name,
            description=description,
            metrics=metrics,
            parameters=params,
            tags=tags or {},
            created_by=created_by,
            checksum=_compute_checksum({"metrics": metrics, "parameters": params}),
        )
        registered.versions.append(version)
        registered.latest_version = new_v
        self._version_index[version.version_id] = version

        logger.info("Logged model %s v%s (checksum=%s)", model_name, new_v, version.checksum)
        return version

    def transition_stage(self, model_name: str, version: str, new_stage: str) -> bool:
        registered = self._models.get(model_name)
        if not registered:
            return False
        mv = next((v for v in registered.versions if v.version == version), None)
        if not mv:
            return False
        old_stage = mv.stage
        mv.stage = new_stage
        mv.updated_at = datetime.utcnow()
        if new_stage == "production":
            registered.production_version = version
        logger.info("Model %s v%s: %s -> %s", model_name, version, old_stage, new_stage)
        return True

    def get_model(self, model_name: str) -> Optional[RegisteredModel]:
        return self._models.get(model_name)

    def get_version(self, model_name: str, version: str) -> Optional[ModelVersion]:
        registered = self._models.get(model_name)
        if not registered:
            return None
        return next((v for v in registered.versions if v.version == version), None)

    def get_production_version(self, model_name: str) -> Optional[ModelVersion]:
        registered = self._models.get(model_name)
        if not registered or not registered.production_version:
            return None
        return self.get_version(model_name, registered.production_version)

    def list_models(self) -> List[str]:
        return list(self._models.keys())

    def search(self, tags: Optional[Dict[str, str]] = None,
               min_metric: Optional[Dict[str, float]] = None,
               stage: Optional[str] = None) -> ModelSearchResult:
        results: List[RegisteredModel] = []
        for model in self._models.values():
            for mv in model.versions:
                if stage and mv.stage != stage:
                    continue
                if tags and not all(mv.tags.get(k) == v for k, v in tags.items()):
                    continue
                if min_metric and not all(mv.metrics.get(k, 0) >= v for k, v in min_metric.items()):
                    continue
                results.append(model)
                break
        return ModelSearchResult(models=results, total=len(results), query={
            "tags": tags, "min_metric": min_metric, "stage": stage})

    def compare_versions(self, model_name: str, v1: str, v2: str) -> Dict[str, Any]:
        mv1 = self.get_version(model_name, v1)
        mv2 = self.get_version(model_name, v2)
        if not mv1 or not mv2:
            return {"error": "version not found"}
        metric_diff = {
            k: mv2.metrics.get(k, 0) - mv1.metrics.get(k, 0)
            for k in set(mv1.metrics) | set(mv2.metrics)
        }
        return {"v1": v1, "v2": v2, "metric_diff": metric_diff,
                "param_changes": {k: v for k, v in mv2.parameters.items()
                                  if mv1.parameters.get(k) != v}}

    def delete_version(self, model_name: str, version: str) -> bool:
        registered = self._models.get(model_name)
        if not registered:
            return False
        before = len(registered.versions)
        registered.versions = [v for v in registered.versions if v.version != version]
        return len(registered.versions) < before

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "total_models": len(self._models),
            "total_versions": len(self._version_index),
            "models": {
                name: {
                    "versions": len(m.versions),
                    "production": m.production_version,
                    "latest": m.latest_version,
                }
                for name, m in self._models.items()
            },
        }
