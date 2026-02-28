"""Ethical AI validation — check text for harm, bias, privacy, and accessibility."""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List

logger = logging.getLogger(__name__)


class EthicsCategory(Enum):
    HARMFUL_CONTENT = "harmful_content"
    BIAS = "bias"
    PRIVACY = "privacy"
    ACCESSIBILITY = "accessibility"
    MISINFORMATION = "misinformation"


@dataclass
class EthicsViolation:
    """A detected ethics violation."""
    category: EthicsCategory
    description: str
    severity: float          # 0-1
    snippet: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Lexicons
# ---------------------------------------------------------------------------
HARMFUL_KEYWORDS = {
    "kill", "harm", "hurt", "attack", "destroy", "suicide", "bomb", "weapon",
    "poison", "rape", "murder", "violence", "hate", "abuse",
}

BIAS_KEYWORDS = {
    "always", "never", "all", "none", "every", "typical", "obviously",
    "naturally", "of course", "just like", "these people", "those people",
}

GENDERED_ASSUMPTIONS = {
    r"\bhe is a (doctor|engineer|ceo|manager|developer|programmer)\b",
    r"\bshe is a (nurse|secretary|cleaner|receptionist)\b",
}

# Common PII patterns
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"),
    "phone": re.compile(r"\b(\+?\d[\d\s\-().]{7,}\d)\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ \-]?){13,16}\b"),
    "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

LONG_WORD_THRESHOLD = 4   # avg words per sentence above this → complexity issue
LONG_SENTENCE_WORDS = 40  # a sentence with more words than this is flagged


class EthicsChecker:
    """Validate text against ethical AI guidelines."""

    def __init__(self) -> None:
        self._gendered_patterns = [
            re.compile(p, re.IGNORECASE) for p in GENDERED_ASSUMPTIONS
        ]
        logger.info("EthicsChecker initialised.")

    def check(self, text: str, context: Dict | None = None) -> List[EthicsViolation]:
        """Run all ethical checks and return a list of violations."""
        violations: List[EthicsViolation] = []
        if self.is_harmful(text):
            words = set(text.lower().split()) & HARMFUL_KEYWORDS
            violations.append(EthicsViolation(
                category=EthicsCategory.HARMFUL_CONTENT,
                description=f"Potentially harmful language detected: {', '.join(words)}",
                severity=0.9, snippet=text[:120]))
        if self.is_biased(text):
            violations.append(EthicsViolation(
                category=EthicsCategory.BIAS,
                description="Absolute / stereotyping language found.",
                severity=0.6, snippet=text[:120]))
        if not self.is_privacy_safe(text):
            violations.append(EthicsViolation(
                category=EthicsCategory.PRIVACY,
                description="Potential PII or sensitive data exposure.",
                severity=0.85, snippet="[redacted]"))
        if not self.is_accessible(text):
            violations.append(EthicsViolation(
                category=EthicsCategory.ACCESSIBILITY,
                description="Text may be too complex or contain long sentences.",
                severity=0.4, snippet=text[:80]))
        return violations

    def is_harmful(self, text: str) -> bool:
        """Return True if harmful keywords are present."""
        words = set(text.lower().split())
        return bool(words & HARMFUL_KEYWORDS)

    def is_biased(self, text: str) -> bool:
        """Return True if absolute language or gendered assumptions are found."""
        words = set(text.lower().split())
        if words & BIAS_KEYWORDS:
            return True
        for pattern in self._gendered_patterns:
            if pattern.search(text):
                return True
        return False

    def is_privacy_safe(self, text: str) -> bool:
        """Return True when no PII patterns are detected."""
        for _label, pattern in PII_PATTERNS.items():
            if pattern.search(text):
                return False
        return True

    def is_accessible(self, text: str) -> bool:
        """Return True when the text does not contain excessively long sentences."""
        sentences = re.split(r"[.!?]+", text)
        for sentence in sentences:
            if len(sentence.split()) > LONG_SENTENCE_WORDS:
                return False
        return True

    def get_ethics_score(self, text: str) -> float:
        """Return a 0-1 ethics score (1 = fully compliant, 0 = many violations)."""
        violations = self.check(text)
        if not violations:
            return 1.0
        total_severity = sum(v.severity for v in violations)
        return round(max(0.0, 1.0 - total_severity / (len(violations) + 1)), 3)
