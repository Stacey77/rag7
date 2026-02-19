"""GPT-based text generation (simulated with template/Markov approach)."""
from __future__ import annotations

import logging
import random
import re
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 200
    temperature: float = 0.7          # 0=deterministic, 1=creative
    top_k: int = 50
    top_p: float = 0.9
    repetition_penalty: float = 1.2
    stop_sequences: List[str] = field(default_factory=list)
    style: str = "neutral"            # "formal" | "casual" | "technical" | "neutral"


@dataclass
class GenerationResult:
    """Result of a text generation request."""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = ""
    generated_text: str = ""
    tokens_generated: int = 0
    finish_reason: str = "length"    # "length" | "stop_sequence" | "complete"
    model: str = "gpt-simulated"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


# Template-based generation for different styles and domains
_TEMPLATES: Dict[str, List[str]] = {
    "technical": [
        "The {subject} system operates by {verb}ing the {object} through a {adjective} pipeline. "
        "Key considerations include {consideration1} and {consideration2}.",
        "To {verb} the {subject}, you should first configure {object} with {adjective} settings. "
        "This ensures {consideration1}.",
        "The {adjective} {subject} leverages {object} to achieve {consideration1}. "
        "Performance can be improved by {consideration2}.",
    ],
    "formal": [
        "It is recommended that the {subject} be {verb}ed in accordance with {object} protocols. "
        "Furthermore, {consideration1} must be taken into account.",
        "The implementation of {adjective} {subject} requires careful attention to {object}. "
        "Stakeholders should note {consideration1}.",
    ],
    "casual": [
        "So basically, {subject} is about {verb}ing your {object} in a {adjective} way. "
        "Just remember to check {consideration1}!",
        "Hey, when you're working with {subject}, you want to {verb} the {object} properly. "
        "The {adjective} part is {consideration1}.",
    ],
    "neutral": [
        "{subject} {verb}s the {object} using {adjective} methods. {consideration1}.",
        "When {verb}ing {subject}, the {object} plays a {adjective} role. {consideration1}.",
    ],
}

_DOMAIN_VOCAB: Dict[str, Dict[str, List[str]]] = {
    "infrastructure": {
        "subject": ["cluster", "node", "service mesh", "load balancer", "container", "microservice"],
        "verb": ["deploy", "scale", "monitor", "configure", "provision", "orchestrate"],
        "object": ["infrastructure", "workloads", "traffic", "resources", "configurations"],
        "adjective": ["distributed", "highly available", "fault-tolerant", "scalable", "elastic"],
        "consideration1": ["ensure high availability", "minimize latency", "optimize resource usage"],
        "consideration2": ["implement circuit breakers", "use health checks", "set resource limits"],
    },
    "ml": {
        "subject": ["model", "training pipeline", "feature store", "inference engine"],
        "verb": ["train", "evaluate", "deploy", "fine-tune", "validate", "optimize"],
        "object": ["dataset", "hyperparameters", "model weights", "predictions"],
        "adjective": ["pre-trained", "deep learning", "gradient-boosted", "transformer-based"],
        "consideration1": ["prevent overfitting", "ensure data quality", "monitor drift"],
        "consideration2": ["use cross-validation", "implement early stopping", "log metrics"],
    },
    "general": {
        "subject": ["system", "application", "platform", "service", "component"],
        "verb": ["process", "handle", "manage", "coordinate", "execute", "implement"],
        "object": ["requests", "data", "workflows", "resources", "operations"],
        "adjective": ["robust", "efficient", "reliable", "scalable", "maintainable"],
        "consideration1": ["error handling", "performance optimization", "security best practices"],
        "consideration2": ["logging and monitoring", "testing coverage", "documentation"],
    },
}


