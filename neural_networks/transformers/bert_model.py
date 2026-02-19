"""BERT model simulation for text understanding tasks."""
from __future__ import annotations
import math
import logging
import hashlib
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class BERTConfig:
    vocab_size: int = 30522
    hidden_size: int = 128
    num_heads: int = 4
    num_layers: int = 2
    max_position: int = 512
    dropout: float = 0.1
    mask_token: str = "[MASK]"
    cls_token: str = "[CLS]"
    sep_token: str = "[SEP]"


class BERTEmbedding:
    def __init__(self, config: BERTConfig) -> None:
        self.config = config

    def tokenize(self, text: str) -> List[int]:
        tokens = [self.config.cls_token] + text.lower().split() + [self.config.sep_token]
        return [int(hashlib.md5(t.encode()).hexdigest(), 16) % self.config.vocab_size for t in tokens]

    def positional_encoding(self, length: int) -> List[List[float]]:
        pe: List[List[float]] = []
        for pos in range(length):
            row = []
            for i in range(self.config.hidden_size):
                angle = pos / (10000 ** (2 * (i // 2) / self.config.hidden_size))
                row.append(math.sin(angle) if i % 2 == 0 else math.cos(angle))
            pe.append(row)
        return pe

    def embed(self, token_ids: List[int]) -> List[List[float]]:
        pe = self.positional_encoding(len(token_ids))
        embeddings = []
        for idx, tid in enumerate(token_ids):
            vec = [(math.sin(tid * (i + 1) * 0.01) + pe[idx][i]) / 2.0
                   for i in range(self.config.hidden_size)]
            embeddings.append(vec)
        return embeddings


class BERTAttention:
    def __init__(self, config: BERTConfig) -> None:
        self.config = config

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) + 1e-9
        nb = math.sqrt(sum(x * x for x in b)) + 1e-9
        return dot / (na * nb)

    def attend(self, embeddings: List[List[float]]) -> List[List[float]]:
        n = len(embeddings)
        output = []
        for i in range(n):
            scores = [self._cosine(embeddings[i], embeddings[j]) for j in range(n)]
            max_s = max(scores)
            exp_scores = [math.exp(s - max_s) for s in scores]
            total = sum(exp_scores) + 1e-9
            weights = [e / total for e in exp_scores]
            attended = [sum(weights[j] * embeddings[j][d] for j in range(n))
                        for d in range(self.config.hidden_size)]
            output.append(attended)
        return output


class BERTEncoder:
    def __init__(self, config: BERTConfig) -> None:
        self.layers = [BERTAttention(config) for _ in range(config.num_layers)]

    def encode(self, embeddings: List[List[float]]) -> List[List[float]]:
        h = embeddings
        for layer in self.layers:
            h = layer.attend(h)
        return h


class BERTModel:
    def __init__(self, config: Optional[BERTConfig] = None) -> None:
        self.config = config or BERTConfig()
        self.embedding = BERTEmbedding(self.config)
        self.encoder = BERTEncoder(self.config)
        logger.info("BERTModel initialised with config: %s", self.config)

    def _forward(self, text: str) -> List[List[float]]:
        token_ids = self.embedding.tokenize(text)
        embeds = self.embedding.embed(token_ids)
        return self.encoder.encode(embeds)

    def encode(self, text: str) -> List[float]:
        logger.debug("Encoding text of length %d", len(text))
        hidden = self._forward(text)
        cls_vec = hidden[0]
        norm = math.sqrt(sum(x * x for x in cls_vec)) + 1e-9
        return [x / norm for x in cls_vec]

    def classify(self, text: str, labels: List[str]) -> Tuple[str, float]:
        logger.debug("Classifying text into %d labels", len(labels))
        text_vec = self.encode(text)
        best_label, best_score = labels[0], -1.0
        for label in labels:
            label_vec = self.encode(label)
            score = sum(a * b for a, b in zip(text_vec, label_vec))
            if score > best_score:
                best_score, best_label = score, label
        confidence = (best_score + 1) / 2.0
        logger.info("Classified as '%s' with confidence %.4f", best_label, confidence)
        return best_label, confidence

    def batch_encode(self, texts: List[str]) -> List[List[float]]:
        logger.debug("Batch encoding %d texts", len(texts))
        return [self.encode(t) for t in texts]

    def fill_mask(self, text_with_mask: str) -> Dict[str, float]:
        logger.debug("fill_mask called")
        words = text_with_mask.split()
        mask_idx = next((i for i, w in enumerate(words)
                         if w == self.config.mask_token), None)
        if mask_idx is None:
            logger.warning("No [MASK] token found")
            return {}
        candidates = [w for w in words if w != self.config.mask_token][:5] or ["unknown"]
        scores: Dict[str, float] = {}
        for cand in candidates:
            test = words.copy()
            test[mask_idx] = cand
            vec = self.encode(" ".join(test))
            scores[cand] = round((sum(vec) + len(vec)) / (2 * len(vec)), 4)
        total = sum(scores.values()) + 1e-9
        return {k: round(v / total, 4) for k, v in scores.items()}
