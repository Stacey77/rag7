"""Track the human impact of AI interactions."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

WELLBEING_CATEGORIES = {"learning", "productivity", "emotional_support",
                        "problem_solving", "creativity", "health", "social"}

WIN_THRESHOLD = 0.7   # value_score >= this is highlighted as a win


@dataclass
class ImpactEvent:
    """A single recorded impact event."""
    category: str
    description: str
    value_score: float          # 0-1, higher = more positive impact
    user_id: str
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ImpactSummary:
    """Aggregated impact summary for one user."""
    user_id: str
    total_events: int
    average_value_score: float
    top_category: str
    win_count: int
    wellbeing_score: float
    generated_at: datetime = field(default_factory=datetime.utcnow)


class ImpactTracker:
    """Record and analyse the positive impact AI interactions have on users."""

    def __init__(self) -> None:
        self._events: Dict[str, List[ImpactEvent]] = defaultdict(list)
        logger.info("ImpactTracker initialised.")

    def record(self, event: ImpactEvent) -> None:
        """Persist a new impact event."""
        event.value_score = max(0.0, min(1.0, event.value_score))
        self._events[event.user_id].append(event)
        logger.debug("Recorded impact event category=%s user=%s score=%.2f",
                     event.category, event.user_id, event.value_score)

    def get_summary(self, user_id: str) -> ImpactSummary:
        """Return an aggregated ImpactSummary for *user_id*."""
        events = self._events.get(user_id, [])
        if not events:
            return ImpactSummary(user_id=user_id, total_events=0, average_value_score=0.0,
                                 top_category="none", win_count=0, wellbeing_score=0.0)

        scores = [e.value_score for e in events]
        avg = round(mean(scores), 3)
        wins = sum(1 for s in scores if s >= WIN_THRESHOLD)
        cat_counts: Dict[str, int] = defaultdict(int)
        for e in events:
            cat_counts[e.category] += 1
        top_cat = max(cat_counts, key=lambda c: cat_counts[c])
        wellbeing = self.compute_wellbeing_score(user_id)
        return ImpactSummary(user_id=user_id, total_events=len(events),
                             average_value_score=avg, top_category=top_cat,
                             win_count=wins, wellbeing_score=wellbeing)

    def compute_wellbeing_score(self, user_id: str) -> float:
        """Compute a 0-1 wellbeing score from category diversity and value scores."""
        events = self._events.get(user_id, [])
        if not events:
            return 0.0
        scores = [e.value_score for e in events]
        avg_score = mean(scores)
        cats = {e.category for e in events}
        diversity_bonus = min(len(cats) / len(WELLBEING_CATEGORIES), 1.0) * 0.2
        wellbeing = round(min(avg_score + diversity_bonus, 1.0), 3)
        logger.debug("Wellbeing score for user=%s: %.3f", user_id, wellbeing)
        return wellbeing

    def highlight_wins(self, user_id: str) -> List[str]:
        """Return descriptions of high-value impact events for *user_id*."""
        events = self._events.get(user_id, [])
        return [f"[{e.category.upper()}] {e.description}"
                for e in events if e.value_score >= WIN_THRESHOLD]

    def generate_impact_report(self) -> Dict:
        """Produce a platform-wide impact report across all users."""
        all_events = [e for events in self._events.values() for e in events]
        if not all_events:
            return {"total_users": 0, "total_events": 0, "platform_wellbeing": 0.0, "categories": {}}

        cat_scores: Dict[str, List[float]] = defaultdict(list)
        for e in all_events:
            cat_scores[e.category].append(e.value_score)

        return {
            "total_users": len(self._events),
            "total_events": len(all_events),
            "platform_wellbeing": round(mean(e.value_score for e in all_events), 3),
            "categories": {cat: {"count": len(v), "avg_score": round(mean(v), 3)}
                           for cat, v in cat_scores.items()},
        }
