"""Automated ML training pipeline orchestration."""
from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PipelineStep:
    name: str
    func: Callable
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    retry_count: int = 1
    timeout_seconds: int = 300
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    step_name: str
    status: str = "pending"    # pending | running | success | failed | skipped
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    elapsed_seconds: float = 0.0
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


@dataclass
class PipelineRun:
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pipeline_name: str = ""
    status: str = "pending"
    step_results: List[StepResult] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class StepExecutor:
    """Executes a single pipeline step with retry logic."""

    def execute(self, step: PipelineStep, context: Dict[str, Any]) -> StepResult:
        result = StepResult(step_name=step.name, started_at=datetime.utcnow())
        result.status = "running"
        start = time.perf_counter()

        for attempt in range(step.retry_count):
            try:
                inputs = {k: context[k] for k in step.inputs if k in context}
                output = step.func(**inputs)
                if output is None:
                    output = {}
                if not isinstance(output, dict):
                    output = {"result": output}
                result.outputs = output
                result.status = "success"
                break
            except Exception as exc:
                logger.warning("Step '%s' attempt %d failed: %s", step.name, attempt + 1, exc)
                result.error = str(exc)
                result.status = "failed"
                if attempt < step.retry_count - 1:
                    time.sleep(0.1 * (attempt + 1))

        result.elapsed_seconds = time.perf_counter() - start
        result.finished_at = datetime.utcnow()
        return result


class TrainingPipeline:
    """
    Automated ML training pipeline with step registration,
    dependency resolution, execution, and run tracking.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._steps: List[PipelineStep] = []
        self._runs: List[PipelineRun] = []
        self._executor = StepExecutor()
        logger.info("TrainingPipeline '%s' initialized", name)

    def add_step(self, name: str, func: Callable,
                 inputs: Optional[List[str]] = None,
                 outputs: Optional[List[str]] = None,
                 retry_count: int = 1) -> "TrainingPipeline":
        step = PipelineStep(name=name, func=func,
                            inputs=inputs or [], outputs=outputs or [],
                            retry_count=retry_count)
        self._steps.append(step)
        return self

    def _topological_sort(self) -> List[PipelineStep]:
        """Order steps by data dependency (outputs -> inputs)."""
        available: set = set()
        ordered: List[PipelineStep] = []
        remaining = list(self._steps)

        max_iterations = len(remaining) ** 2 + 1
        iteration = 0
        while remaining:
            iteration += 1
            if iteration > max_iterations:
                # Break cycle: just append rest
                ordered.extend(remaining)
                break
            for step in list(remaining):
                if all(inp in available for inp in step.inputs):
                    ordered.append(step)
                    available.update(step.outputs)
                    remaining.remove(step)
        return ordered

    def run(self, parameters: Optional[Dict[str, Any]] = None) -> PipelineRun:
        run = PipelineRun(pipeline_name=self.name,
                          parameters=parameters or {},
                          started_at=datetime.utcnow())
        run.status = "running"
        context: Dict[str, Any] = dict(parameters or {})

        ordered_steps = self._topological_sort()
        logger.info("Starting pipeline '%s' (%d steps)", self.name, len(ordered_steps))

        for step in ordered_steps:
            logger.debug("Executing step '%s'", step.name)
            step_result = self._executor.execute(step, context)
            run.step_results.append(step_result)

            if step_result.status == "success":
                context.update(step_result.outputs)
                # Collect metrics from step outputs
                for k, v in step_result.outputs.items():
                    if isinstance(v, (int, float)) and k.startswith("metric_"):
                        run.metrics[k[7:]] = v
            else:
                run.status = "failed"
                logger.error("Pipeline '%s' failed at step '%s': %s",
                             self.name, step.name, step_result.error)
                break
        else:
            run.status = "success"

        run.finished_at = datetime.utcnow()
        run.artifacts = {k: v for k, v in context.items()
                         if k not in (parameters or {})}
        self._runs.append(run)

        elapsed = (run.finished_at - run.started_at).total_seconds()
        logger.info("Pipeline '%s' %s in %.2fs", self.name, run.status, elapsed)
        return run

    def get_run(self, run_id: str) -> Optional[PipelineRun]:
        return next((r for r in self._runs if r.run_id == run_id), None)

    def list_runs(self, status: Optional[str] = None) -> List[PipelineRun]:
        if status:
            return [r for r in self._runs if r.status == status]
        return list(self._runs)

    def last_run(self) -> Optional[PipelineRun]:
        return self._runs[-1] if self._runs else None

    @property
    def step_names(self) -> List[str]:
        return [s.name for s in self._steps]

    @property
    def run_stats(self) -> Dict[str, Any]:
        if not self._runs:
            return {"total": 0}
        statuses = defaultdict(int)
        for r in self._runs:
            statuses[r.status] += 1
        return {"total": len(self._runs), "by_status": dict(statuses)}


# ----- Convenience factory functions -----

def make_data_pipeline(name: str = "data_prep") -> TrainingPipeline:
    """Build a standard data preparation pipeline."""
    import statistics

    def load_data(data_path: str = "data.csv") -> Dict[str, Any]:
        logger.info("Loading data from %s", data_path)
        return {"raw_data": list(range(100)), "data_path": data_path}

    def validate_data(raw_data: list) -> Dict[str, Any]:
        valid = [x for x in raw_data if x is not None]
        return {"validated_data": valid, "metric_validation_rate": len(valid) / len(raw_data)}

    def feature_engineer(validated_data: list) -> Dict[str, Any]:
        features = [float(x) / max(validated_data) for x in validated_data]
        return {"features": features, "metric_feature_count": len(features)}

    def split_data(features: list) -> Dict[str, Any]:
        n = len(features)
        split = int(n * 0.8)
        return {"train_features": features[:split], "test_features": features[split:]}

    pipeline = TrainingPipeline(name)
    pipeline.add_step("load_data", load_data, outputs=["raw_data"])
    pipeline.add_step("validate_data", validate_data, inputs=["raw_data"], outputs=["validated_data"])
    pipeline.add_step("feature_engineer", feature_engineer, inputs=["validated_data"], outputs=["features"])
    pipeline.add_step("split_data", split_data, inputs=["features"],
                      outputs=["train_features", "test_features"])
    return pipeline
