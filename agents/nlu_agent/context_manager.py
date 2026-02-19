"""Conversation context manager for multi-turn NLU."""
from __future__ import annotations

import logging
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Turn:
    """A single conversational turn."""
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "user"   # "user" | "assistant" | "system"
    text: str = ""
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    sentiment: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationState:
    """Tracks state across a conversation session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    domain: str = "general"
    active_intent: Optional[str] = None
    slots: Dict[str, Any] = field(default_factory=dict)  # intent-specific slot values
    pending_clarification: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    context_vars: Dict[str, Any] = field(default_factory=dict)  # free-form shared context


class ConversationContext:
    """
    Manages conversation history, slot state, and context resolution
    for a single user session.
    """

    def __init__(self, session_id: Optional[str] = None, window: int = 10,
                 ttl_minutes: int = 30) -> None:
        self.state = ConversationState(session_id=session_id or str(uuid.uuid4()))
        self._history: deque[Turn] = deque(maxlen=100)
        self._window = window          # number of turns to keep in active context
        self._ttl = timedelta(minutes=ttl_minutes)
        logger.debug("ConversationContext created: session=%s", self.state.session_id)

    @property
    def session_id(self) -> str:
        return self.state.session_id

    def is_expired(self) -> bool:
        return datetime.utcnow() - self.state.last_active > self._ttl

    def add_turn(self, role: str, text: str, intent: Optional[str] = None,
                 entities: Optional[Dict[str, Any]] = None,
                 sentiment: Optional[str] = None) -> Turn:
        turn = Turn(role=role, text=text, intent=intent,
                    entities=entities or {}, sentiment=sentiment)
        self._history.append(turn)
        self.state.last_active = datetime.utcnow()

        if intent:
            self.state.active_intent = intent
        if entities:
            self.state.slots.update(entities)

        logger.debug("Turn added [%s]: %.60s", role, text)
        return turn

    def get_context_window(self) -> List[Turn]:
        """Return the last N turns as context."""
        history = list(self._history)
        return history[-self._window:]

    def get_history(self) -> List[Turn]:
        return list(self._history)

    def set_slot(self, key: str, value: Any) -> None:
        self.state.slots[key] = value

    def get_slot(self, key: str, default: Any = None) -> Any:
        return self.state.slots.get(key, default)

    def clear_slots(self) -> None:
        self.state.slots.clear()

    def set_var(self, key: str, value: Any) -> None:
        self.state.context_vars[key] = value

    def get_var(self, key: str, default: Any = None) -> Any:
        return self.state.context_vars.get(key, default)

    def resolve_coreference(self, text: str) -> str:
        """Resolve pronouns to the most recent entity in context."""
        replacements = {"it": None, "they": None, "this": None, "that": None}
        # Find the most recently mentioned entity value
        for turn in reversed(list(self._history)):
            for val in turn.entities.values():
                if isinstance(val, str) and len(val) > 2:
                    for pronoun in list(replacements.keys()):
                        if replacements[pronoun] is None:
                            replacements[pronoun] = val
                    break
            if all(v is not None for v in replacements.values()):
                break

        resolved = text
        for pronoun, replacement in replacements.items():
            if replacement:
                import re
                resolved = re.sub(r"\b" + pronoun + r"\b", replacement, resolved, flags=re.IGNORECASE)
        return resolved

    def build_prompt_context(self) -> str:
        """Build a text summary of recent context for prompt augmentation."""
        lines: List[str] = []
        if self.state.active_intent:
            lines.append(f"Active intent: {self.state.active_intent}")
        if self.state.slots:
            lines.append("Known slots: " + ", ".join(f"{k}={v}" for k, v in list(self.state.slots.items())[:5]))
        for turn in self.get_context_window()[-5:]:
            lines.append(f"[{turn.role}] {turn.text[:100]}")
        return "\n".join(lines)

    def summarize(self) -> Dict[str, Any]:
        return {
            "session_id": self.state.session_id,
            "domain": self.state.domain,
            "turn_count": len(self._history),
            "active_intent": self.state.active_intent,
            "slots": self.state.slots,
            "last_active": self.state.last_active.isoformat(),
            "expired": self.is_expired(),
        }


class ContextManager:
    """
    Multi-session conversation context manager.
    Creates, retrieves, and expires conversation contexts.
    """

    def __init__(self, window: int = 10, ttl_minutes: int = 30) -> None:
        self._sessions: Dict[str, ConversationContext] = {}
        self._window = window
        self._ttl_minutes = ttl_minutes
        logger.info("ContextManager initialized")

    def get_or_create(self, session_id: Optional[str] = None,
                      user_id: Optional[str] = None) -> ConversationContext:
        if session_id and session_id in self._sessions:
            ctx = self._sessions[session_id]
            if not ctx.is_expired():
                return ctx
            logger.info("Session %s expired; creating new session", session_id)

        ctx = ConversationContext(session_id=session_id, window=self._window,
                                  ttl_minutes=self._ttl_minutes)
        if user_id:
            ctx.state.user_id = user_id
        self._sessions[ctx.session_id] = ctx
        logger.info("Created new session: %s", ctx.session_id)
        return ctx

    def get(self, session_id: str) -> Optional[ConversationContext]:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        return bool(self._sessions.pop(session_id, None))

    def purge_expired(self) -> int:
        expired = [sid for sid, ctx in self._sessions.items() if ctx.is_expired()]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            logger.info("Purged %d expired sessions", len(expired))
        return len(expired)

    def active_session_count(self) -> int:
        return sum(1 for ctx in self._sessions.values() if not ctx.is_expired())

    def stats(self) -> Dict[str, Any]:
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": self.active_session_count(),
            "expired_sessions": len(self._sessions) - self.active_session_count(),
        }
