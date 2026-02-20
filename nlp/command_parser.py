"""
Command parser module for the RAG7 NLP system.

Converts natural language operator commands into structured action
dictionaries using LLM-based or rule-based parsing.
"""

import logging
from typing import Any, Dict, List, Optional

try:
    from langchain_openai import ChatOpenAI  # noqa: F401

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class CommandParser:
    """Natural language command parser for robot control.

    Parses free-text operator commands into structured dictionaries
    containing intent, action, target object, location, and confidence.

    Args:
        llm_config: Optional LLM configuration dictionary.
    """

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the command parser."""
        self._logger = logging.getLogger("rag7.nlp.parser")
        self._llm_config = llm_config or {}
        self._llm = None

        if LANGCHAIN_AVAILABLE and self._llm_config.get("provider") == "openai":
            self._try_init_llm()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse a natural language command into a structured dict.

        Args:
            text: Raw operator input string.

        Returns:
            Dictionary with keys:
                - ``intent``: Detected intent string.
                - ``action``: Primary action word.
                - ``target_object``: Detected object target (or None).
                - ``location``: Detected location (or None).
                - ``confidence``: Parser confidence in [0, 1].
        """
        if self._llm is not None:
            try:
                return self._llm_parse(text)
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("LLM parse failed: %s", exc)

        return self._rule_based_parse(text)

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from a command string.

        Args:
            text: Raw operator input string.

        Returns:
            Dictionary with detected entity types as keys.
        """
        words = text.lower().split()
        entities: Dict[str, Any] = {
            "objects": [],
            "locations": [],
            "actions": [],
            "numbers": [],
        }

        # Object keywords
        object_words = ["box", "bottle", "cup", "chair", "door", "robot", "object", "item"]
        for word in words:
            clean = word.strip(".,!?")
            if clean in object_words:
                entities["objects"].append(clean)
            elif clean.lstrip("-").replace(".", "").isdigit():
                entities["numbers"].append(float(clean))

        # Location prepositions
        location_preps = {"to", "at", "towards", "near", "beside", "on", "in"}
        for i, word in enumerate(words):
            if word in location_preps and i + 1 < len(words):
                entities["locations"].append(words[i + 1].strip(".,!?"))

        return entities

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _rule_based_parse(self, text: str) -> Dict[str, Any]:
        """Keyword-based fallback parser.

        Args:
            text: Raw operator input string.

        Returns:
            Structured command dictionary.
        """
        from nlp.intent_classifier import IntentClassifier

        classifier = IntentClassifier()
        intent = classifier.classify(text)
        entities = self.extract_entities(text)
        target_object = entities["objects"][0] if entities["objects"] else None
        location = entities["locations"][0] if entities["locations"] else None

        return {
            "intent": intent,
            "action": intent,
            "target_object": target_object,
            "location": location,
            "confidence": 0.65,
        }

    def _llm_parse(self, text: str) -> Dict[str, Any]:
        """Parse command using LLM backend."""
        import json

        prompt = (
            f"Parse this robot command into JSON with fields "
            f"intent, action, target_object, location, confidence:\n'{text}'"
        )
        response = self._llm.invoke(prompt)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._rule_based_parse(text)

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
            self._logger.warning("CommandParser LLM init failed: %s", exc)
