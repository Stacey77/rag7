"""Suggest healthy breaks based on continuous work patterns."""

import logging
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

BREAK_ACTIVITIES = {
    "micro": ["Take 5 deep breaths.", "Roll your shoulders back 5 times.",
              "Look away from the screen and focus on something 20 feet away for 20 seconds."],
    "short": ["Walk around the room for 5 minutes.", "Make a cup of tea or water.",
              "Do a quick 5-minute stretch routine.", "Step outside for fresh air."],
    "long": ["Take a 15-minute walk outside.", "Eat a healthy snack away from your desk.",
             "Try a 10-minute guided meditation.", "Chat with a colleague about something non-work."],
    "recovery": ["Finish work for the day — you've earned it.",
                 "Take a proper lunch break away from all screens.",
                 "Schedule at least 30 minutes of restorative activity this evening."],
}

WORK_DURATION_THRESHOLDS = {
    "micro": timedelta(minutes=30),
    "short": timedelta(hours=1),
    "long": timedelta(hours=2),
    "recovery": timedelta(hours=4),
}


@dataclass
class BreakSuggestion:
    """A recommended break for a user."""
    break_type: str              # "micro", "short", "long", "recovery"
    duration_minutes: int
    reason: str
    activity_suggestion: str
    created_at: datetime = field(default_factory=datetime.utcnow)


DURATION_MAP = {"micro": 2, "short": 5, "long": 15, "recovery": 30}


class BreakSuggester:
    """Track work sessions and suggest appropriate breaks."""

    def __init__(self) -> None:
        # user_id -> (session_start, last_break)
        self._sessions: Dict[str, datetime] = {}
        self._last_break: Dict[str, Optional[datetime]] = defaultdict(lambda: None)
        self._break_log: Dict[str, List[datetime]] = defaultdict(list)
        self._interaction_count: Dict[str, int] = defaultdict(int)
        logger.info("BreakSuggester initialised.")

    def _work_duration(self, user_id: str) -> timedelta:
        start = self._sessions.get(user_id)
        if start is None:
            self._sessions[user_id] = datetime.utcnow()
            return timedelta(0)
        return datetime.utcnow() - start

    def _classify_break(self, duration: timedelta) -> str:
        for break_type in ("recovery", "long", "short", "micro"):
            if duration >= WORK_DURATION_THRESHOLDS[break_type]:
                return break_type
        return "micro"

    def should_suggest_break(self, user_id: str) -> bool:
        """Return True if a break is due for *user_id*."""
        self._interaction_count[user_id] += 1
        duration = self._work_duration(user_id)
        # Suggest every 30 min of continuous work, or every 20 interactions
        return (duration >= WORK_DURATION_THRESHOLDS["micro"] or
                self._interaction_count[user_id] % 20 == 0)

    def suggest(self, user_id: str) -> BreakSuggestion:
        """Build a BreakSuggestion tailored to the user's current work duration."""
        duration = self._work_duration(user_id)
        break_type = self._classify_break(duration)
        activity = random.choice(BREAK_ACTIVITIES[break_type])
        minutes_worked = int(duration.total_seconds() / 60)
        reason = (f"You've been working for {minutes_worked} minutes without a break. "
                  f"A {break_type} break will help you stay focused.")
        suggestion = BreakSuggestion(
            break_type=break_type,
            duration_minutes=DURATION_MAP[break_type],
            reason=reason,
            activity_suggestion=activity,
        )
        logger.debug("Break suggestion (%s) for user=%s", break_type, user_id)
        return suggestion

    def record_break_taken(self, user_id: str) -> None:
        """Mark that the user has taken a break — reset the work-session clock."""
        now = datetime.utcnow()
        self._sessions[user_id] = now
        self._last_break[user_id] = now
        self._break_log[user_id].append(now)
        self._interaction_count[user_id] = 0
        logger.info("Break recorded for user=%s at %s", user_id, now.isoformat())

    def get_break_stats(self, user_id: str) -> Dict:
        """Return a summary of break-taking behaviour for *user_id*."""
        log = self._break_log.get(user_id, [])
        if not log:
            return {"total_breaks": 0, "last_break": None, "avg_break_gap_minutes": None}

        gaps: List[float] = []
        for i in range(1, len(log)):
            gap = (log[i] - log[i - 1]).total_seconds() / 60
            gaps.append(gap)

        return {
            "total_breaks": len(log),
            "last_break": log[-1].isoformat(),
            "avg_break_gap_minutes": round(sum(gaps) / len(gaps), 1) if gaps else None,
            "continuous_work_minutes": int(self._work_duration(user_id).total_seconds() / 60),
        }
