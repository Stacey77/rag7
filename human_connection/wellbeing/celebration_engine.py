"""Celebrate user wins and build positive reinforcement."""

import logging
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

CELEBRATION_TEMPLATES = {
    "learning": ["🎓 Levelled up! {achievement} shows real growth.", "📚 {achievement} — you're becoming an expert!"],
    "productivity": ["⚡ Crushed it! {achievement} done.", "✅ {achievement} — efficiency at its best!"],
    "problem_solving": ["🔧 Bug squashed! {achievement} solved.", "🧠 Great problem-solving with {achievement}!"],
    "creativity": ["🎨 Creative genius! {achievement} is inspired.", "✨ {achievement} — what imagination!"],
    "social": ["🤝 Team player! {achievement} made a difference.", "💬 Connection counts: {achievement}!"],
    "general": ["🎉 Well done on {achievement}!", "🌟 {achievement} — you should be proud!",
                "🚀 {achievement} — keep the momentum going!"],
}

MILESTONE_MESSAGES = {
    1: "🌱 First achievement unlocked — every journey starts here!",
    5: "⭐ Five achievements! You're building momentum.",
    10: "🔥 Ten achievements — you're on fire!",
    25: "💎 25 achievements! Remarkable consistency.",
    50: "🏆 50 achievements! You're in elite company.",
    100: "🌟 100 achievements! A true champion.",
}


@dataclass
class Achievement:
    """A recorded user achievement."""
    user_id: str
    description: str
    category: str
    achievement_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CelebrationMessage:
    """A celebration message for an achievement."""
    message: str
    emoji: str
    achievement: Achievement
    milestone_message: Optional[str] = None


class CelebrationEngine:
    """Track achievements and generate enthusiastic celebration messages."""

    def __init__(self) -> None:
        self._achievements: Dict[str, List[Achievement]] = defaultdict(list)
        self._streaks: Dict[str, List[datetime]] = defaultdict(list)
        logger.info("CelebrationEngine initialised.")

    def record_achievement(self, user_id: str, achievement: str, category: str = "general") -> Achievement:
        """Store a new achievement for *user_id* and return it."""
        a = Achievement(user_id=user_id, description=achievement, category=category)
        self._achievements[user_id].append(a)
        self._streaks[user_id].append(a.timestamp)
        logger.info("Achievement recorded: user=%s category=%s", user_id, category)
        return a

    def generate_celebration(self, achievement: Achievement) -> CelebrationMessage:
        """Create a CelebrationMessage for *achievement*."""
        templates = CELEBRATION_TEMPLATES.get(achievement.category, CELEBRATION_TEMPLATES["general"])
        message = random.choice(templates).format(achievement=achievement.description)
        emoji = message[0] if message and not message[0].isalpha() else "🎉"

        total = len(self._achievements.get(achievement.user_id, []))
        milestone_msg = self.get_milestone_message(total) if total in MILESTONE_MESSAGES else None

        return CelebrationMessage(message=message, emoji=emoji,
                                  achievement=achievement, milestone_message=milestone_msg)

    def get_milestone_message(self, count: int) -> str:
        """Return a milestone message for a given achievement *count*."""
        # Return the closest milestone message at or below count
        matching = [n for n in MILESTONE_MESSAGES if n <= count]
        if not matching:
            return "🎯 Keep going — your first milestone is within reach!"
        return MILESTONE_MESSAGES[max(matching)]

    def weekly_summary(self, user_id: str) -> str:
        """Summarise achievements from the past 7 days for *user_id*."""
        cutoff = datetime.utcnow() - timedelta(days=7)
        recent = [a for a in self._achievements.get(user_id, []) if a.timestamp >= cutoff]
        if not recent:
            return f"No achievements this week yet, {user_id} — there's still time to create some!"
        by_cat: Dict[str, int] = defaultdict(int)
        for a in recent:
            by_cat[a.category] += 1
        top_cat = max(by_cat, key=lambda c: by_cat[c])
        lines = [f"  • {a.description}" for a in recent[-5:]]
        summary = (f"🗓️ Weekly summary for {user_id}: {len(recent)} achievement(s) this week!\n"
                   f"Top category: {top_cat}\nRecent highlights:\n" + "\n".join(lines))
        return summary

    def get_streak(self, user_id: str) -> int:
        """Return the current consecutive-day achievement streak for *user_id*."""
        dates = sorted({d.date() for d in self._streaks.get(user_id, [])}, reverse=True)
        if not dates:
            return 0
        streak = 1
        for i in range(1, len(dates)):
            if (dates[i - 1] - dates[i]).days == 1:
                streak += 1
            else:
                break
        return streak
