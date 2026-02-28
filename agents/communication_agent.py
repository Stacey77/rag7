"""
Communication agent module for the RAG7 AGI Robotics Framework.

Handles natural language understanding and generation to enable
human-robot interaction through text-based commands.
"""

import logging
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseAgent

try:
    from langchain_openai import ChatOpenAI  # noqa: F401

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class CommunicationAgent(BaseAgent):
    """Agent responsible for natural language communication.

    Parses incoming text commands into structured intents and generates
    natural language responses.  Uses LangChain with an LLM backend when
    available; falls back to keyword-based parsing otherwise.

    Args:
        config: Communication agent configuration dictionary.
        llm_config: Optional LLM configuration dictionary.
    """

    # Supported intent labels
    INTENTS = ["navigate", "grasp", "place", "inspect", "stop", "query", "unknown"]

    def __init__(
        self,
        config: Dict[str, Any],
        llm_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the communication agent."""
        super().__init__(
            name="communication_agent",
            config=config,
            logger=logging.getLogger("rag7.communication"),
        )
        self._llm_config = llm_config or {}
        self._llm = None
        self._dialog_history: List[Dict[str, str]] = []
        self._max_history = config.get("max_dialog_history", 10)

        if LANGCHAIN_AVAILABLE and self._llm_config.get("provider") == "openai":
            self._try_init_llm()

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def perceive(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming message observation.

        Args:
            observation: Dictionary with optional ``message`` key
                containing the user text.

        Returns:
            Parsed command dict produced by :meth:`parse_command`.
        """
        message = observation.get("message", "")
        parsed = self.parse_command(message) if message else {}
        self.update_state("last_parsed_command", parsed)
        return parsed

    def reason(self, context: Any) -> Dict[str, Any]:
        """Generate an appropriate text response for the given context.

        Args:
            context: Dictionary with ``intent`` and ``robot_state`` keys,
                or a plain string.

        Returns:
            Dictionary with ``response`` string.
        """
        if isinstance(context, str):
            response = self.generate_response({"intent": self.classify_intent(context)})
        else:
            response = self.generate_response(context)
        return {"response": response}

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Send or receive a message.

        Args:
            action: Dictionary with ``type`` key (``send`` or ``receive``)
                and ``message`` payload.

        Returns:
            Result dictionary.
        """
        action_type = action.get("type", "")
        message = action.get("message", "")

        if action_type == "send":
            self._dialog_history.append({"role": "robot", "content": message})
            if len(self._dialog_history) > self._max_history:
                self._dialog_history.pop(0)
            return {"status": "sent", "message": message}

        if action_type == "receive":
            parsed = self.parse_command(message)
            self._dialog_history.append({"role": "human", "content": message})
            if len(self._dialog_history) > self._max_history:
                self._dialog_history.pop(0)
            return {"status": "received", "parsed": parsed}

        return {"status": "unknown_action"}

    # ------------------------------------------------------------------
    # Public NLP API
    # ------------------------------------------------------------------

    def parse_command(self, text: str) -> Dict[str, Any]:
        """Parse a natural language command into a structured representation.

        Args:
            text: Raw natural language input from the operator.

        Returns:
            Dictionary with keys:
                - ``intent``: Detected intent string.
                - ``action``: Primary action verb.
                - ``target_object``: Target object (if detected).
                - ``location``: Target location (if detected).
                - ``confidence``: Confidence score between 0 and 1.
        """
        if self._llm is not None:
            try:
                return self._llm_parse(text)
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("LLM parsing failed: %s", exc)

        return self._rule_based_parse(text)

    def generate_response(self, context: Dict[str, Any]) -> str:
        """Generate a natural language response for the given context.

        Args:
            context: Dictionary with ``intent`` and optional
                ``robot_state`` keys.

        Returns:
            Response string.
        """
        intent = context.get("intent", "unknown")
        robot_state = context.get("robot_state", {})

        if self._llm is not None:
            try:
                prompt = (
                    f"Robot status: {robot_state}\n"
                    f"Intent: {intent}\n"
                    "Generate a concise robot status response:"
                )
                resp = self._llm.invoke(prompt)
                return resp.content.strip()
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("LLM response generation failed: %s", exc)

        return self._template_response(intent, robot_state)

    def classify_intent(self, text: str) -> str:
        """Classify the primary intent of a text string.

        Args:
            text: Natural language input.

        Returns:
            Intent string from :attr:`INTENTS`.
        """
        text_lower = text.lower()

        keyword_map = {
            "navigate": ["go", "move", "navigate", "drive", "travel", "head"],
            "grasp": ["grasp", "pick", "grab", "take", "hold", "lift"],
            "place": ["place", "put", "drop", "set", "release"],
            "inspect": ["inspect", "look", "examine", "scan", "check", "observe"],
            "stop": ["stop", "halt", "freeze", "pause", "emergency"],
            "query": ["what", "where", "how", "status", "tell", "show", "report"],
        }

        for intent, keywords in keyword_map.items():
            if any(kw in text_lower for kw in keywords):
                return intent

        return "unknown"

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _rule_based_parse(self, text: str) -> Dict[str, Any]:
        """Fallback rule-based command parser.

        Args:
            text: Raw natural language input.

        Returns:
            Structured command dictionary.
        """
        intent = self.classify_intent(text)
        words = text.lower().split()

        # Extract simple numeric location tokens
        location = None
        for i, word in enumerate(words):
            if word in ("to", "at", "towards") and i + 1 < len(words):
                location = words[i + 1]
                break

        return {
            "intent": intent,
            "action": intent,
            "target_object": None,
            "location": location,
            "confidence": 0.6,
        }

    def _llm_parse(self, text: str) -> Dict[str, Any]:
        """Parse a command using the LLM backend.

        Args:
            text: Raw natural language input.

        Returns:
            Structured command dictionary.
        """
        prompt = (
            f"Parse this robot command: '{text}'\n"
            "Return JSON with keys: intent, action, target_object, location, confidence."
        )
        import json

        response = self._llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._rule_based_parse(text)

    def _template_response(self, intent: str, robot_state: Dict[str, Any]) -> str:
        """Generate a templated response string.

        Args:
            intent: Detected intent.
            robot_state: Current robot state dictionary.

        Returns:
            Human-readable response string.
        """
        templates = {
            "navigate": "Understood. Navigating to the specified location.",
            "grasp": "Acknowledged. Attempting to grasp the object.",
            "place": "Understood. Placing the object at the target location.",
            "inspect": "Initiating inspection of the specified area.",
            "stop": "Emergency stop acknowledged. All motion halted.",
            "query": f"Current robot state: {robot_state}",
            "unknown": "Command not understood. Please rephrase.",
        }
        return templates.get(intent, templates["unknown"])

    def _try_init_llm(self) -> None:
        """Attempt to initialise the LangChain LLM client."""
        try:
            import os

            from langchain_openai import ChatOpenAI

            api_key = os.environ.get(
                self._llm_config.get("api_key_env", "OPENAI_API_KEY"), ""
            )
            if not api_key:
                return
            self._llm = ChatOpenAI(
                model=self._llm_config.get("model", "gpt-4"),
                temperature=self._llm_config.get("temperature", 0.1),
                openai_api_key=api_key,
            )
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Failed to initialise LLM for communication: %s", exc)
