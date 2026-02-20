"""Hallucination detection for LLM outputs using consistency and confidence checks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class HallucinationReport:
    """Result of a hallucination detection evaluation.

    Attributes:
        output_id: Identifier for the evaluated output.
        is_hallucination: Whether a hallucination was detected.
        confidence_score: Model's self-reported confidence (0–1).
        consistency_score: Internal consistency across multiple samples (0–1).
        factual_score: Factual grounding score (0–1).
        risk_level: Categorical risk (``"low"``, ``"medium"``, ``"high"``).
        flags: Specific issues detected.
        evaluated_at: UTC timestamp.
    """

    output_id: str
    is_hallucination: bool
    confidence_score: float
    consistency_score: float
    factual_score: float
    risk_level: str
    flags: list[str] = field(default_factory=list)
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# Patterns that correlate with low-confidence or hallucinated responses
_UNCERTAINTY_PATTERNS: list[str] = [
    r"\bi (think|believe|suppose|assume)\b",
    r"\b(probably|possibly|perhaps|maybe|might be|could be)\b",
    r"\bi('m| am) not (sure|certain|confident)\b",
    r"\b(i|we) cannot (confirm|verify|guarantee)\b",
    r"\bapproximately\b",
]

_CONTRADICTION_MARKERS: list[str] = [
    r"\bhowever\b.*\bbut\b",
    r"\bon the other hand\b",
    r"\bcontradicts?\b",
]


class HallucinationDetector:
    """LLM output validation using consistency checks and confidence scoring.

    Uses three complementary signals:
    1. **Confidence scoring**: Linguistic uncertainty patterns in the output.
    2. **Consistency checking**: Agreement across multiple sampled outputs.
    3. **Factual grounding**: Overlap with provided ground-truth context.

    Attributes:
        detection_history: All past detection reports.
        _confidence_threshold: Minimum confidence before flagging.
        _consistency_threshold: Minimum consistency score before flagging.
        _factual_threshold: Minimum factual overlap before flagging.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        consistency_threshold: float = 0.7,
        factual_threshold: float = 0.5,
    ) -> None:
        """Initialise the hallucination detector.

        Args:
            confidence_threshold: Outputs below this confidence are flagged.
            consistency_threshold: Outputs below this consistency are flagged.
            factual_threshold: Outputs below this factual overlap are flagged.
        """
        self.detection_history: list[HallucinationReport] = []
        self._confidence_threshold = confidence_threshold
        self._consistency_threshold = consistency_threshold
        self._factual_threshold = factual_threshold
        self._uncertainty_re = [
            re.compile(p, re.IGNORECASE) for p in _UNCERTAINTY_PATTERNS
        ]
        self._contradiction_re = [
            re.compile(p, re.IGNORECASE) for p in _CONTRADICTION_MARKERS
        ]
        logger.info(
            "HallucinationDetector initialised (conf={}, consist={}, fact={})",
            confidence_threshold,
            consistency_threshold,
            factual_threshold,
        )

    def detect(
        self,
        output: str,
        output_id: str | None = None,
        context: str | None = None,
        sampled_outputs: list[str] | None = None,
    ) -> HallucinationReport:
        """Evaluate a single LLM output for hallucination signals.

        Args:
            output: The LLM-generated text to evaluate.
            output_id: Optional identifier (auto-generated if ``None``).
            context: Optional ground-truth or retrieval context for factual
                grounding check.
            sampled_outputs: Optional list of alternative outputs sampled at
                higher temperature for consistency checking.

        Returns:
            :class:`HallucinationReport` with all scoring results.

        Raises:
            ValueError: If ``output`` is empty.
        """
        if not output.strip():
            raise ValueError("output must not be empty")

        oid = output_id or f"output_{len(self.detection_history)}"
        flags: list[str] = []

        confidence_score = self._score_confidence(output, flags)
        consistency_score = self._score_consistency(output, sampled_outputs, flags)
        factual_score = self._score_factual(output, context, flags)

        is_hallucination = (
            confidence_score < self._confidence_threshold
            or consistency_score < self._consistency_threshold
            or factual_score < self._factual_threshold
        )
        risk_level = self._compute_risk(confidence_score, consistency_score, factual_score)

        report = HallucinationReport(
            output_id=oid,
            is_hallucination=is_hallucination,
            confidence_score=round(confidence_score, 4),
            consistency_score=round(consistency_score, 4),
            factual_score=round(factual_score, 4),
            risk_level=risk_level,
            flags=flags,
        )
        self.detection_history.append(report)

        if is_hallucination:
            logger.warning(
                "Hallucination detected (id={}) — risk={}, flags={}",
                oid,
                risk_level,
                flags,
            )
        else:
            logger.debug("Output '{}' passed hallucination checks (risk={})", oid, risk_level)

        return report

    def batch_detect(
        self,
        outputs: list[str],
        context: str | None = None,
    ) -> list[HallucinationReport]:
        """Evaluate a batch of outputs.

        Args:
            outputs: List of LLM-generated texts.
            context: Shared context for factual grounding checks.

        Returns:
            List of :class:`HallucinationReport` in the same order.
        """
        return [
            self.detect(output, output_id=f"output_{i}", context=context)
            for i, output in enumerate(outputs)
        ]

    def _score_confidence(self, output: str, flags: list[str]) -> float:
        """Estimate output confidence from linguistic uncertainty patterns.

        Args:
            output: Model output text.
            flags: Mutable list to append detected flag descriptions.

        Returns:
            Confidence score in [0, 1] (higher is better).
        """
        hit_count = sum(
            1 for pattern in self._uncertainty_re if pattern.search(output)
        )
        contradiction_count = sum(
            1 for pattern in self._contradiction_re if pattern.search(output)
        )

        total_hits = hit_count + contradiction_count
        if total_hits > 0:
            flags.append(f"uncertainty_patterns:{total_hits}")

        # Score decays with number of uncertainty matches
        score = max(0.0, 1.0 - 0.15 * total_hits)
        return float(score)

    def _score_consistency(
        self,
        output: str,
        sampled_outputs: list[str] | None,
        flags: list[str],
    ) -> float:
        """Measure consistency of an output against sampled alternatives.

        Uses normalised word-level Jaccard similarity.

        Args:
            output: Primary model output.
            sampled_outputs: Alternative sampled outputs (optional).
            flags: Mutable list to append flag descriptions.

        Returns:
            Consistency score in [0, 1].
        """
        if not sampled_outputs:
            return 1.0  # Cannot assess — default to passing

        output_words = set(output.lower().split())
        similarities: list[float] = []

        for alt in sampled_outputs:
            alt_words = set(alt.lower().split())
            intersection = len(output_words & alt_words)
            union = len(output_words | alt_words)
            similarities.append(intersection / union if union > 0 else 0.0)

        mean_sim = float(np.mean(similarities))
        if mean_sim < self._consistency_threshold:
            flags.append(f"low_consistency:{mean_sim:.2f}")

        return mean_sim

    def _score_factual(
        self,
        output: str,
        context: str | None,
        flags: list[str],
    ) -> float:
        """Measure factual overlap between output and provided context.

        Args:
            output: Model output text.
            context: Ground-truth or retrieval context.
            flags: Mutable list to append flag descriptions.

        Returns:
            Factual grounding score in [0, 1].
        """
        if not context:
            return 1.0  # Cannot assess — default to passing

        output_words = set(output.lower().split())
        context_words = set(context.lower().split())

        if not output_words:
            return 0.0

        overlap = len(output_words & context_words) / len(output_words)
        if overlap < self._factual_threshold:
            flags.append(f"low_factual_overlap:{overlap:.2f}")

        return float(overlap)

    def _compute_risk(
        self,
        confidence: float,
        consistency: float,
        factual: float,
    ) -> str:
        """Derive a categorical risk level from the three sub-scores.

        Args:
            confidence: Confidence score.
            consistency: Consistency score.
            factual: Factual score.

        Returns:
            ``"low"``, ``"medium"``, or ``"high"``.
        """
        avg = (confidence + consistency + factual) / 3.0
        if avg >= 0.75:
            return "low"
        if avg >= 0.5:
            return "medium"
        return "high"
