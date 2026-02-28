"""Adapt AI responses to individual user communication styles."""

import logging
import re
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger(__name__)

FILLER_WORDS = {"very", "really", "quite", "rather", "just", "actually", "basically",
                "literally", "definitely", "certainly", "absolutely", "simply"}

TECHNICAL_SYNONYMS: Dict[str, Dict[str, str]] = {
    # term -> {novice replacement, expert retention}
    "execute": {"novice": "run", "expert": "execute"},
    "implement": {"novice": "build", "expert": "implement"},
    "instantiate": {"novice": "create", "expert": "instantiate"},
    "iterate": {"novice": "loop through", "expert": "iterate"},
    "concatenate": {"novice": "join together", "expert": "concatenate"},
    "deprecated": {"novice": "no longer recommended", "expert": "deprecated"},
    "parameter": {"novice": "input value", "expert": "parameter"},
    "asynchronous": {"novice": "non-blocking", "expert": "asynchronous"},
    "polymorphism": {"novice": "flexible behaviour", "expert": "polymorphism"},
}


@dataclass
class CommunicationStyle:
    """Describes a user's preferred communication style."""
    verbosity: str = "medium"       # "brief", "medium", "verbose"
    technicality: str = "medium"    # "simple", "medium", "technical"
    formality: str = "neutral"      # "casual", "neutral", "formal"
    avg_message_length: float = 50.0
    common_words: List[str] = field(default_factory=list)


class StyleAdapter:
    """Learn from user interactions and adapt responses accordingly."""

    def __init__(self) -> None:
        self._styles: Dict[str, CommunicationStyle] = {}
        self._word_counters: Dict[str, Counter] = defaultdict(Counter)
        logger.info("StyleAdapter initialised.")

    def learn_style(self, user_id: str, text: str) -> None:
        """Update style model for *user_id* based on *text* sample."""
        words = text.lower().split()
        self._word_counters[user_id].update(words)

        style = self._styles.setdefault(user_id, CommunicationStyle())
        word_count = len(words)

        # Adjust avg message length with exponential moving average
        style.avg_message_length = 0.8 * style.avg_message_length + 0.2 * word_count

        # Verbosity
        if style.avg_message_length > 80:
            style.verbosity = "verbose"
        elif style.avg_message_length < 25:
            style.verbosity = "brief"
        else:
            style.verbosity = "medium"

        # Technicality: count technical terms
        tech_count = sum(1 for w in words if w in TECHNICAL_SYNONYMS)
        ratio = tech_count / max(word_count, 1)
        style.technicality = "technical" if ratio > 0.05 else ("simple" if ratio < 0.01 else "medium")

        # Formality: contractions suggest casual
        contractions = len(re.findall(r"\b\w+n't\b|\bI'm\b|\byou're\b", text, re.IGNORECASE))
        style.formality = "casual" if contractions >= 2 else "neutral"

        # Top common words (excluding stop words)
        stop = {"the", "a", "an", "is", "it", "in", "on", "at", "of", "and", "to", "i"}
        style.common_words = [w for w, _ in self._word_counters[user_id].most_common(10) if w not in stop]
        logger.debug("Style updated for user=%s verbosity=%s technicality=%s",
                     user_id, style.verbosity, style.technicality)

    def adapt_response(self, response: str, user_id: str) -> str:
        """Apply all style adaptations to *response* for *user_id*."""
        style = self._styles.get(user_id, CommunicationStyle())
        result = self.adjust_verbosity(response, style.verbosity)
        result = self.adjust_technicality(result, style.technicality)
        result = self.match_vocabulary(result, user_id)
        return result

    def adjust_verbosity(self, text: str, level: str) -> str:
        """Expand or condense text based on desired verbosity *level*."""
        if level == "brief":
            # Remove filler words and shorten
            words = [w for w in text.split() if w.lower() not in FILLER_WORDS]
            sentences = re.split(r"(?<=[.!?])\s+", " ".join(words))
            return " ".join(sentences[:3])  # keep first 3 sentences max
        if level == "verbose":
            # Add elaboration markers
            text = text.replace(". ", ".  Additionally, ")
            return text.replace(".  Additionally, ", ". ", text.count(". ") - 1)
        return text

    def adjust_technicality(self, text: str, level: str) -> str:
        """Swap technical terms based on desired *level*."""
        for term, mapping in TECHNICAL_SYNONYMS.items():
            target = mapping.get("novice" if level == "simple" else "expert", term)
            text = re.sub(r"\b" + re.escape(term) + r"\b", target, text, flags=re.IGNORECASE)
        return text

    def match_vocabulary(self, text: str, user_id: str) -> str:
        """Minor vocabulary alignment using the user's frequent terms (placeholder)."""
        # This is intentionally lightweight — deep rephrasing would need an LLM.
        return text

    def get_style(self, user_id: str) -> CommunicationStyle:
        """Return the current CommunicationStyle for *user_id*."""
        return self._styles.get(user_id, CommunicationStyle())
