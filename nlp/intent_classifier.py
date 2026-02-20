"""
Intent classifier module for the rag7 NLP system.

Classifies operator commands into predefined intent categories using
keyword matching with confidence scoring.
"""

import logging
from typing import Dict, List


class IntentClassifier:
    """Keyword-based intent classifier for robot commands.

    Classifies text inputs into one of the predefined intents using
    a weighted keyword matching approach.

    Class attributes:
        INTENTS: List of supported intent label strings.
    """

    INTENTS: List[str] = [
        "navigate",
        "grasp",
        "place",
        "inspect",
        "stop",
        "query",
        "unknown",
    ]

    # Mapping from intent to trigger keywords with weights
    _KEYWORD_MAP: Dict[str, Dict[str, float]] = {
        "navigate": {
            "go": 1.0, "move": 1.0, "navigate": 1.5, "drive": 1.0,
            "travel": 0.8, "head": 0.7, "proceed": 0.7, "reach": 0.7,
        },
        "grasp": {
            "grasp": 1.5, "pick": 1.0, "grab": 1.0, "take": 0.8,
            "hold": 0.7, "lift": 0.8, "collect": 0.7, "retrieve": 0.8,
        },
        "place": {
            "place": 1.5, "put": 1.0, "drop": 0.8, "set": 0.7,
            "release": 0.8, "deposit": 0.8, "leave": 0.6,
        },
        "inspect": {
            "inspect": 1.5, "look": 0.7, "examine": 1.0, "scan": 0.9,
            "check": 0.8, "observe": 0.9, "analyse": 0.8, "survey": 0.8,
        },
        "stop": {
            "stop": 1.5, "halt": 1.5, "freeze": 1.0, "pause": 0.9,
            "emergency": 1.0, "abort": 1.0, "cancel": 0.7,
        },
        "query": {
            "what": 0.8, "where": 0.8, "how": 0.7, "status": 1.0,
            "tell": 0.6, "show": 0.6, "report": 0.9, "describe": 0.7,
        },
    }

    def __init__(self) -> None:
        """Initialize the intent classifier."""
        self._logger = logging.getLogger("rag7.nlp.intent")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, text: str) -> str:
        """Classify the primary intent of an input text.

        Args:
            text: Natural language input string.

        Returns:
            Intent label string from :attr:`INTENTS`.
        """
        scores = self._score_all(text)
        if not scores:
            return "unknown"
        best_intent = max(scores, key=scores.get)  # type: ignore[arg-type]
        if scores[best_intent] == 0.0:
            return "unknown"
        return best_intent

    def get_confidence(self, text: str, intent: str) -> float:
        """Return the classifier confidence for a specific intent.

        Args:
            text: Natural language input string.
            intent: Intent label to score.

        Returns:
            Confidence value in the range [0, 1].
        """
        if intent not in self._KEYWORD_MAP:
            return 0.0

        scores = self._score_all(text)
        total = sum(scores.values())
        if total == 0.0:
            return 0.0
        return min(1.0, scores.get(intent, 0.0) / total)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _score_all(self, text: str) -> Dict[str, float]:
        """Compute weighted keyword scores for all intents.

        Args:
            text: Input text to score.

        Returns:
            Dict mapping each intent to its raw keyword score.
        """
        words = text.lower().split()
        scores: Dict[str, float] = {intent: 0.0 for intent in self._KEYWORD_MAP}

        for intent, keywords in self._KEYWORD_MAP.items():
            for word in words:
                clean = word.strip(".,!?;:")
                if clean in keywords:
                    scores[intent] += keywords[clean]

        return scores
