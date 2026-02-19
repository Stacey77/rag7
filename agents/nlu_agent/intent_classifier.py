"""Deep intent classification for NLU."""
from __future__ import annotations

import logging
import math
import re
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Represents a classified intent."""
    name: str
    confidence: float = 0.0
    slots: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassificationResult:
    """Result of intent classification."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    top_intent: Optional[Intent] = None
    all_intents: List[Intent] = field(default_factory=list)
    is_ambiguous: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Predefined intent patterns and keywords
INTENT_PATTERNS: Dict[str, List[str]] = {
    "greeting": ["hello", "hi", "hey", "good morning", "good afternoon", "howdy", "greetings"],
    "farewell": ["bye", "goodbye", "see you", "take care", "later", "exit", "quit"],
    "help": ["help", "assist", "support", "how do i", "what is", "explain", "guide", "tutorial"],
    "create": ["create", "make", "build", "generate", "new", "add", "setup", "initialize"],
    "delete": ["delete", "remove", "destroy", "drop", "purge", "erase", "clean"],
    "update": ["update", "change", "modify", "edit", "set", "configure", "adjust"],
    "query": ["show", "list", "get", "find", "search", "display", "fetch", "retrieve"],
    "deploy": ["deploy", "release", "publish", "launch", "rollout", "ship"],
    "monitor": ["monitor", "watch", "track", "observe", "check", "status", "health"],
    "scale": ["scale", "resize", "increase", "decrease", "expand", "shrink", "autoscale"],
    "debug": ["debug", "troubleshoot", "fix", "diagnose", "investigate", "error", "issue"],
    "report": ["report", "analyze", "statistics", "metrics", "summary", "overview", "audit"],
    "train": ["train", "learn", "fit", "optimize", "improve", "retrain"],
    "predict": ["predict", "forecast", "infer", "estimate", "classify", "detect"],
    "confirm": ["yes", "ok", "sure", "confirm", "agree", "proceed", "go ahead"],
    "deny": ["no", "cancel", "stop", "abort", "refuse", "disagree", "never"],
}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\b\w+\b", text.lower())


def _tfidf_score(text_tokens: List[str], pattern_tokens: List[str]) -> float:
    text_counts = Counter(text_tokens)
    pattern_counts = Counter(pattern_tokens)
    score = 0.0
    for token, freq in pattern_counts.items():
        if token in text_counts:
            tf = text_counts[token] / len(text_tokens)
            idf = math.log(1 + 1.0 / freq)
            score += tf * idf
    return score


class NaiveBayesClassifier:
    """Multinomial Naive Bayes intent classifier."""

    def __init__(self) -> None:
        self.class_priors: Dict[str, float] = {}
        self.feature_likelihoods: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.vocab: set = set()

    def fit(self, examples: List[Tuple[str, str]]) -> None:
        """Train on (text, intent_label) pairs."""
        class_counts: Dict[str, int] = Counter()
        class_features: Dict[str, Counter] = defaultdict(Counter)
        for text, label in examples:
            tokens = _tokenize(text)
            class_counts[label] += 1
            class_features[label].update(tokens)
            self.vocab.update(tokens)

        total = sum(class_counts.values()) or 1
        self.class_priors = {c: count / total for c, count in class_counts.items()}

        vocab_size = len(self.vocab)
        for label, feat_counts in class_features.items():
            total_tokens = sum(feat_counts.values())
            for token in self.vocab:
                # Laplace smoothing
                self.feature_likelihoods[label][token] = (
                    feat_counts.get(token, 0) + 1
                ) / (total_tokens + vocab_size)
        logger.debug("NaiveBayes fitted on %d examples, %d classes", len(examples), len(class_counts))

    def predict_proba(self, text: str) -> Dict[str, float]:
        tokens = _tokenize(text)
        log_probs: Dict[str, float] = {}
        for label, prior in self.class_priors.items():
            log_p = math.log(prior + 1e-9)
            for token in tokens:
                if token in self.vocab:
                    log_p += math.log(self.feature_likelihoods[label].get(token, 1e-9))
            log_probs[label] = log_p

        # Softmax normalization
        max_log = max(log_probs.values())
        exp_probs = {l: math.exp(v - max_log) for l, v in log_probs.items()}
        total = sum(exp_probs.values()) or 1.0
        return {l: v / total for l, v in exp_probs.items()}


