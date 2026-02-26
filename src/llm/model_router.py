"""Smart model router for cost and performance optimization."""
from enum import Enum
from typing import Dict, List, Optional

from ..observability.logging import get_logger
from .litellm_client import LiteLLMClient

logger = get_logger(__name__)


class TaskComplexity(str, Enum):
    """Task complexity levels."""

    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class ModelRouter:
    """Smart router for selecting optimal models based on task requirements."""

    def __init__(self, client: Optional[LiteLLMClient] = None):
        """Initialize model router.
        
        Args:
            client: LiteLLM client instance
        """
        self.client = client or LiteLLMClient()
        
        # Model characteristics
        self.model_metrics: Dict[str, Dict[str, float]] = {
            "gpt-3.5-turbo": {
                "cost": 0.001,
                "latency": 1.2,
                "quality": 7.0,
                "max_tokens": 16385,
            },
            "gpt-4-turbo": {
                "cost": 0.01,
                "latency": 2.5,
                "quality": 9.5,
                "max_tokens": 128000,
            },
            "gpt-4": {
                "cost": 0.03,
                "latency": 3.0,
                "quality": 9.0,
                "max_tokens": 8192,
            },
            "claude-3-sonnet": {
                "cost": 0.003,
                "latency": 2.0,
                "quality": 8.5,
                "max_tokens": 200000,
            },
            "claude-3-opus": {
                "cost": 0.015,
                "latency": 3.5,
                "quality": 9.8,
                "max_tokens": 200000,
            },
            "gemini-pro": {
                "cost": 0.00025,
                "latency": 1.5,
                "quality": 8.0,
                "max_tokens": 32760,
            },
            "mistral-large": {
                "cost": 0.004,
                "latency": 2.0,
                "quality": 8.5,
                "max_tokens": 32000,
            },
        }

        # Model availability tracking
        self.model_availability: Dict[str, bool] = {
            model: True for model in self.model_metrics.keys()
        }

    def select_model(
        self,
        task_complexity: TaskComplexity = TaskComplexity.MEDIUM,
        max_cost: Optional[float] = None,
        max_latency: Optional[float] = None,
        min_quality: Optional[float] = None,
        required_tokens: Optional[int] = None,
        preferred_providers: Optional[List[str]] = None,
    ) -> str:
        """Select optimal model based on requirements.
        
        Args:
            task_complexity: Complexity of the task
            max_cost: Maximum acceptable cost per 1K tokens
            max_latency: Maximum acceptable latency in seconds
            min_quality: Minimum quality score (0-10)
            required_tokens: Required token capacity
            preferred_providers: List of preferred providers
            
        Returns:
            Selected model name
        """
        # Default requirements by complexity
        complexity_defaults = {
            TaskComplexity.SIMPLE: {
                "max_cost": 0.005,
                "max_latency": 2.0,
                "min_quality": 7.0,
            },
            TaskComplexity.MEDIUM: {
                "max_cost": 0.01,
                "max_latency": 3.0,
                "min_quality": 8.0,
            },
            TaskComplexity.COMPLEX: {
                "max_cost": None,
                "max_latency": 5.0,
                "min_quality": 9.0,
            },
        }

        # Apply defaults
        defaults = complexity_defaults[task_complexity]
        max_cost = max_cost or defaults["max_cost"]
        max_latency = max_latency or defaults["max_latency"]
        min_quality = min_quality or defaults["min_quality"]

        # Filter models by requirements
        candidates = []
        for model, metrics in self.model_metrics.items():
            # Check availability
            if not self.model_availability.get(model, False):
                continue

            # Check constraints
            if max_cost and metrics["cost"] > max_cost:
                continue
            if max_latency and metrics["latency"] > max_latency:
                continue
            if min_quality and metrics["quality"] < min_quality:
                continue
            if required_tokens and metrics["max_tokens"] < required_tokens:
                continue

            # Check preferred providers
            if preferred_providers:
                provider = self._get_provider(model)
                if provider not in preferred_providers:
                    continue

            candidates.append((model, metrics))

        if not candidates:
            logger.warning(
                "No models match requirements, falling back to default",
                task_complexity=task_complexity,
                max_cost=max_cost,
                max_latency=max_latency,
                min_quality=min_quality,
            )
            return "gpt-3.5-turbo"

        # Score and rank candidates
        # Score = quality / (cost * latency)
        scored_candidates = []
        for model, metrics in candidates:
            score = metrics["quality"] / (metrics["cost"] * metrics["latency"])
            scored_candidates.append((model, score))

        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        selected_model = scored_candidates[0][0]

        logger.info(
            "Model selected",
            model=selected_model,
            task_complexity=task_complexity,
            candidates=len(candidates),
        )

        return selected_model

    def mark_unavailable(self, model: str) -> None:
        """Mark a model as unavailable.
        
        Args:
            model: Model name
        """
        self.model_availability[model] = False
        logger.warning("Model marked as unavailable", model=model)

    def mark_available(self, model: str) -> None:
        """Mark a model as available.
        
        Args:
            model: Model name
        """
        self.model_availability[model] = True
        logger.info("Model marked as available", model=model)

    def get_fallback_models(self, primary_model: str) -> List[str]:
        """Get fallback models for a primary model.
        
        Args:
            primary_model: Primary model name
            
        Returns:
            List of fallback models
        """
        fallback_chains = {
            "gemini-pro": ["gpt-4-turbo", "claude-3-sonnet"],
            "gpt-4-turbo": ["claude-3-opus", "gemini-pro"],
            "claude-3-opus": ["gpt-4-turbo", "gemini-pro"],
            "gpt-3.5-turbo": ["gemini-pro", "mistral-large"],
        }

        fallbacks = fallback_chains.get(primary_model, ["gpt-3.5-turbo"])
        # Filter to available models
        return [m for m in fallbacks if self.model_availability.get(m, False)]

    def _get_provider(self, model: str) -> str:
        """Get provider from model name.
        
        Args:
            model: Model name
            
        Returns:
            Provider name
        """
        if "gpt" in model:
            return "openai"
        elif "claude" in model:
            return "anthropic"
        elif "gemini" in model:
            return "google"
        elif "mistral" in model:
            return "mistral"
        else:
            return "unknown"

    def optimize_for_cost(self) -> str:
        """Get the most cost-effective available model.
        
        Returns:
            Model name
        """
        available_models = [
            (model, metrics)
            for model, metrics in self.model_metrics.items()
            if self.model_availability.get(model, False)
        ]

        if not available_models:
            return "gpt-3.5-turbo"

        # Sort by cost (lowest first)
        available_models.sort(key=lambda x: x[1]["cost"])
        return available_models[0][0]

    def optimize_for_latency(self) -> str:
        """Get the fastest available model.
        
        Returns:
            Model name
        """
        available_models = [
            (model, metrics)
            for model, metrics in self.model_metrics.items()
            if self.model_availability.get(model, False)
        ]

        if not available_models:
            return "gpt-3.5-turbo"

        # Sort by latency (lowest first)
        available_models.sort(key=lambda x: x[1]["latency"])
        return available_models[0][0]

    def optimize_for_quality(self) -> str:
        """Get the highest quality available model.
        
        Returns:
            Model name
        """
        available_models = [
            (model, metrics)
            for model, metrics in self.model_metrics.items()
            if self.model_availability.get(model, False)
        ]

        if not available_models:
            return "gpt-4-turbo"

        # Sort by quality (highest first)
        available_models.sort(key=lambda x: x[1]["quality"], reverse=True)
        return available_models[0][0]


# Global router instance
router = ModelRouter()
