"""Automatic prompt optimisation using A/B testing and performance metrics."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable

import numpy as np
from loguru import logger

from llmops.prompts.prompt_templates import PromptTemplate


@dataclass
class OptimizationTrial:
    """A single optimisation trial comparing a candidate prompt to a baseline.

    Attributes:
        trial_id: Unique identifier.
        baseline_template: The current production prompt template.
        candidate_template: The challenger prompt template.
        metric_fn: Async callable that takes a rendered prompt and returns a
            scalar performance metric (higher is better).
        n_samples: Number of test samples to evaluate.
        results: Metric values collected during the trial.
    """

    trial_id: str
    baseline_template: PromptTemplate
    candidate_template: PromptTemplate
    metric_fn: Callable[[str], Awaitable[float]]
    n_samples: int = 50
    results: dict[str, list[float]] = field(default_factory=lambda: {"baseline": [], "candidate": []})


@dataclass
class OptimizationResult:
    """Outcome of a completed optimisation trial.

    Attributes:
        trial_id: Identifier of the completed trial.
        winner: ``"baseline"`` or ``"candidate"``.
        baseline_mean: Mean metric for the baseline.
        candidate_mean: Mean metric for the candidate.
        relative_improvement: Fractional improvement of winner over loser.
        p_value: Statistical significance p-value.
        significant: Whether the result is statistically significant.
        accepted: Whether the candidate was accepted as the new baseline.
    """

    trial_id: str
    winner: str
    baseline_mean: float
    candidate_mean: float
    relative_improvement: float
    p_value: float
    significant: bool
    accepted: bool


class PromptOptimizer:
    """Automatic prompt optimisation via sequential A/B trials.

    Generates prompt variants through simple mutations and evaluates
    them against a provided performance metric function.  Winning
    variants are promoted to become the new baseline.

    Attributes:
        best_templates: Best-known template per template name.
        trial_history: Completed trial results.
        _alpha: Statistical significance threshold.
    """

    def __init__(self, alpha: float = 0.05) -> None:
        """Initialise the prompt optimizer.

        Args:
            alpha: Significance level for hypothesis testing (default 0.05).
        """
        self.best_templates: dict[str, PromptTemplate] = {}
        self.trial_history: list[OptimizationResult] = []
        self._alpha = alpha
        logger.info("PromptOptimizer initialised (alpha={})", alpha)

    async def optimize(
        self,
        baseline: PromptTemplate,
        metric_fn: Callable[[str], Awaitable[float]],
        render_kwargs: dict[str, Any],
        n_samples: int = 50,
        n_variants: int = 3,
    ) -> PromptTemplate:
        """Optimise a prompt template through iterative A/B trials.

        Generates ``n_variants`` mutations of the baseline, evaluates each
        against ``metric_fn``, and returns the best-performing variant.

        Args:
            baseline: Starting prompt template.
            metric_fn: Async function scoring a rendered prompt (higher=better).
            render_kwargs: Variables for rendering the templates.
            n_samples: Evaluation samples per trial.
            n_variants: Number of candidate variants to generate.

        Returns:
            The best-performing :class:`PromptTemplate` (may be the original).

        Raises:
            ValueError: If ``n_variants`` < 1 or ``n_samples`` < 10.
        """
        if n_variants < 1:
            raise ValueError(f"n_variants must be ≥1, got {n_variants}")
        if n_samples < 10:
            raise ValueError(f"n_samples must be ≥10, got {n_samples}")

        current_best = self.best_templates.get(baseline.name, baseline)
        logger.info(
            "Optimising template '{}' with {} variants, {} samples each",
            baseline.name,
            n_variants,
            n_samples,
        )

        for i in range(n_variants):
            candidate = self._mutate(current_best, variant_idx=i)
            trial = OptimizationTrial(
                trial_id=str(uuid.uuid4()),
                baseline_template=current_best,
                candidate_template=candidate,
                metric_fn=metric_fn,
                n_samples=n_samples,
            )
            result = await self._run_trial(trial, render_kwargs)
            self.trial_history.append(result)

            if result.accepted:
                current_best = candidate
                self.best_templates[baseline.name] = candidate
                logger.info(
                    "Variant {} accepted for '{}' (improvement={:.2%})",
                    i + 1,
                    baseline.name,
                    result.relative_improvement,
                )
            else:
                logger.debug(
                    "Variant {} rejected for '{}' (improvement={:.2%}, p={:.4f})",
                    i + 1,
                    baseline.name,
                    result.relative_improvement,
                    result.p_value,
                )

        return current_best

    async def _run_trial(
        self,
        trial: OptimizationTrial,
        render_kwargs: dict[str, Any],
    ) -> OptimizationResult:
        """Execute a single A/B trial.

        Args:
            trial: Trial specification.
            render_kwargs: Template rendering variables.

        Returns:
            Completed :class:`OptimizationResult`.
        """
        baseline_prompt = trial.baseline_template.render(**render_kwargs)
        candidate_prompt = trial.candidate_template.render(**render_kwargs)

        baseline_scores: list[float] = []
        candidate_scores: list[float] = []

        for _ in range(trial.n_samples):
            await asyncio.sleep(0)
            b_score = await trial.metric_fn(baseline_prompt)
            c_score = await trial.metric_fn(candidate_prompt)
            baseline_scores.append(b_score)
            candidate_scores.append(c_score)

        b_mean = float(np.mean(baseline_scores))
        c_mean = float(np.mean(candidate_scores))
        p_value = self._t_test_p_value(
            np.asarray(baseline_scores), np.asarray(candidate_scores)
        )
        significant = p_value < self._alpha
        improvement = (c_mean - b_mean) / (abs(b_mean) + 1e-10)
        winner = "candidate" if c_mean > b_mean else "baseline"
        accepted = winner == "candidate" and significant

        return OptimizationResult(
            trial_id=trial.trial_id,
            winner=winner,
            baseline_mean=round(b_mean, 4),
            candidate_mean=round(c_mean, 4),
            relative_improvement=round(improvement, 4),
            p_value=round(p_value, 4),
            significant=significant,
            accepted=accepted,
        )

    def _mutate(self, template: PromptTemplate, variant_idx: int) -> PromptTemplate:
        """Generate a simple mutation of a template for evaluation.

        Applies light textual transformations to explore the prompt space.

        Args:
            template: Source template to mutate.
            variant_idx: Variant index (affects which mutation is applied).

        Returns:
            New :class:`PromptTemplate` with modified text.
        """
        mutations = [
            lambda t: t + "\n\nBe concise and precise in your response.",
            lambda t: "Think step by step.\n\n" + t,
            lambda t: t + "\n\nProvide a confidence score (0–100) with your answer.",
        ]
        mutation_fn = mutations[variant_idx % len(mutations)]
        new_template_str = mutation_fn(template.template)

        return PromptTemplate(
            name=template.name,
            template=new_template_str,
            required_vars=template.required_vars,
            description=f"{template.description} [variant {variant_idx + 1}]",
            version=f"{template.version}.{variant_idx + 1}",
        )

    @staticmethod
    def _t_test_p_value(a: np.ndarray, b: np.ndarray) -> float:
        """Compute a two-sided Welch t-test p-value.

        Args:
            a: Scores for group A.
            b: Scores for group B.

        Returns:
            Two-sided p-value approximated via normal distribution.
        """
        import math

        n_a, n_b = len(a), len(b)
        mean_a, mean_b = float(np.mean(a)), float(np.mean(b))
        var_a = float(np.var(a, ddof=1)) if n_a > 1 else 0.0
        var_b = float(np.var(b, ddof=1)) if n_b > 1 else 0.0

        se = math.sqrt(var_a / n_a + var_b / n_b + 1e-12)
        t_stat = abs((mean_a - mean_b) / se)
        p_value = 2 * (1 - 0.5 * (1 + math.erf(t_stat / math.sqrt(2))))
        return float(np.clip(p_value, 0.0, 1.0))
