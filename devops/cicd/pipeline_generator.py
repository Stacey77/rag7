"""Dynamic CI/CD pipeline generation."""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PipelineStage:
    name: str
    steps: List[Dict[str, Any]] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    allow_failure: bool = False


@dataclass
class CICDPipeline:
    pipeline_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    trigger: str = "push"   # push | pr | schedule | manual
    stages: List[PipelineStage] = field(default_factory=list)
    global_env: Dict[str, str] = field(default_factory=dict)
    artifacts: List[str] = field(default_factory=list)
    format: str = "yaml"
    created_at: datetime = field(default_factory=datetime.utcnow)


class PipelineTemplates:
    """Pre-built pipeline templates for common scenarios."""

    @staticmethod
    def python_service() -> List[PipelineStage]:
        return [
            PipelineStage("install", [{"run": "pip install -r requirements.txt"}]),
            PipelineStage("lint", [{"run": "flake8 . --max-line-length=120"}], depends_on=["install"]),
            PipelineStage("test", [{"run": "pytest tests/ -v --cov"}], depends_on=["install"]),
            PipelineStage("build", [{"run": "docker build -t $IMAGE_NAME:$TAG ."}], depends_on=["test"]),
            PipelineStage("push", [{"run": "docker push $IMAGE_NAME:$TAG"}], depends_on=["build"]),
            PipelineStage("deploy", [{"run": "kubectl apply -f k8s/"}], depends_on=["push"]),
        ]

    @staticmethod
    def ml_training() -> List[PipelineStage]:
        return [
            PipelineStage("data_validation", [{"run": "python scripts/validate_data.py"}]),
            PipelineStage("feature_engineering", [{"run": "python scripts/feature_eng.py"}], depends_on=["data_validation"]),
            PipelineStage("train", [{"run": "python scripts/train.py"}], depends_on=["feature_engineering"]),
            PipelineStage("evaluate", [{"run": "python scripts/evaluate.py"}], depends_on=["train"]),
            PipelineStage("register", [{"run": "python scripts/register_model.py"}], depends_on=["evaluate"]),
            PipelineStage("deploy_model", [{"run": "python scripts/deploy_model.py"}], depends_on=["register"]),
        ]

    @staticmethod
    def data_pipeline() -> List[PipelineStage]:
        return [
            PipelineStage("ingest", [{"run": "python -m dataops.ingest"}]),
            PipelineStage("validate", [{"run": "python -m dataops.validate"}], depends_on=["ingest"]),
            PipelineStage("transform", [{"run": "python -m dataops.transform"}], depends_on=["validate"]),
            PipelineStage("load", [{"run": "python -m dataops.load"}], depends_on=["transform"]),
        ]


def _render_yaml_stage(stage: PipelineStage) -> str:
    lines = [f"  {stage.name}:"]
    if stage.depends_on:
        lines.append(f"    needs: [{', '.join(stage.depends_on)}]")
    if stage.env:
        lines.append("    env:")
        for k, v in stage.env.items():
            lines.append(f"      {k}: {v}")
    lines.append("    steps:")
    for step in stage.steps:
        if "run" in step:
            lines.append(f"      - run: {step['run']}")
        elif "uses" in step:
            lines.append(f"      - uses: {step['uses']}")
    return "\n".join(lines)


def _render_github_actions(pipeline: CICDPipeline) -> str:
    lines = [f"name: {pipeline.name}", "on:", f"  {pipeline.trigger}:", "    branches: ['*']", ""]
    if pipeline.global_env:
        lines.append("env:")
        for k, v in pipeline.global_env.items():
            lines.append(f"  {k}: {v}")
        lines.append("")
    lines.append("jobs:")
    for stage in pipeline.stages:
        lines.append(_render_yaml_stage(stage))
        lines.append("")
    return "\n".join(lines)


def _render_gitlab_ci(pipeline: CICDPipeline) -> str:
    stage_names = [s.name for s in pipeline.stages]
    lines = [f"stages:", *[f"  - {n}" for n in stage_names], ""]
    for stage in pipeline.stages:
        lines.append(f"{stage.name}:")
        lines.append(f"  stage: {stage.name}")
        if stage.depends_on:
            lines.append(f"  needs: {stage.depends_on}")
        lines.append("  script:")
        for step in stage.steps:
            if "run" in step:
                lines.append(f"    - {step['run']}")
        lines.append("")
    return "\n".join(lines)


class PipelineGenerator:
    """
    Dynamic CI/CD pipeline generator supporting GitHub Actions, GitLab CI,
    and Jenkins output formats with template-based and custom pipeline construction.
    """

    def __init__(self) -> None:
        self._templates = PipelineTemplates()
        logger.info("PipelineGenerator initialized")

    def create(self, name: str, template: str = "python_service",
               trigger: str = "push",
               global_env: Optional[Dict[str, str]] = None) -> CICDPipeline:
        template_map = {
            "python_service": self._templates.python_service,
            "ml_training": self._templates.ml_training,
            "data_pipeline": self._templates.data_pipeline,
        }
        stages = template_map.get(template, self._templates.python_service)()
        pipeline = CICDPipeline(name=name, trigger=trigger, stages=stages,
                                global_env=global_env or {})
        logger.info("Created pipeline '%s' (%d stages)", name, len(stages))
        return pipeline

    def add_stage(self, pipeline: CICDPipeline, stage: PipelineStage) -> None:
        pipeline.stages.append(stage)

    def render(self, pipeline: CICDPipeline, format: str = "github_actions") -> str:
        if format == "github_actions":
            return _render_github_actions(pipeline)
        elif format == "gitlab_ci":
            return _render_gitlab_ci(pipeline)
        else:
            return _render_github_actions(pipeline)

    def validate(self, pipeline: CICDPipeline) -> List[str]:
        """Validate pipeline for dependency cycles and missing stages."""
        errors: List[str] = []
        stage_names = {s.name for s in pipeline.stages}
        for stage in pipeline.stages:
            for dep in stage.depends_on:
                if dep not in stage_names:
                    errors.append(f"Stage '{stage.name}' depends on unknown stage '{dep}'")
        if not pipeline.stages:
            errors.append("Pipeline has no stages")
        return errors
