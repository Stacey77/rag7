"""T5 model simulation for sequence-to-sequence tasks."""
from __future__ import annotations
import math
import logging
import hashlib
from dataclasses import dataclass
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

_LANG_PREFIXES: Dict[str, str] = {
    "fr": "En français: ",
    "es": "En español: ",
    "de": "Auf Deutsch: ",
    "it": "In italiano: ",
}

_STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "be",
               "been", "being", "have", "has", "had", "do", "does", "did",
               "will", "would", "could", "should", "may", "might", "shall",
               "to", "of", "in", "for", "on", "with", "at", "by", "from"}


@dataclass
class T5Config:
    hidden_size: int = 128
    num_heads: int = 4
    num_encoder_layers: int = 2
    num_decoder_layers: int = 2
    max_length: int = 512
    vocab_size: int = 32128


class T5Encoder:
    def __init__(self, config: T5Config) -> None:
        self.config = config

    def _token_id(self, word: str) -> int:
        return int(hashlib.md5(word.encode()).hexdigest(), 16) % self.config.vocab_size

    def _embed(self, text: str) -> List[List[float]]:
        words = text.lower().split()
        embeddings = []
        for pos, word in enumerate(words):
            tid = self._token_id(word)
            vec = [math.sin(tid * (i + 1) * 0.01 + pos * 0.001)
                   for i in range(self.config.hidden_size)]
            embeddings.append(vec)
        return embeddings

    def encode(self, text: str) -> List[List[float]]:
        logger.debug("T5Encoder encoding %d chars", len(text))
        embeddings = self._embed(text)
        if not embeddings:
            return []
        for _ in range(self.config.num_encoder_layers):
            new_emb = []
            for i, vec in enumerate(embeddings):
                context = embeddings[max(0, i - 1): i + 2]
                avg = [sum(c[d] for c in context) / len(context)
                       for d in range(self.config.hidden_size)]
                new_emb.append([math.tanh(v + a) for v, a in zip(vec, avg)])
            embeddings = new_emb
        return embeddings

    def pool(self, encoded: List[List[float]]) -> List[float]:
        if not encoded:
            return [0.0] * self.config.hidden_size
        return [sum(row[d] for row in encoded) / len(encoded)
                for d in range(self.config.hidden_size)]


class T5Decoder:
    def __init__(self, config: T5Config) -> None:
        self.config = config

    def decode(self, encoder_output: List[float], target_hint: str) -> str:
        logger.debug("T5Decoder generating from hint: '%s'", target_hint)
        words = target_hint.lower().split()
        enriched = []
        for i, word in enumerate(words):
            score = encoder_output[i % self.config.hidden_size]
            enriched.append((word, score))
        enriched.sort(key=lambda x: -abs(x[1]))
        return " ".join(w for w, _ in enriched[:max(1, len(enriched))])


class T5Model:
    def __init__(self, config: Optional[T5Config] = None) -> None:
        self.config = config or T5Config()
        self.encoder = T5Encoder(self.config)
        self.decoder = T5Decoder(self.config)
        logger.info("T5Model initialised with config: %s", self.config)

    def translate(self, text: str, target_lang: str = "fr") -> str:
        logger.info("Translating to '%s'", target_lang)
        encoded = self.encoder.encode(text)
        pooled = self.encoder.pool(encoded)
        prefix = _LANG_PREFIXES.get(target_lang, f"[{target_lang}]: ")
        decoded = self.decoder.decode(pooled, text)
        return prefix + decoded

    def summarize(self, text: str, max_length: int = 50) -> str:
        logger.info("Summarizing text of length %d", len(text))
        encoded = self.encoder.encode(text)
        sentences = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if not sentences:
            return text[:max_length]
        pooled = self.encoder.pool(encoded)
        scored = []
        for sent in sentences:
            words = sent.lower().split()
            content_words = [w for w in words if w not in _STOP_WORDS]
            score = len(content_words) / (len(words) + 1e-9)
            sim = sum(pooled[i % self.config.hidden_size] for i in range(len(words)))
            scored.append((sent, score + abs(sim) * 0.01))
        scored.sort(key=lambda x: -x[1])
        summary = " ".join(s for s, _ in scored[:2])
        return summary[:max_length] if len(summary) > max_length else summary

    def answer_question(self, context: str, question: str) -> str:
        logger.info("Answering question from context")
        q_enc = self.encoder.pool(self.encoder.encode(question))
        sentences = [s.strip() for s in context.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if not sentences:
            return "No answer found."
        best_sent, best_score = sentences[0], -float("inf")
        for sent in sentences:
            s_enc = self.encoder.pool(self.encoder.encode(sent))
            score = sum(a * b for a, b in zip(q_enc, s_enc))
            if score > best_score:
                best_score, best_sent = score, sent
        return best_sent

    def classify(self, text: str, task: str = "sentiment") -> str:
        logger.info("Classifying text for task '%s'", task)
        pooled = self.encoder.pool(self.encoder.encode(text))
        score = sum(pooled[:self.config.hidden_size // 2])
        if task == "sentiment":
            return "positive" if score > 0 else "negative"
        if task == "topic":
            topics = ["technology", "science", "sports", "politics", "health"]
            idx = int(abs(score) * 10) % len(topics)
            return topics[idx]
        return "unknown"

    def paraphrase(self, text: str) -> str:
        logger.info("Paraphrasing text")
        encoded = self.encoder.encode(text)
        pooled = self.encoder.pool(encoded)
        words = text.split()
        paraphrased = []
        for i, word in enumerate(words):
            shift = pooled[i % self.config.hidden_size]
            paraphrased.append(word if shift > 0 else word.lower())
        return " ".join(paraphrased)
