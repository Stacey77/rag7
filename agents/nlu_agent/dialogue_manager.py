"""Multi-turn dialogue manager for NLU."""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DialogueAction:
    """An action the dialogue manager can take."""
    action_type: str           # "inform", "clarify", "confirm", "request_slot", "fulfill", "goodbye"
    intent: Optional[str] = None
    slot: Optional[str] = None
    message: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogueTurn:
    """One exchange in a multi-turn dialogue."""
    turn_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_input: str = ""
    intent: Optional[str] = None
    entities: Dict[str, Any] = field(default_factory=dict)
    action: Optional[DialogueAction] = None
    system_response: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DialogueState:
    """Tracks state across a multi-turn dialogue."""
    dialogue_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    current_intent: Optional[str] = None
    filled_slots: Dict[str, Any] = field(default_factory=dict)
    required_slots: List[str] = field(default_factory=list)
    stage: str = "open"          # "open" | "slot_filling" | "confirming" | "fulfilled" | "ended"
    turns: List[DialogueTurn] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


# Intent-to-required-slots mapping
_INTENT_SLOTS: Dict[str, List[str]] = {
    "deploy": ["service_name", "environment", "version"],
    "scale": ["service_name", "replicas"],
    "monitor": ["service_name", "metric"],
    "create": ["resource_type", "resource_name"],
    "delete": ["resource_type", "resource_name"],
    "update": ["resource_type", "resource_name", "parameter"],
    "train": ["model_name", "dataset"],
    "predict": ["model_name", "input_data"],
    "report": ["report_type", "time_range"],
}

_RESPONSE_TEMPLATES: Dict[str, str] = {
    "request_slot": "Could you please provide the {slot}?",
    "confirm": "You want to {intent} with {slots}. Shall I proceed?",
    "fulfill": "Done! I have successfully executed {intent} with {slots}.",
    "clarify": "I'm not sure I understood. Could you clarify what you mean?",
    "inform": "{message}",
    "goodbye": "Goodbye! Let me know if you need anything else.",
    "greeting": "Hello! How can I help you today?",
    "unknown": "I didn't quite understand that. Could you rephrase?",
}


def _fill_template(template: str, **kwargs: Any) -> str:
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


class SlotFiller:
    """Manages slot collection for intent fulfillment."""

    def get_missing_slots(self, state: DialogueState) -> List[str]:
        return [s for s in state.required_slots if s not in state.filled_slots]

    def fill_from_entities(self, state: DialogueState, entities: Dict[str, Any]) -> List[str]:
        """Try to fill slots from extracted entities. Returns newly filled slots."""
        filled: List[str] = []
        for slot in state.required_slots:
            if slot not in state.filled_slots and slot in entities:
                state.filled_slots[slot] = entities[slot]
                filled.append(slot)
        return filled


class DialoguePolicy:
    """Determines the system action given the current dialogue state."""

    def __init__(self, fulfillment_handlers: Optional[Dict[str, Callable]] = None) -> None:
        self._handlers = fulfillment_handlers or {}
        self._slot_filler = SlotFiller()

    def select_action(self, state: DialogueState, intent: Optional[str],
                      entities: Dict[str, Any]) -> DialogueAction:
        # Update intent & initialize required slots
        if intent and intent != state.current_intent:
            state.current_intent = intent
            state.required_slots = _INTENT_SLOTS.get(intent, [])
            state.filled_slots = {}
            state.stage = "slot_filling" if state.required_slots else "confirming"

        # Fill slots from entities
        if state.current_intent:
            self._slot_filler.fill_from_entities(state, entities)

        missing = self._slot_filler.get_missing_slots(state)

        if state.stage == "slot_filling" and missing:
            return DialogueAction(
                action_type="request_slot",
                slot=missing[0],
                message=_fill_template(_RESPONSE_TEMPLATES["request_slot"], slot=missing[0]),
            )

        if state.stage in ("slot_filling", "confirming") and not missing:
            state.stage = "confirming"
            slots_str = ", ".join(f"{k}={v}" for k, v in state.filled_slots.items())
            return DialogueAction(
                action_type="confirm",
                intent=state.current_intent,
                message=_fill_template(_RESPONSE_TEMPLATES["confirm"],
                                       intent=state.current_intent, slots=slots_str),
            )

        if intent == "confirm" and state.stage == "confirming":
            return self._fulfill(state)

        if intent == "deny":
            state.stage = "open"
            return DialogueAction(action_type="inform", message="Okay, action cancelled.")

        if intent in ("greeting",):
            return DialogueAction(action_type="inform",
                                  message=_RESPONSE_TEMPLATES["greeting"])

        if intent in ("farewell",):
            state.stage = "ended"
            return DialogueAction(action_type="goodbye",
                                  message=_RESPONSE_TEMPLATES["goodbye"])

        return DialogueAction(action_type="clarify",
                              message=_RESPONSE_TEMPLATES["clarify"])

    def _fulfill(self, state: DialogueState) -> DialogueAction:
        state.stage = "fulfilled"
        handler = self._handlers.get(state.current_intent or "")
        result = handler(state.filled_slots) if handler else "Action executed successfully."
        slots_str = ", ".join(f"{k}={v}" for k, v in state.filled_slots.items())
        return DialogueAction(
            action_type="fulfill",
            intent=state.current_intent,
            payload={"result": result, "slots": state.filled_slots},
            message=_fill_template(_RESPONSE_TEMPLATES["fulfill"],
                                   intent=state.current_intent, slots=slots_str),
        )


class DialogueManager:
    """
    Multi-turn dialogue manager coordinating intent understanding,
    slot filling, confirmation, and fulfillment across sessions.
    """

    def __init__(self, fulfillment_handlers: Optional[Dict[str, Callable]] = None) -> None:
        self._policy = DialoguePolicy(fulfillment_handlers)
        self._states: Dict[str, DialogueState] = {}
        logger.info("DialogueManager initialized")

    def get_or_create_state(self, dialogue_id: Optional[str] = None) -> DialogueState:
        if dialogue_id and dialogue_id in self._states:
            return self._states[dialogue_id]
        state = DialogueState(dialogue_id=dialogue_id or str(uuid.uuid4()))
        self._states[state.dialogue_id] = state
        return state

    def process_turn(self, dialogue_id: str, user_input: str,
                     intent: Optional[str] = None,
                     entities: Optional[Dict[str, Any]] = None) -> DialogueTurn:
        state = self.get_or_create_state(dialogue_id)
        entities = entities or {}

        action = self._policy.select_action(state, intent, entities)
        state.updated_at = datetime.utcnow()

        turn = DialogueTurn(
            user_input=user_input,
            intent=intent,
            entities=entities,
            action=action,
            system_response=action.message,
        )
        state.turns.append(turn)
        logger.debug("[%s] User: %.50s | Action: %s", dialogue_id, user_input, action.action_type)
        return turn

    def reset(self, dialogue_id: str) -> bool:
        state = self._states.get(dialogue_id)
        if state:
            state.stage = "open"
            state.current_intent = None
            state.filled_slots.clear()
            state.required_slots.clear()
            return True
        return False

    def get_state_summary(self, dialogue_id: str) -> Dict[str, Any]:
        state = self._states.get(dialogue_id)
        if not state:
            return {}
        return {
            "dialogue_id": dialogue_id,
            "stage": state.stage,
            "current_intent": state.current_intent,
            "filled_slots": state.filled_slots,
            "missing_slots": [s for s in state.required_slots if s not in state.filled_slots],
            "turn_count": len(state.turns),
        }
