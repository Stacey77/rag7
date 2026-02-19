"""Detect emotional states from text using keyword lexicons."""

import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict
from statistics import mean

logger = logging.getLogger(__name__)

EMOTION_LEXICONS: Dict[str, List[str]] = {
    "joy": ["happy", "joy", "delighted", "glad", "pleased", "wonderful", "fantastic",
            "great", "love", "excited", "cheerful", "thrilled", "elated", "bliss"],
    "sadness": ["sad", "unhappy", "depressed", "miserable", "heartbroken", "grief",
                "sorrow", "cry", "tears", "lonely", "hopeless", "disappointed", "down"],
    "anger": ["angry", "furious", "rage", "mad", "outraged", "livid", "hate",
              "annoyed", "hostile", "bitter", "resentful", "frustrated", "infuriated"],
    "fear": ["afraid", "scared", "terrified", "anxious", "worried", "panic",
             "nervous", "dread", "frightened", "horrified", "phobia", "uneasy"],
    "frustration": ["frustrated", "stuck", "confused", "lost", "cant", "impossible",
                    "useless", "broken", "failed", "wrong", "error", "problem", "issue"],
    "excitement": ["excited", "amazing", "awesome", "incredible", "wow", "yes",
                   "finally", "cant wait", "thrilled", "pumped", "stoked", "brilliant"],
}

VALENCE_MAP = {"joy": 0.9, "sadness": -0.8, "anger": -0.7,
               "fear": -0.6, "frustration": -0.5, "excitement": 0.8}
AROUSAL_MAP = {"joy": 0.6, "sadness": 0.2, "anger": 0.9,
               "fear": 0.8, "frustration": 0.7, "excitement": 0.9}
DISTRESS_EMOTIONS = {"sadness", "fear", "anger", "frustration"}


@dataclass
class EmotionalState:
    """Represents a detected emotional state."""
    valence: float        # -1 (negative) to 1 (positive)
    arousal: float        # 0 (calm) to 1 (activated)
    emotion: str
    intensity: float      # 0 to 1


@dataclass
class EmotionTrigger:
    """Represents a trigger phrase that evoked an emotion."""
    phrase: str
    emotion: str
    position: int


class EmpathyDetector:
    """Detect emotional states and triggers from text using lexicon matching."""

    def __init__(self) -> None:
        self._compiled = {
            emotion: re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.IGNORECASE)
            for emotion, words in EMOTION_LEXICONS.items()
        }
        logger.info("EmpathyDetector initialised with %d emotion categories.", len(EMOTION_LEXICONS))

    def _score_emotions(self, text: str) -> Dict[str, float]:
        """Return a normalised hit-count score per emotion."""
        word_count = max(len(text.split()), 1)
        scores: Dict[str, float] = {}
        for emotion, pattern in self._compiled.items():
            hits = pattern.findall(text)
            scores[emotion] = len(hits) / word_count
        return scores

    def detect(self, text: str) -> EmotionalState:
        """Detect the dominant emotional state in *text*."""
        scores = self._score_emotions(text)
        dominant = max(scores, key=lambda e: scores[e])
        intensity = min(scores[dominant] * 10, 1.0)

        if all(v == 0 for v in scores.values()):
            return EmotionalState(valence=0.0, arousal=0.3, emotion="neutral", intensity=0.1)

        valence = VALENCE_MAP.get(dominant, 0.0) * intensity
        arousal = AROUSAL_MAP.get(dominant, 0.5) * intensity
        logger.debug("Detected emotion=%s intensity=%.2f", dominant, intensity)
        return EmotionalState(valence=round(valence, 3), arousal=round(arousal, 3),
                              emotion=dominant, intensity=round(intensity, 3))

    def detect_triggers(self, text: str) -> List[EmotionTrigger]:
        """Return individual trigger phrases found in *text*."""
        triggers: List[EmotionTrigger] = []
        for emotion, pattern in self._compiled.items():
            for match in pattern.finditer(text):
                triggers.append(EmotionTrigger(phrase=match.group(),
                                               emotion=emotion,
                                               position=match.start()))
        triggers.sort(key=lambda t: t.position)
        return triggers

    def is_in_distress(self, text: str) -> bool:
        """Return True when the text signals significant emotional distress."""
        state = self.detect(text)
        if state.emotion in DISTRESS_EMOTIONS and state.intensity >= 0.3:
            return True
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        exclamations = text.count("!")
        return caps_ratio > 0.4 or exclamations >= 3

    def emotional_trajectory(self, texts: List[str]) -> List[EmotionalState]:
        """Compute an emotional state for each text in chronological order."""
        trajectory = [self.detect(t) for t in texts]
        logger.info("Computed trajectory over %d texts.", len(trajectory))
        return trajectory
