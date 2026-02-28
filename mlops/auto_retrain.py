"""Automated model retraining triggers."""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class RetrainTrigger:
    trigger_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    trigger_type: str = ""        # "drift" | "performance" | "schedule" | "data_volume"
    condition: str = ""
    threshold: float = 0.0
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    cooldown_hours: int = 24


@dataclass
class RetrainJob:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = ""
    trigger_id: str = ""
    trigger_type: str = ""
    status: str = "queued"     # queued | running | completed | failed | cancelled
    reason: str = ""
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    new_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AutoRetrainConfig:
    drift_threshold: float = 0.15
    performance_threshold: float = 0.75
    min_new_samples: int = 500
    schedule_hours: int = 168       # weekly by default
    max_concurrent_jobs: int = 2
    auto_promote: bool = False


class TriggerEvaluator:
    """Evaluates whether retraining conditions are met."""

    def evaluate_drift(self, trigger: RetrainTrigger, drift_score: float) -> bool:
        return trigger.enabled and drift_score >= trigger.threshold

    def evaluate_performance(self, trigger: RetrainTrigger, metric_value: float) -> bool:
        return trigger.enabled and metric_value <= trigger.threshold

    def evaluate_schedule(self, trigger: RetrainTrigger) -> bool:
        if not trigger.enabled:
            return False
        if trigger.last_triggered is None:
            return True
        elapsed = datetime.utcnow() - trigger.last_triggered
        return elapsed >= timedelta(hours=trigger.cooldown_hours)

    def evaluate_data_volume(self, trigger: RetrainTrigger, new_sample_count: int) -> bool:
        return trigger.enabled and new_sample_count >= trigger.threshold

    def is_on_cooldown(self, trigger: RetrainTrigger) -> bool:
        if trigger.last_triggered is None:
            return False
        elapsed = datetime.utcnow() - trigger.last_triggered
        return elapsed < timedelta(hours=trigger.cooldown_hours)


class AutoRetrain:
    """
    Automated retraining system that monitors model health signals
    and triggers retraining pipelines based on configurable rules.
    """

    def __init__(self, config: Optional[AutoRetrainConfig] = None) -> None:
        self._config = config or AutoRetrainConfig()
        self._triggers: Dict[str, List[RetrainTrigger]] = {}   # model_name -> triggers
        self._jobs: List[RetrainJob] = []
        self._evaluator = TriggerEvaluator()
        self._retraining_handlers: Dict[str, Callable] = {}
        logger.info("AutoRetrain initialized")

    def register_model(self, model_name: str) -> None:
        if model_name not in self._triggers:
            self._triggers[model_name] = []
            self._create_default_triggers(model_name)
            logger.info("Registered model '%s' for auto-retrain", model_name)

    def _create_default_triggers(self, model_name: str) -> None:
        self._triggers[model_name].extend([
            RetrainTrigger(model_name=model_name, trigger_type="drift",
                           condition="drift_score >= threshold",
                           threshold=self._config.drift_threshold),
            RetrainTrigger(model_name=model_name, trigger_type="performance",
                           condition="accuracy <= threshold",
                           threshold=self._config.performance_threshold),
            RetrainTrigger(model_name=model_name, trigger_type="schedule",
                           condition="elapsed_hours >= cooldown_hours",
                           threshold=0.0, cooldown_hours=self._config.schedule_hours),
            RetrainTrigger(model_name=model_name, trigger_type="data_volume",
                           condition="new_samples >= threshold",
                           threshold=float(self._config.min_new_samples)),
        ])

    def add_trigger(self, trigger: RetrainTrigger) -> None:
        self._triggers.setdefault(trigger.model_name, []).append(trigger)

    def register_handler(self, model_name: str, handler: Callable) -> None:
        """Register a callable that performs the actual retraining."""
        self._retraining_handlers[model_name] = handler

    def check_and_trigger(self, model_name: str,
                           drift_score: Optional[float] = None,
                           performance_metric: Optional[float] = None,
                           new_sample_count: Optional[int] = None) -> Optional[RetrainJob]:
        triggers = self._triggers.get(model_name, [])
        reason = ""
        triggered_trigger: Optional[RetrainTrigger] = None

        for trigger in triggers:
            if self._evaluator.is_on_cooldown(trigger):
                continue
            fired = False
            if trigger.trigger_type == "drift" and drift_score is not None:
                fired = self._evaluator.evaluate_drift(trigger, drift_score)
                if fired:
                    reason = f"Drift score {drift_score:.3f} >= {trigger.threshold:.3f}"
            elif trigger.trigger_type == "performance" and performance_metric is not None:
                fired = self._evaluator.evaluate_performance(trigger, performance_metric)
                if fired:
                    reason = f"Performance {performance_metric:.3f} <= {trigger.threshold:.3f}"
            elif trigger.trigger_type == "schedule":
                fired = self._evaluator.evaluate_schedule(trigger)
                if fired:
                    reason = "Scheduled retraining interval reached"
            elif trigger.trigger_type == "data_volume" and new_sample_count is not None:
                fired = self._evaluator.evaluate_data_volume(trigger, new_sample_count)
                if fired:
                    reason = f"New samples {new_sample_count} >= {int(trigger.threshold)}"

            if fired:
                triggered_trigger = trigger
                break

        if not triggered_trigger:
            return None

        # Check concurrent job limit
        running = [j for j in self._jobs if j.status == "running"]
        if len(running) >= self._config.max_concurrent_jobs:
            logger.warning("Max concurrent jobs (%d) reached for '%s'",
                           self._config.max_concurrent_jobs, model_name)
            return None

        job = RetrainJob(
            model_name=model_name,
            trigger_id=triggered_trigger.trigger_id,
            trigger_type=triggered_trigger.trigger_type,
            reason=reason,
        )
        self._jobs.append(job)
        triggered_trigger.last_triggered = datetime.utcnow()
        logger.info("Retrain triggered for '%s': %s", model_name, reason)
        self._execute_job(job)
        return job

    def _execute_job(self, job: RetrainJob) -> None:
        job.status = "running"
        job.started_at = datetime.utcnow()
        handler = self._retraining_handlers.get(job.model_name)
        try:
            if handler:
                result = handler(job.model_name)
                job.new_version = result.get("new_version") if isinstance(result, dict) else None
                job.metrics_after = result.get("metrics", {}) if isinstance(result, dict) else {}
            else:
                logger.info("[Simulated] Retraining '%s'", job.model_name)
                job.metrics_after = {"accuracy": 0.92, "f1": 0.91}
                job.new_version = "auto"
            job.status = "completed"
        except Exception as exc:
            job.status = "failed"
            job.metadata["error"] = str(exc)
            logger.error("Retrain job failed for '%s': %s", job.model_name, exc)
        finally:
            job.finished_at = datetime.utcnow()

    def get_jobs(self, model_name: Optional[str] = None,
                  status: Optional[str] = None) -> List[RetrainJob]:
        jobs = self._jobs
        if model_name:
            jobs = [j for j in jobs if j.model_name == model_name]
        if status:
            jobs = [j for j in jobs if j.status == status]
        return jobs

    def stats(self) -> Dict[str, Any]:
        from collections import Counter
        status_counts = Counter(j.status for j in self._jobs)
        return {
            "total_jobs": len(self._jobs),
            "by_status": dict(status_counts),
            "registered_models": list(self._triggers.keys()),
        }
