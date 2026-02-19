"""Monitor user stress signals from interaction patterns."""

import logging
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from statistics import mean, stdev
from typing import Deque, Dict, List, Tuple

logger = logging.getLogger(__name__)

MAX_HISTORY = 50  # interactions kept per session


class StressLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class StressIndicator:
    """A single observable signal of stress."""
    signal_type: str       # e.g. "capitalization", "urgency_word", "fast_response"
    value: float           # normalised 0-1
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


URGENCY_WORDS = {"urgent", "asap", "immediately", "now", "emergency", "critical",
                 "broken", "down", "help", "please", "hurry", "fast", "quick"}

FRUSTRATION_PHRASES = {"this doesn't work", "nothing works", "i give up",
                       "what the hell", "why is this", "stupid", "useless"}


class StressMonitor:
    """Track stress signals across user interactions within a session."""

    def __init__(self) -> None:
        # user_id -> deque of (text, response_time_ms, timestamp)
        self._history: Dict[str, Deque[Tuple[str, float, datetime]]] = {}
        self._indicators: Dict[str, List[StressIndicator]] = {}
        logger.info("StressMonitor initialised.")

    def _ensure_user(self, user_id: str) -> None:
        if user_id not in self._history:
            self._history[user_id] = deque(maxlen=MAX_HISTORY)
            self._indicators[user_id] = []

    def record_interaction(self, text: str, response_time_ms: float, user_id: str = "default") -> None:
        """Record a single interaction and extract stress signals."""
        self._ensure_user(user_id)
        now = datetime.utcnow()
        self._history[user_id].append((text, response_time_ms, now))
        self._extract_signals(user_id, text, response_time_ms, now)

    def _extract_signals(self, user_id: str, text: str, rt_ms: float, ts: datetime) -> None:
        indicators = self._indicators[user_id]

        # Capitalisation ratio
        if len(text) > 0:
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
            if caps_ratio > 0.25:
                indicators.append(StressIndicator("capitalization", min(caps_ratio, 1.0),
                                                  f"High caps ratio ({caps_ratio:.0%})", ts))

        # Exclamation marks
        excl = text.count("!")
        if excl >= 2:
            indicators.append(StressIndicator("exclamation_marks", min(excl / 5, 1.0),
                                              f"{excl} exclamation marks", ts))

        # Urgency vocabulary
        words = set(text.lower().split())
        urgency_hits = words & URGENCY_WORDS
        if urgency_hits:
            indicators.append(StressIndicator("urgency_word", min(len(urgency_hits) / 3, 1.0),
                                              f"Urgency words: {', '.join(urgency_hits)}", ts))

        # Frustration phrases
        low_text = text.lower()
        for phrase in FRUSTRATION_PHRASES:
            if phrase in low_text:
                indicators.append(StressIndicator("frustration_phrase", 0.8,
                                                  f"Phrase detected: '{phrase}'", ts))
                break

        # Fast response time (< 3 s) signals possible panic / agitation
        if 0 < rt_ms < 3000:
            indicators.append(StressIndicator("fast_response", min((3000 - rt_ms) / 3000, 1.0),
                                              f"Very fast response: {rt_ms:.0f} ms", ts))

    def compute_stress_level(self, user_id: str = "default") -> StressLevel:
        """Aggregate recent signals into a StressLevel."""
        self._ensure_user(user_id)
        recent = [i for i in self._indicators[user_id][-20:]]
        if not recent:
            return StressLevel.LOW
        avg_score = mean(i.value for i in recent)
        if avg_score >= 0.75:
            return StressLevel.CRITICAL
        if avg_score >= 0.5:
            return StressLevel.HIGH
        if avg_score >= 0.25:
            return StressLevel.MEDIUM
        return StressLevel.LOW

    def get_stress_signals(self, user_id: str = "default") -> List[StressIndicator]:
        """Return all stress indicators collected for *user_id*."""
        self._ensure_user(user_id)
        return list(self._indicators[user_id])

    def trend(self, user_id: str = "default") -> str:
        """Return 'rising', 'falling', or 'stable' based on recent signal values."""
        self._ensure_user(user_id)
        scores = [i.value for i in self._indicators[user_id]]
        if len(scores) < 4:
            return "stable"
        first_half = mean(scores[:len(scores) // 2])
        second_half = mean(scores[len(scores) // 2:])
        delta = second_half - first_half
        if delta > 0.1:
            return "rising"
        if delta < -0.1:
            return "falling"
        return "stable"

    def reset_session(self, user_id: str = "default") -> None:
        """Clear all interaction history and indicators for *user_id*."""
        self._history[user_id] = deque(maxlen=MAX_HISTORY)
        self._indicators[user_id] = []
        logger.info("Session reset for user_id=%s", user_id)
