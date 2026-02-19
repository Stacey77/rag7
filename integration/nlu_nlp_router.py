"""Route NLP/NLU requests and expose lightweight intent, entity, and text pipelines."""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Intent patterns (regex-based lightweight NLU)
# ------------------------------------------------------------------
INTENT_PATTERNS: Dict[str, List[str]] = {
    "question": [r"\?$", r"^(what|who|where|when|why|how|which|is|are|do|does|can|could|would)\b"],
    "command": [r"^(please\s+)?(show|tell|give|find|list|create|delete|update|run|start|stop|get)\b"],
    "sentiment_feedback": [r"\b(love|hate|like|dislike|great|terrible|good|bad|awful|amazing)\b"],
    "help_request": [r"\b(help|assist|support|guide|explain|how to|what is)\b"],
    "greeting": [r"^(hi|hello|hey|good morning|good afternoon|good evening|greetings)\b"],
    "farewell": [r"^(bye|goodbye|see you|take care|thanks|thank you|cheers)\b"],
    "complaint": [r"\b(broken|not working|error|bug|issue|problem|fail|crash|wrong)\b"],
    "confirmation": [r"^(yes|no|ok|okay|sure|of course|absolutely|correct|right|wrong)\b"],
}

ENTITY_PATTERNS: Dict[str, re.Pattern] = {
    "email": re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    "url": re.compile(r"https?://[^\s]+"),
    "number": re.compile(r"\b\d+(?:\.\d+)?\b"),
    "date": re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+ \d{1,2},? \d{4})\b"),
    "mention": re.compile(r"@\w+"),
    "hashtag": re.compile(r"#\w+"),
}

NLU_TASKS = {"intent", "entity", "sentiment"}
NLP_TASKS = {"generate", "summarize", "translate", "qa"}


@dataclass
class RoutingDecision:
    """The result of routing a text request."""
    pipeline: str          # "nlu" or "nlp"
    task: str
    confidence: float
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class NLUNLPRouter:
    """Classify and route text to the NLU or NLP pipeline."""

    def __init__(self) -> None:
        self._intent_compiled = [
            (intent, [re.compile(p, re.IGNORECASE) for p in patterns])
            for intent, patterns in INTENT_PATTERNS.items()
        ]
        logger.info("NLUNLPRouter initialised.")

    def classify_request_type(self, text: str) -> str:
        """Return the primary request type string from INTENT_PATTERNS keys."""
        scores: Dict[str, int] = {}
        for intent, patterns in self._intent_compiled:
            hits = sum(1 for p in patterns if p.search(text))
            if hits:
                scores[intent] = hits
        return max(scores, key=lambda k: scores[k]) if scores else "statement"

    def route(self, text: str, context: Optional[Dict] = None) -> RoutingDecision:
        """Decide whether the text should go to NLU or NLP and specify the task."""
        context = context or {}
        request_type = self.classify_request_type(text)
        word_count = len(text.split())

        # Long text → NLP (summarization / generation)
        if word_count > 80:
            return RoutingDecision(pipeline="nlp", task="summarize",
                                   confidence=0.82, reasoning="Long text → summarization pipeline.")

        # Explicit task hint from context
        if context.get("task") in NLP_TASKS:
            return RoutingDecision(pipeline="nlp", task=context["task"],
                                   confidence=0.95, reasoning="Explicit task in context.")

        if request_type in ("question", "help_request", "command"):
            return RoutingDecision(pipeline="nlu", task="intent",
                                   confidence=0.88, reasoning=f"Request type '{request_type}' → NLU.")

        if request_type == "sentiment_feedback":
            return RoutingDecision(pipeline="nlu", task="sentiment",
                                   confidence=0.85, reasoning="Sentiment feedback → NLU.")

        return RoutingDecision(pipeline="nlu", task="entity",
                               confidence=0.65, reasoning="Default → NLU entity extraction.")

    def nlu_pipeline(self, text: str) -> Dict[str, Any]:
        """Run intent detection, entity extraction, and sentiment analysis."""
        intent = self.classify_request_type(text)
        entities: Dict[str, List[str]] = {}
        for label, pattern in ENTITY_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                entities[label] = matches

        # Naive sentiment: count positive/negative words
        positive = len(re.findall(r"\b(good|great|love|excellent|amazing|happy|yes|thanks)\b", text, re.I))
        negative = len(re.findall(r"\b(bad|terrible|hate|error|broken|fail|wrong|no)\b", text, re.I))
        if positive > negative:
            sentiment, sentiment_score = "positive", round(min(positive / 5, 1.0), 2)
        elif negative > positive:
            sentiment, sentiment_score = "negative", round(-min(negative / 5, 1.0), 2)
        else:
            sentiment, sentiment_score = "neutral", 0.0

        return {"intent": intent, "entities": entities,
                "sentiment": sentiment, "sentiment_score": sentiment_score}

    def nlp_pipeline(self, text: str, task: str = "summarize") -> Dict[str, Any]:
        """Run a basic NLP task: summarize, generate, translate stub, or QA stub."""
        if task == "summarize":
            sentences = re.split(r"(?<=[.!?])\s+", text.strip())
            summary = " ".join(sentences[:2]) if len(sentences) > 2 else text
            return {"task": "summarize", "output": summary, "input_length": len(text.split())}

        if task == "generate":
            continuation = text.strip().rstrip(".") + " — and that opens exciting new possibilities."
            return {"task": "generate", "output": continuation}

        if task == "translate":
            return {"task": "translate", "output": f"[Translation placeholder for: {text[:60]}...]",
                    "note": "Integrate an external translation API for real translation."}

        if task == "qa":
            return {"task": "qa", "output": f"Based on the context, the answer relates to: {text[:80]}",
                    "confidence": 0.5}

        return {"task": task, "output": text, "note": "Unknown NLP task — returning input unchanged."}
