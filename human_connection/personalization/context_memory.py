"""Remember and utilise user context across sessions."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)

RELEVANCE_THRESHOLD = 0.2   # minimum score to include in recall results
DEFAULT_IMPORTANCE = 0.5


@dataclass
class MemoryEntry:
    """A single remembered fact about a user."""
    user_id: str
    key: str
    value: str
    importance: float          # 0-1; higher = kept longer, surfaced first
    entry_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0


class ContextMemory:
    """Long-term, importance-weighted context memory for each user."""

    def __init__(self) -> None:
        self._memory: Dict[str, List[MemoryEntry]] = defaultdict(list)
        logger.info("ContextMemory initialised.")

    def remember(self, user_id: str, key: str, value: str,
                 importance: float = DEFAULT_IMPORTANCE) -> MemoryEntry:
        """Store a key-value memory for *user_id*, overwriting if key already exists."""
        importance = max(0.0, min(1.0, importance))
        entries = self._memory[user_id]
        # Overwrite existing entry with same key
        for entry in entries:
            if entry.key == key:
                entry.value = value
                entry.importance = importance
                entry.accessed_at = datetime.utcnow()
                logger.debug("Updated memory key=%s user=%s", key, user_id)
                return entry
        new_entry = MemoryEntry(user_id=user_id, key=key, value=value, importance=importance)
        entries.append(new_entry)
        logger.debug("Stored new memory key=%s user=%s", key, user_id)
        return new_entry

    def recall(self, user_id: str, query: str) -> List[MemoryEntry]:
        """Return memories relevant to *query*, sorted by relevance score."""
        entries = self._memory.get(user_id, [])
        query_words = set(query.lower().split())
        scored: List[tuple] = []
        for entry in entries:
            key_words = set(entry.key.lower().split("_"))
            val_words = set(entry.value.lower().split())
            overlap = len(query_words & (key_words | val_words))
            score = (overlap / max(len(query_words), 1)) * 0.7 + entry.importance * 0.3
            if score >= RELEVANCE_THRESHOLD:
                entry.accessed_at = datetime.utcnow()
                entry.access_count += 1
                scored.append((score, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored]

    def forget_old_memories(self, user_id: str, days: int = 30) -> int:
        """Remove memories older than *days* days with low importance. Returns count removed."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        before = len(self._memory.get(user_id, []))
        self._memory[user_id] = [
            e for e in self._memory.get(user_id, [])
            if e.created_at > cutoff or e.importance >= 0.7
        ]
        removed = before - len(self._memory[user_id])
        logger.info("Forgot %d old memories for user=%s", removed, user_id)
        return removed

    def get_context_summary(self, user_id: str) -> str:
        """Return a human-readable summary of stored context for *user_id*."""
        entries = self._memory.get(user_id, [])
        if not entries:
            return "No context stored yet."
        top = sorted(entries, key=lambda e: e.importance, reverse=True)[:5]
        lines = [f"• {e.key}: {e.value}" for e in top]
        return f"Context summary for {user_id} ({len(entries)} memories):\n" + "\n".join(lines)

    def find_relevant(self, user_id: str, text: str) -> List[MemoryEntry]:
        """Alias for recall with a natural-language text query."""
        return self.recall(user_id, text)

    def all_memories(self, user_id: str) -> List[MemoryEntry]:
        """Return all memories for *user_id*, newest first."""
        return sorted(self._memory.get(user_id, []),
                      key=lambda e: e.created_at, reverse=True)