class MarkovChainGenerator:
    """Simple bigram Markov chain text generator trained on input corpus."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        self._start_tokens: List[str] = []
        self._rng = random.Random(seed)

    def train(self, texts: List[str], n: int = 2) -> None:
        for text in texts:
            tokens = text.split()
            if len(tokens) < n + 1:
                continue
            self._start_tokens.append(tokens[0])
            for i in range(len(tokens) - n):
                key = tuple(tokens[i:i + n])
                self._chain[key].append(tokens[i + n])
        logger.debug("MarkovChain trained: %d states", len(self._chain))

    def generate(self, max_tokens: int = 50, seed_token: Optional[str] = None) -> str:
        if not self._chain:
            return ""
        keys = list(self._chain.keys())
        if seed_token:
            matching = [k for k in keys if seed_token.lower() in " ".join(k).lower()]
            start = self._rng.choice(matching) if matching else self._rng.choice(keys)
        else:
            start = self._rng.choice(keys)

        tokens = list(start)
        for _ in range(max_tokens - len(start)):
            key = tuple(tokens[-len(start):])
            candidates = self._chain.get(key)
            if not candidates:
                break
            tokens.append(self._rng.choice(candidates))
        return " ".join(tokens)


class TemplateGenerator:
    """Template-based generation for structured content."""

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)

    def generate(self, style: str = "neutral", domain: str = "general",
                 context: Optional[Dict[str, str]] = None) -> str:
        templates = _TEMPLATES.get(style, _TEMPLATES["neutral"])
        template = self._rng.choice(templates)
        vocab = _DOMAIN_VOCAB.get(domain, _DOMAIN_VOCAB["general"])

        substitutions = context or {}
        for key, options in vocab.items():
            if key not in substitutions:
                substitutions[key] = self._rng.choice(options)
        return _fill_safe(template, substitutions)


def _fill_safe(template: str, subs: Dict[str, str]) -> str:
    try:
        return template.format(**subs)
    except KeyError:
        return template


class TextGenerator:
    """
    Simulated GPT-style text generator combining template and
    Markov chain approaches with configurable style and domain.
    """

    def __init__(self) -> None:
        self._template_gen = TemplateGenerator()
        self._markov_gen = MarkovChainGenerator()
        self._is_trained = False
        self._corpus: List[str] = []
        logger.info("TextGenerator initialized")

    def load_corpus(self, texts: List[str]) -> None:
        """Pre-train Markov chain on a corpus."""
        self._corpus.extend(texts)
        self._markov_gen.train(self._corpus)
        self._is_trained = True
        logger.info("Corpus loaded: %d documents", len(self._corpus))

    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> GenerationResult:
        if config is None:
            config = GenerationConfig()

        domain = self._infer_domain(prompt)

        # Use Markov if trained and temperature > 0.5, else templates
        if self._is_trained and config.temperature > 0.5:
            seed_word = prompt.split()[0] if prompt.split() else None
            text = self._markov_gen.generate(max_tokens=config.max_tokens // 5, seed_token=seed_word)
            if not text:
                text = self._template_gen.generate(config.style, domain)
        else:
            text = self._template_gen.generate(config.style, domain)

        # Apply stop sequences
        finish_reason = "length"
        for stop_seq in config.stop_sequences:
            if stop_seq in text:
                text = text[:text.index(stop_seq)]
                finish_reason = "stop_sequence"
                break

        tokens = len(text.split())
        return GenerationResult(
            prompt=prompt,
            generated_text=text,
            tokens_generated=tokens,
            finish_reason=finish_reason,
            metadata={"domain": domain, "style": config.style, "temperature": config.temperature},
        )

    def complete(self, text: str, n_completions: int = 3) -> List[str]:
        """Generate multiple completions for the same prompt."""
        return [self.generate(text).generated_text for _ in range(n_completions)]

    def _infer_domain(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["cluster", "kubernetes", "docker", "server", "deploy"]):
            return "infrastructure"
        if any(w in text_lower for w in ["model", "train", "dataset", "ml", "accuracy"]):
            return "ml"
        return "general"