class PatternMatcher:
    """Rule-based intent classifier using keyword patterns."""

    def __init__(self, patterns: Optional[Dict[str, List[str]]] = None) -> None:
        self.patterns = patterns or INTENT_PATTERNS

    def score(self, text: str) -> Dict[str, float]:
        tokens = _tokenize(text)
        scores: Dict[str, float] = {}
        for intent, keywords in self.patterns.items():
            pattern_tokens = _tokenize(" ".join(keywords))
            scores[intent] = _tfidf_score(tokens, Counter(pattern_tokens))
        total = sum(scores.values()) or 1.0
        return {k: v / total for k, v in scores.items()}


class IntentClassifier:
    """
    Hybrid intent classifier combining Naive Bayes (learned) and pattern matching (rule-based).
    Falls back to pattern matching when insufficient training data is available.
    """

    def __init__(self, confidence_threshold: float = 0.3, ambiguity_margin: float = 0.1) -> None:
        self.confidence_threshold = confidence_threshold
        self.ambiguity_margin = ambiguity_margin
        self._nb = NaiveBayesClassifier()
        self._pattern = PatternMatcher()
        self._trained = False
        self._training_examples: List[Tuple[str, str]] = []
        logger.info("IntentClassifier initialized")

    def train(self, examples: List[Tuple[str, str]]) -> None:
        """Train on (text, intent_label) pairs."""
        self._training_examples.extend(examples)
        self._nb.fit(self._training_examples)
        self._trained = True
        logger.info("Trained on %d examples", len(self._training_examples))

    def classify(self, text: str) -> ClassificationResult:
        pattern_scores = self._pattern.score(text)

        if self._trained:
            nb_scores = self._nb.predict_proba(text)
            combined = {
                intent: 0.6 * nb_scores.get(intent, 0.0) + 0.4 * pattern_scores.get(intent, 0.0)
                for intent in set(nb_scores) | set(pattern_scores)
            }
        else:
            combined = pattern_scores

        sorted_intents = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        all_intents = [Intent(name=name, confidence=conf) for name, conf in sorted_intents]

        top_intent = all_intents[0] if all_intents else None
        is_ambiguous = (
            len(all_intents) >= 2
            and all_intents[1].confidence > (all_intents[0].confidence - self.ambiguity_margin)
        )

        result = ClassificationResult(
            text=text,
            top_intent=top_intent,
            all_intents=all_intents[:5],
            is_ambiguous=is_ambiguous,
        )
        logger.debug("Classified '%s' -> %s (%.2f)", text[:50], top_intent.name if top_intent else "none",
                     top_intent.confidence if top_intent else 0.0)
        return result

    def batch_classify(self, texts: List[str]) -> List[ClassificationResult]:
        return [self.classify(text) for text in texts]

    def add_intent_pattern(self, intent: str, keywords: List[str]) -> None:
        existing = self._pattern.patterns.get(intent, [])
        self._pattern.patterns[intent] = list(set(existing + keywords))

    def get_supported_intents(self) -> List[str]:
        return list(self._pattern.patterns.keys())

    def explain(self, result: ClassificationResult) -> str:
        lines = [f"Text: {result.text}", f"Top intent: {result.top_intent.name if result.top_intent else 'none'}"]
        if result.top_intent:
            lines.append(f"Confidence: {result.top_intent.confidence:.1%}")
        if result.is_ambiguous:
            lines.append("⚠ Ambiguous classification")
        lines.append("All intents:")
        for intent in result.all_intents[:5]:
            lines.append(f"  {intent.name}: {intent.confidence:.1%}")
        return "\n".join(lines)
