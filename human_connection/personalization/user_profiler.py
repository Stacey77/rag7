"""Learn and store user preferences for personalised AI experiences."""

import logging
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

EXPERTISE_THRESHOLDS = {"novice": 0.3, "intermediate": 0.6, "expert": 1.0}
TECHNICAL_TERMS = {
    "algorithm", "parameter", "function", "class", "object", "module",
    "api", "endpoint", "database", "query", "schema", "latency", "throughput",
    "gradient", "tensor", "embedding", "inference", "pipeline",
}


@dataclass
class UserProfile:
    """Stored profile for a single user."""
    user_id: str
    preferences: Dict[str, Any] = field(default_factory=dict)
    communication_style: str = "balanced"   # "concise", "detailed", "balanced"
    expertise_level: str = "intermediate"   # "novice", "intermediate", "expert"
    interaction_count: int = 0
    last_seen: datetime = field(default_factory=datetime.utcnow)
    vocabulary: Counter = field(default_factory=Counter)


class UserProfiler:
    """Build and maintain user profiles through interaction history."""

    def __init__(self) -> None:
        self._profiles: Dict[str, UserProfile] = {}
        logger.info("UserProfiler initialised.")

    def _ensure_profile(self, user_id: str) -> UserProfile:
        if user_id not in self._profiles:
            self._profiles[user_id] = UserProfile(user_id=user_id)
        return self._profiles[user_id]

    def update(self, user_id: str, interaction: Dict[str, Any]) -> None:
        """Incorporate a new interaction into the user's profile."""
        profile = self._ensure_profile(user_id)
        profile.interaction_count += 1
        profile.last_seen = datetime.utcnow()

        text: str = interaction.get("text", "")
        if text:
            words = text.lower().split()
            profile.vocabulary.update(words)

        # Update preferences from explicit keys
        for key in ("topic", "format", "language", "domain"):
            if key in interaction:
                profile.preferences[key] = interaction[key]

        # Infer communication style from message length
        word_count = len(text.split()) if text else 0
        if word_count > 80:
            profile.communication_style = "detailed"
        elif word_count < 20:
            profile.communication_style = "concise"

        profile.expertise_level = self.infer_expertise(user_id)
        logger.debug("Profile updated: user=%s interactions=%d", user_id, profile.interaction_count)

    def get_profile(self, user_id: str) -> UserProfile:
        """Return the UserProfile for *user_id*, creating one if needed."""
        return self._ensure_profile(user_id)

    def infer_expertise(self, user_id: str) -> str:
        """Estimate expertise level from technical vocabulary usage."""
        profile = self._profiles.get(user_id)
        if not profile or not profile.vocabulary:
            return "intermediate"
        total_words = sum(profile.vocabulary.values())
        tech_words = sum(profile.vocabulary[w] for w in TECHNICAL_TERMS if w in profile.vocabulary)
        ratio = tech_words / max(total_words, 1)
        if ratio >= 0.08:
            return "expert"
        if ratio >= 0.03:
            return "intermediate"
        return "novice"

    def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Return the stored preference dictionary for *user_id*."""
        return self._ensure_profile(user_id).preferences.copy()

    def similar_users(self, user_id: str) -> List[str]:
        """Return user IDs with similar expertise and communication style."""
        target = self._profiles.get(user_id)
        if not target:
            return []
        return [
            uid for uid, profile in self._profiles.items()
            if uid != user_id
            and profile.expertise_level == target.expertise_level
            and profile.communication_style == target.communication_style
        ]
