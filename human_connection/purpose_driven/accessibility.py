"""Universal design and accessibility utilities for AI-generated text."""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List

logger = logging.getLogger(__name__)

COMPLEX_WORDS: Dict[str, str] = {
    "utilise": "use", "utilization": "use", "commence": "start",
    "terminate": "end", "ascertain": "find out", "endeavour": "try",
    "facilitate": "help", "implement": "carry out", "leverage": "use",
    "methodology": "method", "paradigm": "model", "synergy": "cooperation",
    "bandwidth": "capacity", "iterate": "repeat", "optimise": "improve",
    "mitigate": "reduce", "henceforth": "from now on", "aforementioned": "the above",
    "notwithstanding": "despite", "herein": "here", "pursuant": "following",
}

NON_INCLUSIVE_TERMS: Dict[str, str] = {
    r"\bmanpower\b": "workforce", r"\bblacklist\b": "blocklist",
    r"\bwhitelist\b": "allowlist", r"\bmaster\b": "primary",
    r"\bslave\b": "secondary", r"\bhe or she\b": "they",
    r"\bhis or her\b": "their", r"\bguy\b": "person",
    r"\bguys\b": "everyone", r"\bcrazy\b": "unexpected",
    r"\binsane\b": "unusual", r"\blame\b": "issue",
}

READING_LEVELS = {
    "simple": 6,      # ~grade 6, Flesch ≥ 70
    "standard": 10,   # ~grade 10, Flesch ≥ 50
    "technical": 14,  # ~grade 14, Flesch ≥ 30
}


@dataclass
class AccessibilityIssue:
    """A detected accessibility concern."""
    issue_type: str         # e.g. "long_sentence", "complex_word", "non_inclusive"
    description: str
    suggestion: str
    severity: str = "warning"   # "info", "warning", "error"


class AccessibilityChecker:
    """Evaluate and improve text accessibility."""

    def __init__(self) -> None:
        self._inclusive_patterns = {
            re.compile(p, re.IGNORECASE): r for p, r in NON_INCLUSIVE_TERMS.items()
        }
        logger.info("AccessibilityChecker initialised.")

    def check(self, text: str) -> List[AccessibilityIssue]:
        """Return all accessibility issues found in *text*."""
        issues: List[AccessibilityIssue] = []
        sentences = re.split(r"[.!?]+", text)
        for sentence in sentences:
            words = sentence.split()
            if len(words) > 35:
                issues.append(AccessibilityIssue(
                    "long_sentence",
                    f"Sentence has {len(words)} words.",
                    "Break it into shorter sentences (≤ 20 words each).",
                    "warning"))

        for word, replacement in COMPLEX_WORDS.items():
            if re.search(r"\b" + re.escape(word) + r"\b", text, re.IGNORECASE):
                issues.append(AccessibilityIssue(
                    "complex_word",
                    f"Complex word '{word}' found.",
                    f"Consider replacing with '{replacement}'.",
                    "info"))

        for pattern, replacement in self._inclusive_patterns.items():
            if pattern.search(text):
                issues.append(AccessibilityIssue(
                    "non_inclusive",
                    f"Non-inclusive term found matching pattern '{pattern.pattern}'.",
                    f"Consider using '{replacement}' instead.",
                    "warning"))

        return issues

    def simplify_language(self, text: str, reading_level: str = "standard") -> str:
        """Replace complex words with simpler equivalents."""
        result = text
        for word, replacement in COMPLEX_WORDS.items():
            result = re.sub(r"\b" + re.escape(word) + r"\b", replacement, result, flags=re.IGNORECASE)
        if reading_level == "simple":
            sentences = re.split(r"(?<=[.!?])\s+", result)
            simplified = []
            for sent in sentences:
                words = sent.split()
                if len(words) > 20:
                    mid = len(words) // 2
                    simplified.append(" ".join(words[:mid]) + ".")
                    simplified.append(" ".join(words[mid:]))
                else:
                    simplified.append(sent)
            result = " ".join(simplified)
        return result

    def add_alt_text_suggestions(self, text: str) -> str:
        """Append alt-text reminders after image/figure references."""
        result = re.sub(
            r"\b(image|figure|diagram|chart|graph|screenshot)\b",
            r"\1 [add descriptive alt text here]",
            text, flags=re.IGNORECASE)
        return result

    def check_readability(self, text: str) -> Dict:
        """Approximate Flesch Reading Ease and grade level."""
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        words = text.split()
        if not sentences or not words:
            return {"flesch_score": 0, "grade_level": 0, "avg_sentence_length": 0,
                    "avg_syllables_per_word": 0}

        def count_syllables(word: str) -> int:
            word = word.lower().rstrip("es ")
            return max(1, len(re.findall(r"[aeiou]+", word)))

        avg_sentence_len = len(words) / len(sentences)
        avg_syllables = sum(count_syllables(w) for w in words) / len(words)
        flesch = 206.835 - 1.015 * avg_sentence_len - 84.6 * avg_syllables
        flesch = round(max(0.0, min(100.0, flesch)), 1)
        grade = round(0.39 * avg_sentence_len + 11.8 * avg_syllables - 15.59, 1)
        return {"flesch_score": flesch, "grade_level": max(1.0, grade),
                "avg_sentence_length": round(avg_sentence_len, 1),
                "avg_syllables_per_word": round(avg_syllables, 2)}

    def make_inclusive(self, text: str) -> str:
        """Replace non-inclusive terms with inclusive alternatives."""
        result = text
        for pattern, replacement in self._inclusive_patterns.items():
            result = pattern.sub(replacement, result)
        return result
