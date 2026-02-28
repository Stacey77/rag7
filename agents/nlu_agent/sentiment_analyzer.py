"""Sentiment analysis and emotional tone detection."""
from __future__ import annotations

import logging
import re
import statistics
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Sentiment lexicons (valence scores: -1 strongly negative, +1 strongly positive)
_POSITIVE_WORDS: Dict[str, float] = {
    "great": 0.8, "excellent": 0.9, "good": 0.6, "wonderful": 0.9, "amazing": 0.85,
    "fantastic": 0.88, "love": 0.8, "happy": 0.75, "success": 0.7, "perfect": 0.9,
    "outstanding": 0.88, "brilliant": 0.85, "helpful": 0.65, "easy": 0.5, "fast": 0.55,
    "reliable": 0.65, "stable": 0.6, "efficient": 0.65, "improved": 0.6, "resolved": 0.7,
    "fixed": 0.65, "works": 0.55, "working": 0.55, "thanks": 0.5, "thank": 0.5,
}

_NEGATIVE_WORDS: Dict[str, float] = {
    "bad": -0.7, "terrible": -0.9, "awful": -0.88, "horrible": -0.9, "hate": -0.85,
    "failure": -0.8, "error": -0.65, "broken": -0.75, "slow": -0.5, "unreliable": -0.7,
    "crash": -0.8, "problem": -0.6, "issue": -0.5, "bug": -0.6, "fail": -0.7,
    "failed": -0.75, "wrong": -0.65, "difficult": -0.45, "confusing": -0.55, "frustrated": -0.7,
    "annoying": -0.65, "useless": -0.8, "waste": -0.7, "stuck": -0.55, "broken": -0.75,
}

_NEGATORS = {"not", "no", "never", "neither", "nor", "without", "don't", "doesn't",
             "didn't", "won't", "wouldn't", "can't", "cannot"}

_INTENSIFIERS: Dict[str, float] = {
    "very": 1.3, "extremely": 1.5, "incredibly": 1.4, "absolutely": 1.4,
    "quite": 1.1, "rather": 1.1, "somewhat": 0.8, "slightly": 0.7, "barely": 0.6,
    "really": 1.25, "super": 1.3, "highly": 1.25,
}

# Emotion categories mapped to seed words
_EMOTION_SEEDS: Dict[str, List[str]] = {
    "joy": ["happy", "joy", "delighted", "pleased", "excited", "great", "wonderful"],
    "anger": ["angry", "furious", "outraged", "mad", "hate", "annoying", "rage"],
    "fear": ["afraid", "scared", "worried", "nervous", "anxious", "panic", "dread"],
    "sadness": ["sad", "unhappy", "disappointed", "miserable", "terrible", "awful"],
    "surprise": ["surprised", "shocked", "unexpected", "amazing", "wow", "suddenly"],
    "disgust": ["disgusting", "horrible", "awful", "nasty", "repulsive", "terrible"],
    "trust": ["trust", "reliable", "secure", "confident", "honest", "consistent"],
    "anticipation": ["hope", "expect", "forward", "plan", "soon", "future", "upcoming"],
}


@dataclass
class SentimentScore:
    """Numerical sentiment metrics."""
    polarity: float = 0.0       # -1 to +1
    subjectivity: float = 0.0   # 0 (objective) to 1 (subjective)
    intensity: float = 0.0      # 0 to 1


@dataclass
class EmotionScores:
    """Per-emotion confidence scores."""
    joy: float = 0.0
    anger: float = 0.0
    fear: float = 0.0
    sadness: float = 0.0
    surprise: float = 0.0
    disgust: float = 0.0
    trust: float = 0.0
    anticipation: float = 0.0

    def dominant(self) -> Tuple[str, float]:
        scores = vars(self)
        best = max(scores, key=lambda k: scores[k])
        return best, scores[best]


