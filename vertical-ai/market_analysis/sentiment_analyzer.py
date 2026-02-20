"""Sentiment analysis: news and social-media text scoring.

Provides :class:`SentimentAnalyzer` which uses a lexicon-based approach with
weighted averaging to produce a sentiment score in [-1, 1].
"""

from __future__ import annotations

import re
from typing import Any

import numpy as np
from loguru import logger


# ---------------------------------------------------------------------------
# Minimal built-in lexicon (finance-domain keywords)
# ---------------------------------------------------------------------------

_POSITIVE_WORDS: frozenset[str] = frozenset(
    [
        "bullish", "rally", "surge", "gain", "profit", "growth", "beat",
        "outperform", "upgrade", "strong", "record", "breakthrough", "positive",
        "optimistic", "recovery", "boom", "buy", "upside", "expansion", "rise",
        "soar", "high", "robust", "confident", "dividend", "upbeat", "exceed",
        "accelerate", "improve", "advance", "momentum",
    ]
)

_NEGATIVE_WORDS: frozenset[str] = frozenset(
    [
        "bearish", "crash", "plunge", "loss", "decline", "miss", "downgrade",
        "weak", "concern", "risk", "fear", "sell", "cut", "drop", "fall",
        "slump", "debt", "default", "recession", "inflation", "warning",
        "disappointing", "underperform", "volatile", "uncertainty", "downturn",
        "restructure", "layoff", "bankruptcy", "lawsuit", "fraud",
    ]
)

_NEGATION_WORDS: frozenset[str] = frozenset(
    ["not", "no", "never", "neither", "nor", "hardly", "barely", "scarcely"]
)

_INTENSIFIER_WORDS: dict[str, float] = {
    "very": 1.5,
    "extremely": 2.0,
    "significantly": 1.5,
    "slightly": 0.5,
    "somewhat": 0.7,
    "highly": 1.5,
    "major": 1.5,
    "minor": 0.5,
}


class SentimentAnalyzer:
    """Lexicon-based sentiment scorer for financial text.

    Scores individual tokens using a finance-domain lexicon, applies negation
    and intensifier modifiers, then aggregates across multiple documents using
    a configurable weighting scheme.

    Attributes:
        positive_words: Set of positive sentiment words.
        negative_words: Set of negative sentiment words.
        negation_window: Number of tokens after a negation word where
            sentiment is flipped.
        default_weights: Weighting strategy (``"uniform"`` or ``"recency"``).
    """

    def __init__(
        self,
        positive_words: frozenset[str] | None = None,
        negative_words: frozenset[str] | None = None,
        negation_window: int = 3,
        default_weights: str = "uniform",
    ) -> None:
        """Initialise SentimentAnalyzer.

        Args:
            positive_words: Override default positive lexicon.
            negative_words: Override default negative lexicon.
            negation_window: Token window after a negation word where polarity
                is flipped.
            default_weights: ``"uniform"`` (equal weight per document) or
                ``"recency"`` (more-recent docs weighted higher).
        """
        self.positive_words = positive_words or _POSITIVE_WORDS
        self.negative_words = negative_words or _NEGATIVE_WORDS
        self.negation_window = negation_window
        self.default_weights = default_weights

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """Lower-case and split text into word tokens.

        Args:
            text: Raw input string.

        Returns:
            List of lower-cased word tokens.
        """
        return re.findall(r"[a-z]+", text.lower())

    def _score_text(self, text: str) -> float:
        """Score a single text document.

        Applies negation window and intensifier multipliers.

        Args:
            text: Raw text string.

        Returns:
            Raw sentiment score (can exceed [-1, 1] before normalisation).
        """
        tokens = self._tokenize(text)
        score = 0.0
        negation_count = 0
        intensifier = 1.0

        for token in tokens:
            if token in _NEGATION_WORDS:
                negation_count = self.negation_window
                continue

            if token in _INTENSIFIER_WORDS:
                intensifier = _INTENSIFIER_WORDS[token]
                continue

            polarity = 0.0
            if token in self.positive_words:
                polarity = 1.0
            elif token in self.negative_words:
                polarity = -1.0

            if polarity != 0.0:
                if negation_count > 0:
                    polarity *= -1.0
                score += polarity * intensifier

            if negation_count > 0:
                negation_count -= 1
            intensifier = 1.0  # reset after each scored word

        return score

    @staticmethod
    def _normalise(score: float, n_tokens: int) -> float:
        """Normalise raw score to [-1, 1].

        Args:
            score: Accumulated raw score.
            n_tokens: Number of tokens in the document.

        Returns:
            Score clamped to [-1, 1].
        """
        if n_tokens == 0:
            return 0.0
        normalised = score / n_tokens
        return float(np.clip(normalised, -1.0, 1.0))

    def _build_weights(self, n: int, strategy: str) -> np.ndarray:
        """Build a weight vector for *n* documents.

        Args:
            n: Number of documents.
            strategy: ``"uniform"`` or ``"recency"``.

        Returns:
            Normalised weight array of shape ``(n,)``.
        """
        if strategy == "recency":
            weights = np.arange(1, n + 1, dtype=float)
        else:
            weights = np.ones(n, dtype=float)
        return weights / weights.sum()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def analyze_sentiment(
        self,
        texts: list[str],
        weights: list[float] | None = None,
    ) -> dict[str, Any]:
        """Compute aggregate sentiment score across a list of text documents.

        Args:
            texts: List of text strings (news headlines, tweets, etc.).
            weights: Optional per-document weights.  Must sum to 1 if provided.
                If ``None``, uses :attr:`default_weights` strategy.

        Returns:
            Dict with keys:

            * ``score`` – aggregate sentiment in [-1, 1]
            * ``individual_scores`` – per-document scores
            * ``label`` – ``"positive"``, ``"negative"``, or ``"neutral"``

        Raises:
            ValueError: If *texts* is empty or *weights* length mismatches.
        """
        if not texts:
            raise ValueError("texts must be a non-empty list of strings.")

        individual: list[float] = []
        for text in texts:
            tokens = self._tokenize(text)
            raw = self._score_text(text)
            individual.append(self._normalise(raw, max(len(tokens), 1)))

        if weights is not None:
            if len(weights) != len(texts):
                raise ValueError(
                    f"weights length ({len(weights)}) != texts length ({len(texts)})"
                )
            w = np.asarray(weights, dtype=float)
            w = w / w.sum()
        else:
            w = self._build_weights(len(texts), self.default_weights)

        aggregate = float(np.dot(w, individual))

        if aggregate > 0.05:
            label = "positive"
        elif aggregate < -0.05:
            label = "negative"
        else:
            label = "neutral"

        logger.debug(f"Sentiment analysis: {len(texts)} docs → score={aggregate:.4f} ({label})")
        return {
            "score": aggregate,
            "individual_scores": individual,
            "label": label,
        }
