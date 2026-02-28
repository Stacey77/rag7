"""Cross-domain knowledge transfer module."""
from __future__ import annotations

import logging
import math
import statistics
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class DomainKnowledge:
    """Encapsulates knowledge learned in a specific domain."""
    domain_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain_name: str = ""
    features: Dict[str, float] = field(default_factory=dict)       # feature weights
    rules: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    performance: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TransferConfig:
    """Configuration for a transfer learning operation."""
    source_domain: str = ""
    target_domain: str = ""
    transfer_ratio: float = 0.5       # how much source knowledge to transfer
    freeze_layers: bool = False
    fine_tune_steps: int = 10
    similarity_threshold: float = 0.3  # minimum similarity to transfer


@dataclass
class TransferResult:
    """Outcome of a transfer learning operation."""
    transfer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_domain: str = ""
    target_domain: str = ""
    transferred_features: Dict[str, float] = field(default_factory=dict)
    similarity_score: float = 0.0
    improvement: float = 0.0
    steps_taken: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


def _feature_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    """Jaccard-weighted similarity between two feature dictionaries."""
    all_keys = set(a) | set(b)
    if not all_keys:
        return 0.0
    common_keys = set(a) & set(b)
    if not common_keys:
        return 0.0
    weight_sim = sum(
        1.0 - abs(a[k] - b[k]) / (max(abs(a[k]), abs(b[k])) + 1e-9)
        for k in common_keys
    ) / len(all_keys)
    jaccard = len(common_keys) / len(all_keys)
    return (jaccard + weight_sim) / 2.0


class FeatureAligner:
    """Aligns feature spaces between source and target domains."""

    def align(self, source_features: Dict[str, float],
              target_features: Dict[str, float],
              transfer_ratio: float) -> Dict[str, float]:
        """
        Produce aligned features by blending source into target.
        Features existing in target are kept; new features from source are added at reduced weight.
        """
        aligned = dict(target_features)
        for key, value in source_features.items():
            if key in aligned:
                # Blend existing feature
                aligned[key] = aligned[key] * (1 - transfer_ratio) + value * transfer_ratio
            else:
                # Import new feature at reduced weight
                aligned[key] = value * transfer_ratio * 0.5
        return aligned


class DomainAdapter:
    """Adapts source domain knowledge to a target domain via fine-tuning simulation."""

    def __init__(self, fine_tune_steps: int = 10, lr: float = 0.1) -> None:
        self.fine_tune_steps = fine_tune_steps
        self.lr = lr

    def fine_tune(self, transferred: Dict[str, float],
                  target_examples: List[Dict[str, Any]]) -> Tuple[Dict[str, float], int]:
        """
        Simulate fine-tuning by nudging feature weights towards
        the centroid of target domain examples.
        """
        if not target_examples:
            return transferred, 0

        # Compute target centroid
        all_keys = set(k for ex in target_examples for k in ex.get("features", {}))
        centroid: Dict[str, float] = {
            k: statistics.mean(ex.get("features", {}).get(k, 0.0) for ex in target_examples)
            for k in all_keys
        }
        adapted = dict(transferred)
        for step in range(self.fine_tune_steps):
            grad_norm = 0.0
            for k in all_keys:
                target_v = centroid.get(k, 0.0)
                current_v = adapted.get(k, 0.0)
                delta = self.lr * (target_v - current_v)
                adapted[k] = current_v + delta
                grad_norm += delta ** 2
            if math.sqrt(grad_norm) < 1e-4:
                return adapted, step + 1
        return adapted, self.fine_tune_steps


