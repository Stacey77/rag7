"""Serve neural network model predictions with caching, batching, and health checks."""

import logging
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

CACHE_MAX_SIZE = 256


@dataclass
class InferenceRequest:
    """A single prediction request."""
    model_name: str
    inputs: Dict[str, Any]
    request_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InferenceResult:
    """The prediction output from a model."""
    request_id: str
    model_name: str
    prediction: Any
    confidence: float
    latency_ms: float
    cached: bool = False
    error: Optional[str] = None
    produced_at: datetime = field(default_factory=datetime.utcnow)


class NeuralNetInference:
    """Register callable model wrappers and serve inference with LRU caching."""

    def __init__(self, cache_size: int = CACHE_MAX_SIZE) -> None:
        # name -> callable(inputs: dict) -> (prediction, confidence float)
        self._models: Dict[str, Callable] = {}
        self._model_meta: Dict[str, Dict[str, Any]] = {}
        self._cache: OrderedDict = OrderedDict()
        self._cache_size = cache_size
        self._call_stats: Dict[str, Dict[str, Any]] = {}
        logger.info("NeuralNetInference initialised (cache_size=%d).", cache_size)

    def register_model(self, name: str, model: Callable,
                       version: str = "1.0", description: str = "") -> None:
        """Register a model callable under *name*."""
        self._models[name] = model
        self._model_meta[name] = {
            "name": name, "version": version, "description": description,
            "registered_at": datetime.utcnow().isoformat(),
        }
        self._call_stats[name] = {"calls": 0, "errors": 0, "total_latency_ms": 0.0}
        logger.info("Model registered: %s v%s", name, version)

    def _cache_key(self, request: InferenceRequest) -> str:
        return f"{request.model_name}:{hash(str(sorted(request.inputs.items())))}"

    def cache_result(self, key: str, result: InferenceResult) -> None:
        """Store a result in the LRU cache, evicting oldest if full."""
        if len(self._cache) >= self._cache_size:
            self._cache.popitem(last=False)
        self._cache[key] = result

    def infer(self, request: InferenceRequest) -> InferenceResult:
        """Run inference for a single request, using cache when possible."""
        key = self._cache_key(request)
        if key in self._cache:
            cached = self._cache[key]
            self._cache.move_to_end(key)
            logger.debug("Cache hit: model=%s", request.model_name)
            return InferenceResult(request_id=request.request_id,
                                   model_name=request.model_name,
                                   prediction=cached.prediction,
                                   confidence=cached.confidence,
                                   latency_ms=0.0, cached=True)

        model = self._models.get(request.model_name)
        stats = self._call_stats.get(request.model_name, {"calls": 0, "errors": 0, "total_latency_ms": 0.0})
        stats["calls"] += 1
        t0 = time.monotonic()

        if model is None:
            stats["errors"] += 1
            latency = round((time.monotonic() - t0) * 1000, 2)
            return InferenceResult(request_id=request.request_id,
                                   model_name=request.model_name,
                                   prediction=None, confidence=0.0,
                                   latency_ms=latency, error=f"Model '{request.model_name}' not registered.")

        try:
            raw = model(request.inputs)
            if isinstance(raw, tuple) and len(raw) == 2:
                prediction, confidence = raw
            else:
                prediction, confidence = raw, 0.9
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            latency = round((time.monotonic() - t0) * 1000, 2)
            logger.exception("Inference error for model=%s", request.model_name)
            return InferenceResult(request_id=request.request_id,
                                   model_name=request.model_name,
                                   prediction=None, confidence=0.0,
                                   latency_ms=latency, error=str(exc))

        latency = round((time.monotonic() - t0) * 1000, 2)
        stats["total_latency_ms"] += latency
        result = InferenceResult(request_id=request.request_id,
                                 model_name=request.model_name,
                                 prediction=prediction, confidence=float(confidence),
                                 latency_ms=latency)
        self.cache_result(key, result)
        return result

    def batch_infer(self, requests: List[InferenceRequest]) -> List[InferenceResult]:
        """Run inference for a batch of requests and return results in order."""
        return [self.infer(req) for req in requests]

    def get_model_info(self, name: str) -> Dict[str, Any]:
        """Return metadata and runtime stats for a registered model."""
        if name not in self._model_meta:
            return {"error": f"Model '{name}' not registered."}
        stats = self._call_stats.get(name, {})
        calls = stats.get("calls", 0)
        avg_lat = stats["total_latency_ms"] / calls if calls else 0.0
        return {**self._model_meta[name],
                "calls": calls, "errors": stats.get("errors", 0),
                "avg_latency_ms": round(avg_lat, 2)}

    def health_check(self) -> Dict[str, Any]:
        """Return overall system health and per-model error rates."""
        model_health = {}
        for name in self._models:
            info = self.get_model_info(name)
            calls = info.get("calls", 0)
            errors = info.get("errors", 0)
            model_health[name] = {
                "status": "degraded" if (calls > 0 and errors / calls > 0.1) else "healthy",
                "error_rate": round(errors / max(calls, 1), 3),
            }
        return {
            "status": "ok", "registered_models": len(self._models),
            "cache_entries": len(self._cache),
            "models": model_health,
            "checked_at": datetime.utcnow().isoformat(),
        }
