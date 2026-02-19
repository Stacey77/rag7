"""Core AGI reasoning engine with contextual multi-domain problem solving."""
from __future__ import annotations

import logging
import math
import re
import time
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ReasoningContext:
    """Holds context for a reasoning session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = "general"
    history: List[Dict[str, Any]] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.7
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReasoningStep:
    """Single step in a reasoning chain."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    domain: str = "general"
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ReasoningResult:
    """Result of a reasoning process."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conclusion: str = ""
    steps: List[ReasoningStep] = field(default_factory=list)
    confidence: float = 0.0
    domain: str = "general"
    alternatives: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReasoningStrategy(ABC):
    """Abstract base class for reasoning strategies."""

    @abstractmethod
    def reason(self, problem: str, context: ReasoningContext) -> ReasoningResult:
        pass

    @abstractmethod
    def can_handle(self, domain: str) -> bool:
        pass


class DeductiveReasoner(ReasoningStrategy):
    """Applies deductive reasoning: general rules -> specific conclusions."""

    RULES: Dict[str, List[str]] = {
        "infrastructure": ["high_cpu => scale_out", "low_memory => add_ram", "network_latency => check_routing"],
        "security": ["open_port => vulnerability_check", "failed_auth => alert", "data_leak => quarantine"],
        "performance": ["slow_query => optimize_index", "high_io => cache_layer", "memory_leak => restart_service"],
    }

    def can_handle(self, domain: str) -> bool:
        return domain in self.RULES or domain == "general"

    def reason(self, problem: str, context: ReasoningContext) -> ReasoningResult:
        steps: List[ReasoningStep] = []
        rules = self.RULES.get(context.domain, [r for rules in self.RULES.values() for r in rules])

        matched: List[str] = []
        for rule in rules:
            antecedent, consequent = rule.split(" => ")
            if antecedent.replace("_", " ") in problem.lower() or antecedent in problem.lower():
                matched.append(consequent)
                steps.append(ReasoningStep(
                    description=f"Applied rule: {rule}",
                    inputs={"rule": rule, "problem": problem},
                    outputs={"conclusion": consequent},
                    confidence=0.85,
                    domain=context.domain,
                ))

        conclusion = "; ".join(matched) if matched else "No direct rule matches found; applying heuristics."
        confidence = min(0.95, 0.5 + 0.15 * len(matched))
        return ReasoningResult(
            conclusion=conclusion,
            steps=steps,
            confidence=confidence,
            domain=context.domain,
            alternatives=[f"Consider: {r}" for r in rules if r not in matched][:3],
        )


class InductiveReasoner(ReasoningStrategy):
    """Infers general patterns from specific observations."""

    def can_handle(self, domain: str) -> bool:
        return True

    def reason(self, problem: str, context: ReasoningContext) -> ReasoningResult:
        steps: List[ReasoningStep] = []
        history_patterns = self._extract_patterns(context.history)
        observations = self._tokenize(problem)

        pattern_matches = sum(1 for p in history_patterns if p in observations)
        pattern_ratio = pattern_matches / max(len(history_patterns), 1)

        steps.append(ReasoningStep(
            description="Extracted observations from problem statement",
            inputs={"problem": problem},
            outputs={"observations": observations},
            confidence=0.9,
        ))
        steps.append(ReasoningStep(
            description=f"Matched {pattern_matches}/{len(history_patterns)} historical patterns",
            inputs={"patterns": history_patterns, "observations": observations},
            outputs={"match_ratio": pattern_ratio},
            confidence=0.75 + 0.2 * pattern_ratio,
        ))

        conclusion = (
            f"Based on {len(context.history)} historical cases, pattern similarity is "
            f"{pattern_ratio:.1%}. Recommend action consistent with similar past outcomes."
        )
        return ReasoningResult(
            conclusion=conclusion,
            steps=steps,
            confidence=0.6 + 0.3 * pattern_ratio,
            domain=context.domain,
        )

    def _extract_patterns(self, history: List[Dict[str, Any]]) -> List[str]:
        tokens: List[str] = []
        for entry in history[-10:]:
            text = str(entry.get("problem", "")) + " " + str(entry.get("conclusion", ""))
            tokens.extend(self._tokenize(text))
        return list(set(tokens))

    def _tokenize(self, text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b\w{4,}\b", text)]


class AbductiveReasoner(ReasoningStrategy):
    """Generates best-explanation hypotheses for observations."""

    HYPOTHESES_TEMPLATES: List[str] = [
        "The most likely cause is {cause} given the observed {symptom}.",
        "Hypothesis: {symptom} results from {cause} under current conditions.",
        "Best explanation: {cause} accounts for the majority of observed {symptom}.",
    ]

    def can_handle(self, domain: str) -> bool:
        return True

    def reason(self, problem: str, context: ReasoningContext) -> ReasoningResult:
        keywords = re.findall(r"\b\w{4,}\b", problem.lower())
        symptom = keywords[0] if keywords else "unknown_symptom"
        cause = keywords[-1] if len(keywords) > 1 else "undetermined_cause"

        hypotheses = [
            t.format(cause=cause, symptom=symptom) for t in self.HYPOTHESES_TEMPLATES
        ]
        steps = [
            ReasoningStep(
                description="Identified symptoms and generated causal hypotheses",
                inputs={"problem": problem},
                outputs={"symptom": symptom, "cause": cause, "hypotheses": hypotheses},
                confidence=0.72,
            )
        ]
        return ReasoningResult(
            conclusion=hypotheses[0],
            steps=steps,
            confidence=0.72,
            domain=context.domain,
            alternatives=hypotheses[1:],
        )


class ReasoningEngine:
    """
    Core AGI reasoning engine combining multiple reasoning strategies
    with adaptive selection, meta-learning integration, and multi-domain support.
    """

    DOMAIN_KEYWORDS: Dict[str, List[str]] = {
        "infrastructure": ["server", "cpu", "memory", "network", "latency", "scale"],
        "security": ["auth", "token", "vulnerability", "breach", "encrypt", "threat"],
        "performance": ["slow", "latency", "throughput", "optimize", "bottleneck"],
        "data": ["database", "query", "schema", "pipeline", "etl", "dataset"],
    }

    def __init__(self) -> None:
        self.strategies: List[ReasoningStrategy] = [
            DeductiveReasoner(),
            InductiveReasoner(),
            AbductiveReasoner(),
        ]
        self.reasoning_history: deque = deque(maxlen=100)
        self.domain_performance: Dict[str, List[float]] = defaultdict(list)
        logger.info("ReasoningEngine initialized with %d strategies", len(self.strategies))

    def infer_domain(self, problem: str) -> str:
        problem_lower = problem.lower()
        scores: Dict[str, int] = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            scores[domain] = sum(1 for kw in keywords if kw in problem_lower)
        best = max(scores, key=lambda d: scores[d])
        return best if scores[best] > 0 else "general"

    def solve(self, problem: str, context: Optional[ReasoningContext] = None) -> ReasoningResult:
        if context is None:
            context = ReasoningContext()
        if context.domain == "general":
            context.domain = self.infer_domain(problem)

        logger.debug("Solving problem in domain '%s': %.80s...", context.domain, problem)
        start = time.perf_counter()

        applicable = [s for s in self.strategies if s.can_handle(context.domain)]
        results: List[ReasoningResult] = []
        for strategy in applicable:
            try:
                result = strategy.reason(problem, context)
                results.append(result)
            except Exception as exc:
                logger.warning("Strategy %s failed: %s", type(strategy).__name__, exc)

        best = max(results, key=lambda r: r.confidence) if results else ReasoningResult(
            conclusion="Unable to reason about the problem.",
            confidence=0.0,
        )
        best.metadata["elapsed_ms"] = round((time.perf_counter() - start) * 1000, 2)
        best.metadata["strategies_used"] = [type(s).__name__ for s in applicable]

        self.reasoning_history.append({"problem": problem, "domain": context.domain, "confidence": best.confidence})
        self.domain_performance[context.domain].append(best.confidence)
        context.history.append({"problem": problem, "conclusion": best.conclusion, "confidence": best.confidence})

        logger.info("Reasoning complete. Domain: %s, Confidence: %.2f", best.domain, best.confidence)
        return best

    def multi_step_reason(self, problem: str, steps: int = 3, context: Optional[ReasoningContext] = None) -> List[ReasoningResult]:
        """Iterative deepening reasoning over multiple passes."""
        if context is None:
            context = ReasoningContext()
        results: List[ReasoningResult] = []
        current_problem = problem
        for i in range(steps):
            result = self.solve(current_problem, context)
            results.append(result)
            current_problem = f"{result.conclusion} — further analysis required."
            logger.debug("Multi-step iteration %d confidence: %.2f", i + 1, result.confidence)
            if result.confidence >= context.confidence_threshold:
                break
        return results

    def domain_accuracy(self) -> Dict[str, float]:
        return {
            domain: sum(scores) / len(scores)
            for domain, scores in self.domain_performance.items()
            if scores
        }

    def adaptive_select_strategy(self, domain: str) -> ReasoningStrategy:
        """Select best-performing strategy for domain based on history."""
        history = [h for h in self.reasoning_history if h["domain"] == domain]
        if not history:
            return self.strategies[0]
        avg_confidence = sum(h["confidence"] for h in history) / len(history)
        idx = min(int(avg_confidence * len(self.strategies)), len(self.strategies) - 1)
        return self.strategies[idx]

    def explain(self, result: ReasoningResult) -> str:
        """Return human-readable explanation of a reasoning result."""
        lines = [
            f"Conclusion: {result.conclusion}",
            f"Confidence: {result.confidence:.1%}",
            f"Domain: {result.domain}",
            f"Reasoning steps ({len(result.steps)}):",
        ]
        for i, step in enumerate(result.steps, 1):
            lines.append(f"  {i}. {step.description} (confidence: {step.confidence:.1%})")
        if result.alternatives:
            lines.append("Alternatives considered:")
            for alt in result.alternatives:
                lines.append(f"  - {alt}")
        return "\n".join(lines)
