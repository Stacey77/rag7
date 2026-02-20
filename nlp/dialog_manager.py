"""
Dialog manager module for the rag7 NLP system.

Manages multi-turn conversations between human operators and the robot,
maintaining dialog history and generating contextually appropriate
responses.
"""

import logging
from typing import Any, Dict, List, Optional

from nlp.intent_classifier import IntentClassifier


class DialogManager:
    """Multi-turn dialog manager for human-robot interaction.

    Maintains conversation history and generates contextually aware
    responses based on detected intent and robot state.

    Args:
        max_history: Maximum number of dialog turns to retain.
    """

    def __init__(self, max_history: int = 10) -> None:
        """Initialize the dialog manager."""
        self._logger = logging.getLogger("rag7.nlp.dialog")
        self._max_history = max_history
        self._history: List[Dict[str, str]] = []
        self._classifier = IntentClassifier()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(
        self, user_input: str, robot_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process a user utterance and return a robot response.

        Args:
            user_input: Free-text message from the operator.
            robot_state: Optional current robot state dictionary.

        Returns:
            Response string from the robot.
        """
        robot_state = robot_state or {}
        intent = self._classifier.classify(user_input)
        self.add_turn("human", user_input)
        response = self._generate_response(intent, robot_state)
        self.add_turn("robot", response)
        return response

    def add_turn(self, role: str, content: str) -> None:
        """Add a single dialog turn to the history.

        Args:
            role: Speaker role (``"human"`` or ``"robot"``).
            content: Utterance content string.
        """
        self._history.append({"role": role, "content": content})
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def get_history(self) -> List[Dict[str, str]]:
        """Return the current conversation history.

        Returns:
            List of turn dictionaries with ``role`` and ``content`` keys.
        """
        return list(self._history)

    def clear_history(self) -> None:
        """Clear all stored dialog turns."""
        self._history.clear()
        self._logger.debug("Dialog history cleared.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _generate_response(
        self, intent: str, robot_state: Dict[str, Any]
    ) -> str:
        """Generate a contextually appropriate robot response.

        Args:
            intent: Classified intent string.
            robot_state: Current robot state dictionary.

        Returns:
            Response string.
        """
        is_stopped = robot_state.get("is_stopped", False)
        position = robot_state.get("position", {})
        pos_str = ""
        if position:
            pos_str = (
                f" Current position: ({position.get('x', 0):.2f}, "
                f"{position.get('y', 0):.2f})."
            )

        if is_stopped:
            return "Emergency stop is active. Please reset before issuing new commands."

        responses = {
            "navigate": f"Understood. I will navigate to the specified location.{pos_str}",
            "grasp": "Acknowledged. Initiating grasp sequence for the target object.",
            "place": "Understood. I will place the object at the specified location.",
            "inspect": f"Starting inspection scan.{pos_str}",
            "stop": "Emergency stop engaged. All motion halted immediately.",
            "query": f"System is operational.{pos_str} All agents are running.",
            "unknown": (
                "I did not understand that command. "
                "Please try: navigate, grasp, place, inspect, stop, or query."
            ),
        }
        return responses.get(intent, responses["unknown"])
