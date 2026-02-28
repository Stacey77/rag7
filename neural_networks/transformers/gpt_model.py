"""GPT model simulation for text generation tasks."""
from __future__ import annotations
import math
import random
import logging
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class GPTConfig:
    vocab_size: int = 50257
    hidden_size: int = 128
    num_heads: int = 4
    num_layers: int = 2
    max_tokens: int = 512
    temperature: float = 1.0
    top_k: int = 10


class GPTTokenizer:
    def __init__(self, config: GPTConfig) -> None:
        self.config = config

    def encode(self, text: str) -> List[int]:
        return [int(hashlib.md5(w.encode()).hexdigest(), 16) % self.config.vocab_size
                for w in text.lower().split()]

    def decode(self, token_ids: List[int]) -> str:
        words = []
        for tid in token_ids:
            seed = tid % 1000
            random.seed(seed)
            words.append(random.choice(["data", "model", "system", "service",
                                        "result", "output", "value", "process"]))
        return " ".join(words)

    def build_ngrams(self, text: str, n: int = 2) -> Dict[Tuple, List[str]]:
        tokens = text.lower().split()
        ngrams: Dict[Tuple, List[str]] = defaultdict(list)
        for i in range(len(tokens) - n):
            key = tuple(tokens[i:i + n])
            ngrams[key].append(tokens[i + n])
        return ngrams


class GPTAttention:
    """Causal (autoregressive) attention simulation."""

    def __init__(self, config: GPTConfig) -> None:
        self.config = config

    @staticmethod
    def _dot(a: List[float], b: List[float]) -> float:
        return sum(x * y for x, y in zip(a, b))

    def causal_attend(self, embeddings: List[List[float]]) -> List[List[float]]:
        n = len(embeddings)
        d = len(embeddings[0])
        scale = math.sqrt(d) + 1e-9
        output = []
        for i in range(n):
            scores = [self._dot(embeddings[i], embeddings[j]) / scale
                      if j <= i else -1e9 for j in range(n)]
            max_s = max(scores)
            exp_s = [math.exp(s - max_s) for s in scores]
            total = sum(exp_s) + 1e-9
            weights = [e / total for e in exp_s]
            attended = [sum(weights[j] * embeddings[j][k] for j in range(n))
                        for k in range(d)]
            output.append(attended)
        return output


class GPTModel:
    def __init__(self, config: Optional[GPTConfig] = None) -> None:
        self.config = config or GPTConfig()
        self.tokenizer = GPTTokenizer(self.config)
        self.attention_layers = [GPTAttention(self.config)
                                 for _ in range(self.config.num_layers)]
        self._ngram_cache: Dict[Tuple, List[str]] = {}
        logger.info("GPTModel initialised with config: %s", self.config)

    def _embed(self, token_ids: List[int]) -> List[List[float]]:
        return [[math.sin(tid * (i + 1) * 0.01)
                 for i in range(self.config.hidden_size)]
                for tid in token_ids]

    def _sample(self, candidates: List[str], temperature: float) -> str:
        if not candidates:
            return "the"
        if temperature <= 0:
            return candidates[0]
        scores = [math.exp(-(i * temperature)) for i in range(len(candidates))]
        total = sum(scores)
        r = random.random() * total
        cumulative = 0.0
        for cand, score in zip(candidates, scores):
            cumulative += score
            if r <= cumulative:
                return cand
        return candidates[-1]

    def generate(self, prompt: str, max_tokens: int = 50,
                 temperature: float = 1.0) -> str:
        logger.info("Generating up to %d tokens from prompt", max_tokens)
        ngrams = self.tokenizer.build_ngrams(prompt, n=2)
        self._ngram_cache.update(ngrams)
        words = prompt.lower().split()
        for _ in range(max_tokens):
            key = tuple(words[-2:]) if len(words) >= 2 else tuple(words[-1:])
            candidates = self._ngram_cache.get(key, [])
            if not candidates:
                fallback = ["the", "a", "in", "of", "and", "is", "for"]
                candidates = fallback
            next_word = self._sample(candidates[:self.config.top_k], temperature)
            words.append(next_word)
            if next_word in {".", "!", "?"}:
                break
        generated = " ".join(words[len(prompt.split()):])
        logger.debug("Generated %d tokens", len(words) - len(prompt.split()))
        return generated

    def complete(self, text: str) -> str:
        logger.debug("Completing text snippet")
        return text + " " + self.generate(text, max_tokens=20,
                                          temperature=self.config.temperature)

    def batch_generate(self, prompts: List[str], max_tokens: int = 30) -> List[str]:
        logger.info("Batch generating for %d prompts", len(prompts))
        return [self.generate(p, max_tokens) for p in prompts]
