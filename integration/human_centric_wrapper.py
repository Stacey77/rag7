"""Wrap AI responses with empathy, clarity, and personalisation layers."""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

CLARITY_REPLACEMENTS = {
    r"\bin order to\b": "to",
    r"\bdue to the fact that\b": "because",
    r"\bat this point in time\b": "now",
    r"\bin the event that\b": "if",
    r"\bfor the purpose of\b": "to",
    r"\bit is important to note that\b": "note that",
    r"\bplease be advised that\b": "",
    r"\bkindly note\b": "note",
}

EMPATHY_OPENERS: Dict[str, str] = {
    "sadness": "I'm really sorry you're going through this. ",
    "anger": "I completely understand your frustration. ",
    "fear": "I can see this feels overwhelming — let's take it step by step. ",
    "frustration": "I hear you — that's genuinely frustrating. ",
    "joy": "That's wonderful to hear! ",
    "excitement": "Love the enthusiasm! ",
    "neutral": "Thanks for reaching out. ",
}

QUALITY_CHECKS = {
    "length_ok": lambda t: 20 <= len(t.split()) <= 500,
    "no_jargon_overload": lambda t: len(re.findall(r"\b\w{15,}\b", t)) < 5,
    "ends_with_punctuation": lambda t: bool(re.search(r"[.!?]$", t.strip())),
    "no_repeated_sentences": lambda t: len(set(re.split(r"[.!?]+", t))) > 1,
}


@dataclass
class HumanCentricRequest:
    """An inbound request to the human-centric wrapper."""
    raw_response: str
    user_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: __import__("uuid").uuid4().hex)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class HumanCentricResponse:
    """An enriched, empathy-layered response ready for delivery."""
    original: str
    enhanced: str
    user_id: str
    quality_scores: Dict[str, bool] = field(default_factory=dict)
    empathy_added: bool = False
    clarity_improved: bool = False
    personalised: bool = False
    produced_at: datetime = field(default_factory=datetime.utcnow)


class HumanCentricWrapper:
    """Add empathy, clarity, and personalisation to raw AI-generated responses."""

    def __init__(self) -> None:
        self._user_names: Dict[str, str] = {}  # user_id -> display name
        self._clarity_patterns = [
            (re.compile(p, re.IGNORECASE), r)
            for p, r in CLARITY_REPLACEMENTS.items()
        ]
        logger.info("HumanCentricWrapper initialised.")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def wrap_response(self, raw_response: str, user_id: str,
                      context: Optional[Dict[str, Any]] = None) -> HumanCentricResponse:
        """Apply the full enhancement pipeline to *raw_response*."""
        context = context or {}
        text = raw_response

        clarity_before = text
        text = self.ensure_clarity(text)
        clarity_improved = text != clarity_before

        emotion = context.get("detected_emotion", "neutral")
        empathy_before = text
        text = self.add_empathy_layer(text, emotion)
        empathy_added = text != empathy_before

        personalised_before = text
        text = self.personalize(text, user_id)
        personalised = text != personalised_before

        quality = self.assess_response_quality(text)
        logger.debug("Wrapped response for user=%s clarity=%s empathy=%s",
                     user_id, clarity_improved, empathy_added)
        return HumanCentricResponse(
            original=raw_response, enhanced=text, user_id=user_id,
            quality_scores=quality, empathy_added=empathy_added,
            clarity_improved=clarity_improved, personalised=personalised,
        )

    def assess_response_quality(self, response: str) -> Dict[str, bool]:
        """Run all quality checks and return a dict of {check_name: passed}."""
        return {name: check(response) for name, check in QUALITY_CHECKS.items()}

    def add_empathy_layer(self, text: str, emotion: str) -> str:
        """Prepend an emotion-appropriate opener to *text*."""
        opener = EMPATHY_OPENERS.get(emotion, EMPATHY_OPENERS["neutral"])
        if not opener:
            return text
        # Avoid double empathy openers
        if any(text.startswith(o.strip()) for o in EMPATHY_OPENERS.values() if o.strip()):
            return text
        return opener + text

    def ensure_clarity(self, text: str) -> str:
        """Remove filler phrases and simplify wordy constructions."""
        result = text
        for pattern, replacement in self._clarity_patterns:
            result = pattern.sub(replacement, result)
        # Collapse multiple spaces left by empty replacements
        result = re.sub(r" {2,}", " ", result).strip()
        # Capitalise first letter
        if result and result[0].islower():
            result = result[0].upper() + result[1:]
        return result

    def personalize(self, text: str, user_id: str) -> str:
        """Insert the user's display name if known."""
        name = self._user_names.get(user_id)
        if name and f"{name}," not in text and text and not text.startswith(name):
            return f"{name}, {text[0].lower()}{text[1:]}" if text else text
        return text

    def register_user_name(self, user_id: str, name: str) -> None:
        """Store a display name for personalised greetings."""
        self._user_names[user_id] = name
        logger.debug("Registered display name for user=%s", user_id)
