"""Generate empathetic, compassionate responses to user messages."""

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

ACKNOWLEDGEMENT_TEMPLATES = [
    "It sounds like you're going through a really tough time with {topic}.",
    "I can hear how {emotion} you're feeling right now.",
    "That must be genuinely difficult — {topic} is not easy to deal with.",
    "Your feelings about {topic} make complete sense.",
]

SUPPORT_TEMPLATES: Dict[str, List[str]] = {
    "sadness": [
        "I'm here with you, and you don't have to face this alone.",
        "It's okay to feel sad — take the time you need.",
        "Would it help to talk through what's weighing on you?",
    ],
    "anger": [
        "Your frustration is completely valid. Let's see what we can do.",
        "I understand why this situation would make anyone angry.",
        "Let's work through this together and find a way forward.",
    ],
    "fear": [
        "It's natural to feel scared. Let's break this down into smaller steps.",
        "You're not alone in this — we'll tackle it one piece at a time.",
        "Take a breath. We can figure this out together.",
    ],
    "frustration": [
        "I know this is really annoying. Let's try a different approach.",
        "Technical problems are so frustrating — let's get this sorted.",
        "You've been patient. Let's get to the bottom of this right now.",
    ],
    "joy": [
        "That's absolutely wonderful — you deserve this!",
        "Your happiness is contagious. Keep going!",
        "What a great moment — enjoy every bit of it!",
    ],
    "excitement": [
        "Yes! This is exciting — let's channel that energy!",
        "Your enthusiasm is inspiring. Let's make the most of it!",
        "Love the excitement — let's dive in!",
    ],
    "neutral": [
        "I'm here to help. Just let me know what you need.",
        "Happy to assist — what would be most useful right now?",
    ],
}

VALIDATION_PHRASES = [
    "What you're feeling is completely valid.",
    "Anyone in your position would feel the same way.",
    "Your reaction makes total sense given the circumstances.",
    "It's understandable to feel that way.",
]

ENCOURAGEMENT_PHRASES = [
    "You've got this — one step at a time.",
    "Every challenge you overcome makes you stronger.",
    "I believe in your ability to work through this.",
    "Progress isn't always linear, but you're moving forward.",
    "Small steps still count. Keep going.",
]


@dataclass
class CompassionResponse:
    """A structured empathetic response."""
    acknowledgement: str
    validation: str
    support: str
    encouragement: str
    full_response: str
    detected_emotion: str


class CompassionEngine:
    """Compose warm, empathetic responses grounded in the user's emotional state."""

    def __init__(self) -> None:
        logger.info("CompassionEngine initialised.")

    @staticmethod
    def _extract_topic(text: str) -> str:
        """Heuristically pull a short topic phrase from the user's message."""
        words = text.split()
        if len(words) <= 5:
            return text.strip().rstrip(".")
        # Use the first meaningful noun-phrase chunk (words 3-8)
        return " ".join(words[2:min(7, len(words))]).rstrip(".,!?")

    def acknowledge_struggle(self, text: str) -> str:
        """Return an acknowledgement sentence tailored to the message content."""
        topic = self._extract_topic(text)
        template = random.choice(ACKNOWLEDGEMENT_TEMPLATES)
        return template.format(topic=topic, emotion="difficult things")

    def offer_support(self, emotion: str) -> str:
        """Return a supportive statement appropriate for *emotion*."""
        options = SUPPORT_TEMPLATES.get(emotion, SUPPORT_TEMPLATES["neutral"])
        return random.choice(options)

    def validate_feelings(self, text: str) -> str:  # noqa: ARG002 (text reserved for future NLU)
        """Return a validation statement."""
        return random.choice(VALIDATION_PHRASES)

    def provide_encouragement(self) -> str:
        """Return an encouraging closing statement."""
        return random.choice(ENCOURAGEMENT_PHRASES)

    def generate(self, user_text: str, detected_emotion: str,
                 context: Optional[Dict] = None) -> CompassionResponse:
        """Compose a full CompassionResponse for *user_text*."""
        context = context or {}
        acknowledgement = self.acknowledge_struggle(user_text)
        validation = self.validate_feelings(user_text)
        support = self.offer_support(detected_emotion)
        encouragement = self.provide_encouragement()
        full = " ".join([acknowledgement, validation, support, encouragement])
        logger.debug("CompassionResponse generated for emotion=%s", detected_emotion)
        return CompassionResponse(
            acknowledgement=acknowledgement,
            validation=validation,
            support=support,
            encouragement=encouragement,
            full_response=full,
            detected_emotion=detected_emotion,
        )