@dataclass
class SentimentResult:
    """Full result of sentiment analysis."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    label: str = "neutral"           # "positive" | "negative" | "neutral" | "mixed"
    scores: SentimentScore = field(default_factory=SentimentScore)
    emotions: EmotionScores = field(default_factory=EmotionScores)
    dominant_emotion: str = ""
    keyword_hits: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+'\w+|\b\w+\b", text.lower())


class LexiconSentimentAnalyzer:
    """Lexicon + rule-based sentiment scorer."""

    def analyze(self, text: str) -> Tuple[float, float, List[str]]:
        """Returns (polarity, subjectivity, keyword_hits)."""
        tokens = _tokenize(text)
        total_score = 0.0
        sentiment_tokens = 0
        keyword_hits: List[str] = []
        intensity_multiplier = 1.0

        for i, token in enumerate(tokens):
            if token in _NEGATORS:
                intensity_multiplier = -0.9
                continue
            if token in _INTENSIFIERS:
                intensity_multiplier *= _INTENSIFIERS[token]
                continue

            score: Optional[float] = None
            if token in _POSITIVE_WORDS:
                score = _POSITIVE_WORDS[token]
                keyword_hits.append(f"+{token}")
            elif token in _NEGATIVE_WORDS:
                score = _NEGATIVE_WORDS[token]
                keyword_hits.append(f"-{token}")

            if score is not None:
                total_score += score * intensity_multiplier
                sentiment_tokens += 1
                intensity_multiplier = 1.0

        polarity = max(-1.0, min(1.0, total_score / max(sentiment_tokens, 1)))
        subjectivity = min(1.0, sentiment_tokens / max(len(tokens), 1) * 3)
        return polarity, subjectivity, keyword_hits


class EmotionDetector:
    """Detects fine-grained emotions using seed word proximity."""

    def detect(self, text: str) -> EmotionScores:
        tokens = set(_tokenize(text))
        scores: Dict[str, float] = {}
        for emotion, seeds in _EMOTION_SEEDS.items():
            hits = sum(1 for seed in seeds if seed in tokens)
            scores[emotion] = min(1.0, hits / max(len(seeds), 1) * 4)
        return EmotionScores(**scores)


class SentimentAnalyzer:
    """
    Full sentiment analysis pipeline combining lexicon scoring,
    negation/intensifier handling, and emotion detection.
    """

    def __init__(self, neutral_threshold: float = 0.15) -> None:
        self.neutral_threshold = neutral_threshold
        self._lexicon = LexiconSentimentAnalyzer()
        self._emotion_detector = EmotionDetector()
        logger.info("SentimentAnalyzer initialized")

    def analyze(self, text: str) -> SentimentResult:
        polarity, subjectivity, keyword_hits = self._lexicon.analyze(text)
        emotions = self._emotion_detector.detect(text)
        dominant_emotion, _ = emotions.dominant()

        label = self._polarity_label(polarity, subjectivity)
        intensity = min(1.0, abs(polarity) + subjectivity * 0.3)

        result = SentimentResult(
            text=text,
            label=label,
            scores=SentimentScore(polarity=polarity, subjectivity=subjectivity, intensity=intensity),
            emotions=emotions,
            dominant_emotion=dominant_emotion,
            keyword_hits=keyword_hits,
        )
        logger.debug("Sentiment: '%s' -> %s (%.2f)", text[:50], label, polarity)
        return result

    def _polarity_label(self, polarity: float, subjectivity: float) -> str:
        if abs(polarity) < self.neutral_threshold:
            return "neutral"
        if polarity > 0 and subjectivity < 0.2:
            return "mixed"  # high polarity but objective
        return "positive" if polarity > 0 else "negative"

    def batch_analyze(self, texts: List[str]) -> List[SentimentResult]:
        return [self.analyze(t) for t in texts]

    def aggregate(self, results: List[SentimentResult]) -> Dict[str, Any]:
        if not results:
            return {}
        polarities = [r.scores.polarity for r in results]
        labels = [r.label for r in results]
        from collections import Counter
        label_counts = Counter(labels)
        return {
            "mean_polarity": statistics.mean(polarities),
            "std_polarity": statistics.stdev(polarities) if len(polarities) > 1 else 0.0,
            "label_distribution": dict(label_counts),
            "dominant_label": label_counts.most_common(1)[0][0],
            "sample_count": len(results),
        }

    def explain(self, result: SentimentResult) -> str:
        lines = [
            f"Text: {result.text[:80]}",
            f"Sentiment: {result.label} (polarity={result.scores.polarity:+.2f})",
            f"Subjectivity: {result.scores.subjectivity:.1%}",
            f"Dominant emotion: {result.dominant_emotion}",
            f"Key indicators: {', '.join(result.keyword_hits[:5])}",
        ]
        return "\n".join(lines)
