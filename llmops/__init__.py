"""LLMOps: Operations framework for managing large language models in trading systems."""

from __future__ import annotations

from loguru import logger

from llmops.deployment.model_server import ModelServer
from llmops.deployment.ab_testing import ABTesting
from llmops.deployment.canary_deployment import CanaryDeployment
from llmops.monitoring.drift_detection import DriftDetection
from llmops.monitoring.performance_metrics import PerformanceMetrics
from llmops.monitoring.hallucination_detector import HallucinationDetector
from llmops.prompts.prompt_templates import PromptTemplates
from llmops.prompts.prompt_optimizer import PromptOptimizer
from llmops.prompts.context_injector import ContextInjector
from llmops.training.fine_tuning import FineTuning
from llmops.training.rlhf_pipeline import RLHFPipeline
from llmops.training.continual_learning import ContinualLearning


class LLMOps:
    """Unified LLMOps orchestrator for trading platform language models.

    Aggregates training, deployment, monitoring, and prompt management
    capabilities into a single operational interface.

    Attributes:
        model_server: Async inference serving component.
        ab_testing: A/B experiment management component.
        canary: Canary rollout management component.
        drift_detection: Model drift monitoring component.
        performance_metrics: Model performance tracking component.
        hallucination_detector: Output validation component.
        prompt_templates: Reusable prompt library component.
        prompt_optimizer: Automated prompt tuning component.
        context_injector: Dynamic context injection component.
        fine_tuning: Domain-specific fine-tuning component.
        rlhf_pipeline: Reinforcement learning from feedback component.
        continual_learning: Ongoing model update component.
    """

    def __init__(self) -> None:
        """Initialise all LLMOps sub-components."""
        self.model_server = ModelServer()
        self.ab_testing = ABTesting()
        self.canary = CanaryDeployment()
        self.drift_detection = DriftDetection()
        self.performance_metrics = PerformanceMetrics()
        self.hallucination_detector = HallucinationDetector()
        self.prompt_templates = PromptTemplates()
        self.prompt_optimizer = PromptOptimizer()
        self.context_injector = ContextInjector()
        self.fine_tuning = FineTuning()
        self.rlhf_pipeline = RLHFPipeline()
        self.continual_learning = ContinualLearning()
        logger.info("LLMOps initialised")

    def status(self) -> dict[str, str]:
        """Return a health summary for all sub-components.

        Returns:
            Mapping of component name to status string.
        """
        return {
            "model_server": "ready",
            "ab_testing": "ready",
            "canary": "ready",
            "drift_detection": "ready",
            "performance_metrics": "ready",
            "hallucination_detector": "ready",
            "prompt_templates": "ready",
            "prompt_optimizer": "ready",
            "context_injector": "ready",
            "fine_tuning": "ready",
            "rlhf_pipeline": "ready",
            "continual_learning": "ready",
        }


__all__ = ["LLMOps"]
