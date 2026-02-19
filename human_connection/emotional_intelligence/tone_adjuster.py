"""Adapt communication tone for different contexts and emotional states."""

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

INFORMAL_TO_FORMAL = {
    r"\bdon't\b": "do not", r"\bcan't\b": "cannot", r"\bwon't\b": "will not",
    r"\bisn't\b": "is not", r"\baren't\b": "are not", r"\bwasn't\b": "was not",
    r"\bweren't\b": "were not", r"\bhadn't\b": "had not", r"\bhasn't\b": "has not",
    r"\bhaven't\b": "have not", r"\bdidn't\b": "did not", r"\bdoesn't\b": "does not",
    r"\bI'm\b": "I am", r"\byou're\b": "you are", r"\bthey're\b": "they are",
    r"\bwe're\b": "we are", r"\bhe's\b": "he is", r"\bshe's\b": "she is",
    r"\bit's\b": "it is", r"\bthat's\b": "that is",
    r"\bgonna\b": "going to", r"\bwanna\b": "want to", r"\bgotta\b": "have to",
    r"\bkinda\b": "somewhat", r"\bsorta\b": "somewhat",
}

COLD_TO_WARM = {
    r"^(The result is)": "Great news — the result is",
    r"^(Error:)": "Something went wrong:",
    r"^(Note:)": "Just so you know:",
    r"\buser\b": "you", r"\bthe user\b": "you",
    r"\bOne must\b": "You can",
}

HARSH_TO_GENTLE = {
    r"\bfailed\b": "did not succeed yet",
    r"\bwrong\b": "not quite right",
    r"\bstupid\b": "not the best approach",
    r"\bimpossible\b": "quite challenging",
    r"\bmust\b": "might want to",
    r"\byou need to\b": "it could help to",
    r"\byou have to\b": "you might consider",
}

EMOTION_TONE_MAP = {
    "sadness": {"opener": "I'm really sorry to hear that. ", "closer": " I'm here if you need more support."},
    "fear": {"opener": "That sounds really stressful. ", "closer": " We'll work through this together."},
    "anger": {"opener": "I completely understand your frustration. ", "closer": " Let's fix this right away."},
    "frustration": {"opener": "That's genuinely annoying — let's sort it out. ", "closer": " You're almost there."},
    "joy": {"opener": "That's wonderful! ", "closer": " Keep up the great work!"},
    "excitement": {"opener": "Love the energy! ", "closer": " Let's make it happen!"},
    "neutral": {"opener": "", "closer": ""},
}


@dataclass
class ToneProfile:
    """Describes the desired tone of a response."""
    formality: float = 0.5    # 0 = casual, 1 = very formal
    warmth: float = 0.5       # 0 = cold, 1 = very warm
    directness: float = 0.5   # 0 = indirect, 1 = very direct
    empathy_level: float = 0.5  # 0 = neutral, 1 = highly empathetic


class ToneAdjuster:
    """Adjust the tone of text to match a target ToneProfile or emotional context."""

    def __init__(self) -> None:
        logger.info("ToneAdjuster initialised.")

    @staticmethod
    def _apply_replacements(text: str, mapping: dict) -> str:
        for pattern, replacement in mapping.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def adjust(self, text: str, target_profile: ToneProfile) -> str:
        """Apply tone transformations according to *target_profile*."""
        result = text
        if target_profile.formality > 0.6:
            result = self._apply_replacements(result, INFORMAL_TO_FORMAL)
        if target_profile.warmth > 0.6:
            result = self._apply_replacements(result, COLD_TO_WARM)
        if target_profile.empathy_level > 0.6:
            result = self.make_gentler(result)
        if target_profile.directness < 0.3 and not result.startswith("Perhaps"):
            result = "Perhaps " + result[0].lower() + result[1:]
        logger.debug("Tone adjusted: formality=%.1f warmth=%.1f", target_profile.formality, target_profile.warmth)
        return result

    def make_warmer(self, text: str) -> str:
        """Add warmth cues to *text*."""
        result = self._apply_replacements(text, COLD_TO_WARM)
        if not any(result.startswith(p) for p in ("That", "I", "Great", "Love")):
            result = "I'd be happy to help. " + result
        return result

    def make_more_formal(self, text: str) -> str:
        """Convert contractions and colloquialisms to formal equivalents."""
        return self._apply_replacements(text, INFORMAL_TO_FORMAL)

    def make_gentler(self, text: str) -> str:
        """Soften potentially harsh or blunt language."""
        return self._apply_replacements(text, HARSH_TO_GENTLE)

    def calibrate_to_emotion(self, text: str, emotion: str) -> str:
        """Wrap *text* with an emotion-appropriate opener and closer."""
        tone = EMOTION_TONE_MAP.get(emotion, EMOTION_TONE_MAP["neutral"])
        result = tone["opener"] + text.strip() + tone["closer"]
        logger.debug("Calibrated tone for emotion=%s", emotion)
        return result