class TransferLearning:
    """
    Cross-domain knowledge transfer system.
    Supports domain registration, similarity computation,
    feature alignment, and fine-tuning-based adaptation.
    """

    def __init__(self) -> None:
        self._domains: Dict[str, DomainKnowledge] = {}
        self._transfer_history: List[TransferResult] = []
        self.aligner = FeatureAligner()
        self.adapter = DomainAdapter()
        logger.info("TransferLearning system initialized")

    def register_domain(self, domain_name: str, features: Optional[Dict[str, float]] = None,
                        rules: Optional[List[str]] = None) -> DomainKnowledge:
        dk = DomainKnowledge(domain_name=domain_name, features=features or {},
                             rules=rules or [])
        self._domains[domain_name] = dk
        logger.debug("Registered domain '%s'", domain_name)
        return dk

    def update_domain(self, domain_name: str, new_features: Dict[str, float],
                      performance: float = 0.0) -> bool:
        dk = self._domains.get(domain_name)
        if not dk:
            return False
        lr = 0.1
        for k, v in new_features.items():
            dk.features[k] = dk.features.get(k, v) * (1 - lr) + v * lr
        dk.performance = performance
        dk.updated_at = datetime.utcnow()
        return True

    def domain_similarity(self, source: str, target: str) -> float:
        """Compute feature similarity between two registered domains."""
        src = self._domains.get(source)
        tgt = self._domains.get(target)
        if not src or not tgt:
            return 0.0
        return _feature_similarity(src.features, tgt.features)

    def transfer(self, config: TransferConfig,
                 target_examples: Optional[List[Dict[str, Any]]] = None) -> TransferResult:
        """
        Transfer knowledge from source domain to target domain.
        """
        source_dk = self._domains.get(config.source_domain)
        target_dk = self._domains.get(config.target_domain)

        if not source_dk:
            logger.warning("Source domain '%s' not found", config.source_domain)
            return TransferResult(source_domain=config.source_domain,
                                  target_domain=config.target_domain, similarity_score=0.0)

        sim = self.domain_similarity(config.source_domain, config.target_domain) if target_dk else 0.0
        if sim < config.similarity_threshold and target_dk:
            logger.info("Similarity %.2f below threshold %.2f; skipping transfer",
                        sim, config.similarity_threshold)
            return TransferResult(source_domain=config.source_domain,
                                  target_domain=config.target_domain,
                                  similarity_score=sim,
                                  metadata={"skipped": True, "reason": "low_similarity"})

        target_features = target_dk.features if target_dk else {}
        aligned = self.aligner.align(source_dk.features, target_features, config.transfer_ratio)

        steps = 0
        if target_examples and not config.freeze_layers:
            aligned, steps = self.adapter.fine_tune(aligned, target_examples)

        if not target_dk:
            target_dk = self.register_domain(config.target_domain, aligned)
        else:
            target_dk.features = aligned
            target_dk.updated_at = datetime.utcnow()

        # Simulate improvement
        improvement = max(0.0, sim * config.transfer_ratio * (1 + steps * 0.01))

        result = TransferResult(
            source_domain=config.source_domain,
            target_domain=config.target_domain,
            transferred_features=aligned,
            similarity_score=sim,
            improvement=improvement,
            steps_taken=steps,
            metadata={"transfer_ratio": config.transfer_ratio, "fine_tune_steps": steps},
        )
        self._transfer_history.append(result)
        logger.info("Transferred from '%s' to '%s': sim=%.2f, improvement=%.2f",
                    config.source_domain, config.target_domain, sim, improvement)
        return result

    def auto_transfer(self, target_domain: str,
                      target_examples: Optional[List[Dict[str, Any]]] = None) -> List[TransferResult]:
        """Automatically find the most similar source domain and transfer."""
        scores = {
            name: _feature_similarity(dk.features, self._domains.get(target_domain, DomainKnowledge()).features)
            for name, dk in self._domains.items()
            if name != target_domain
        }
        if not scores:
            return []
        best_source = max(scores, key=lambda n: scores[n])
        config = TransferConfig(
            source_domain=best_source,
            target_domain=target_domain,
            transfer_ratio=0.4,
            similarity_threshold=0.1,
        )
        return [self.transfer(config, target_examples)]

    def get_transfer_history(self, domain: Optional[str] = None) -> List[TransferResult]:
        if domain:
            return [r for r in self._transfer_history
                    if r.source_domain == domain or r.target_domain == domain]
        return list(self._transfer_history)

    def list_domains(self) -> List[str]:
        return list(self._domains.keys())

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "registered_domains": len(self._domains),
            "total_transfers": len(self._transfer_history),
            "domain_names": self.list_domains(),
        }
