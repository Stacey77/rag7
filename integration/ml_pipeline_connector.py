"""Connect MLOps components into a unified inference and training pipeline."""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PipelineConnector:
    """Bridge between ML registries, feature stores, monitors, and runtime pipelines."""

    def __init__(self) -> None:
        self._registry: Optional[Any] = None
        self._feature_store: Optional[Any] = None
        self._monitor: Optional[Any] = None
        self._training_history: List[Dict[str, Any]] = []
        self._inference_cache: Dict[str, Any] = {}
        logger.info("PipelineConnector initialised.")

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def connect_registry(self, registry: Any) -> None:
        """Attach a model registry (must expose .get_model(name) and .list_models())."""
        self._registry = registry
        logger.info("Model registry connected: %s", type(registry).__name__)

    def connect_feature_store(self, store: Any) -> None:
        """Attach a feature store (must expose .get_features(keys))."""
        self._feature_store = store
        logger.info("Feature store connected: %s", type(store).__name__)

    def connect_monitor(self, monitor: Any) -> None:
        """Attach a model monitor (must expose .record(model_name, prediction, latency))."""
        self._monitor = monitor
        logger.info("Monitor connected: %s", type(monitor).__name__)

    # ------------------------------------------------------------------
    # Core pipeline operations
    # ------------------------------------------------------------------

    def run_inference_pipeline(self, input_data: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        Execute a full inference pipeline:
        1. Optionally enrich input from the feature store.
        2. Fetch the model from the registry.
        3. Run prediction (or return a stub if no real model).
        4. Record results with the monitor.
        """
        t0 = time.monotonic()
        cache_key = f"{model_name}:{hash(str(input_data))}"
        if cache_key in self._inference_cache:
            logger.debug("Cache hit for model=%s", model_name)
            return {**self._inference_cache[cache_key], "cached": True}

        # Feature enrichment
        features = dict(input_data)
        if self._feature_store is not None:
            try:
                extra = self._feature_store.get_features(list(input_data.keys()))
                features.update(extra or {})
            except Exception as exc:  # noqa: BLE001
                logger.warning("Feature store enrichment failed: %s", exc)

        # Model invocation (stub if no registry)
        prediction: Any
        if self._registry is not None:
            try:
                model = self._registry.get_model(model_name)
                prediction = model.predict(features) if hasattr(model, "predict") else str(features)
            except Exception as exc:  # noqa: BLE001
                logger.error("Model inference failed: %s", exc)
                return {"success": False, "error": str(exc), "model": model_name}
        else:
            prediction = {"stub_prediction": sum(v for v in features.values() if isinstance(v, (int, float)))}

        latency_ms = round((time.monotonic() - t0) * 1000, 2)

        if self._monitor is not None:
            try:
                self._monitor.record(model_name, prediction, latency_ms)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Monitor recording failed: %s", exc)

        result = {"model": model_name, "prediction": prediction,
                  "latency_ms": latency_ms, "success": True, "cached": False}
        self._inference_cache[cache_key] = result
        return result

    def trigger_training(self, trigger_reason: str) -> Dict[str, Any]:
        """Log a training trigger event (scheduling is handled externally)."""
        event = {"reason": trigger_reason, "triggered_at": datetime.utcnow().isoformat(),
                 "status": "queued"}
        self._training_history.append(event)
        logger.info("Training triggered: reason=%s", trigger_reason)
        return event

    def health_check(self) -> Dict[str, Any]:
        """Return connectivity status for all attached components."""
        return {
            "registry": "connected" if self._registry else "disconnected",
            "feature_store": "connected" if self._feature_store else "disconnected",
            "monitor": "connected" if self._monitor else "disconnected",
            "cache_size": len(self._inference_cache),
            "training_events": len(self._training_history),
            "checked_at": datetime.utcnow().isoformat(),
        }
