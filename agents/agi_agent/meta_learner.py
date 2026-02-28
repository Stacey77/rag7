"""Adaptive meta-learning system that learns from limited examples."""
from __future__ import annotations

import logging
import math
import random
import statistics
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Example:
    """A labeled example for meta-learning."""
    example_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    features: Dict[str, float] = field(default_factory=dict)
    label: str = ""
    domain: str = "general"
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Task:
    """A few-shot learning task."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    support_set: List[Example] = field(default_factory=list)   # labeled examples
    query_set: List[Example] = field(default_factory=list)     # to predict
    domain: str = "general"
    n_way: int = 2
    k_shot: int = 5


@dataclass
class MetaLearningResult:
    """Outcome of a meta-learning inference."""
    task_id: str = ""
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    accuracy: float = 0.0
    adaptation_steps: int = 0
    domain: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


def _cosine_similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a) | set(b)
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    mag_a = math.sqrt(sum(v ** 2 for v in a.values()))
    mag_b = math.sqrt(sum(v ** 2 for v in b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def _euclidean_distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a) | set(b)
    return math.sqrt(sum((a.get(k, 0.0) - b.get(k, 0.0)) ** 2 for k in keys))


class PrototypicalNetwork:
    """
    Simulates prototypical networks: computes class prototypes from
    support examples and classifies queries by nearest prototype.
    """

    def __init__(self) -> None:
        self.prototypes: Dict[str, Dict[str, float]] = {}

    def fit(self, support_set: List[Example]) -> None:
        class_features: Dict[str, List[Dict[str, float]]] = defaultdict(list)
        for ex in support_set:
            class_features[ex.label].append(ex.features)
        for label, feats_list in class_features.items():
            all_keys = set(k for f in feats_list for k in f)
            proto = {k: statistics.mean(f.get(k, 0.0) for f in feats_list) for k in all_keys}
            self.prototypes[label] = proto
        logger.debug("Fitted %d prototypes", len(self.prototypes))

    def predict(self, query_features: Dict[str, float]) -> Tuple[str, float]:
        if not self.prototypes:
            return "unknown", 0.0
        distances = {
            label: _euclidean_distance(query_features, proto)
            for label, proto in self.prototypes.items()
        }
        best_label = min(distances, key=lambda l: distances[l])
        max_dist = max(distances.values()) if len(distances) > 1 else 1.0
        confidence = 1.0 - (distances[best_label] / (max_dist + 1e-9))
        return best_label, confidence


class MAMLLearner:
    """
    Simulates MAML (Model-Agnostic Meta-Learning) with gradient-like
    parameter adaptation using iterative prototype refinement.
    """

    def __init__(self, inner_lr: float = 0.1, inner_steps: int = 5) -> None:
        self.inner_lr = inner_lr
        self.inner_steps = inner_steps
        self.meta_params: Dict[str, Dict[str, float]] = {}  # domain -> prototype offsets

    def meta_update(self, domain: str, support: List[Example]) -> int:
        """Simulate inner-loop adaptation. Returns adaptation steps used."""
        class_sums: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        class_counts: Dict[str, int] = defaultdict(int)
        for ex in support:
            for k, v in ex.features.items():
                class_sums[ex.label][k] += v
            class_counts[ex.label] += 1

        offsets: Dict[str, float] = {}
        for label, sums in class_sums.items():
            for k, total in sums.items():
                offsets[f"{label}:{k}"] = total / class_counts[label] * self.inner_lr

        existing = self.meta_params.get(domain, {})
        for key, val in offsets.items():
            existing[key] = existing.get(key, 0.0) * (1 - self.inner_lr) + val * self.inner_lr
        self.meta_params[domain] = existing
        return self.inner_steps

    def adapt(self, domain: str, query_features: Dict[str, float]) -> Dict[str, float]:
        """Apply meta-parameters to shift query features for adaptation."""
        offsets = self.meta_params.get(domain, {})
        adapted = dict(query_features)
        for key, offset in offsets.items():
            if ":" in key:
                _, feat = key.split(":", 1)
                if feat in adapted:
                    adapted[feat] += offset
        return adapted


class MetaLearner:
    """
    High-level adaptive meta-learner combining prototypical networks
    and MAML-style adaptation for few-shot learning.
    """

    def __init__(self, inner_lr: float = 0.1, inner_steps: int = 5) -> None:
        self.proto_net = PrototypicalNetwork()
        self.maml = MAMLLearner(inner_lr=inner_lr, inner_steps=inner_steps)
        self.task_history: List[Dict[str, Any]] = []
        self.domain_accuracy: Dict[str, List[float]] = defaultdict(list)
        logger.info("MetaLearner initialized")

    def fit_task(self, task: Task) -> MetaLearningResult:
        """Adapt to a task using support examples, then predict queries."""
        # Fit prototypical network from support set
        self.proto_net.fit(task.support_set)
        # MAML inner-loop adaptation
        steps = self.maml.meta_update(task.domain, task.support_set)

        predictions: List[Dict[str, Any]] = []
        correct = 0
        for ex in task.query_set:
            adapted_features = self.maml.adapt(task.domain, ex.features)
            pred_label, conf = self.proto_net.predict(adapted_features)
            predictions.append({
                "example_id": ex.example_id,
                "predicted": pred_label,
                "true": ex.label,
                "confidence": conf,
            })
            if pred_label == ex.label:
                correct += 1

        accuracy = correct / len(task.query_set) if task.query_set else 0.0
        self.domain_accuracy[task.domain].append(accuracy)

        result = MetaLearningResult(
            task_id=task.task_id,
            predictions=predictions,
            accuracy=accuracy,
            adaptation_steps=steps,
            domain=task.domain,
            metadata={"n_way": task.n_way, "k_shot": task.k_shot, "support_size": len(task.support_set)},
        )
        self.task_history.append({"task_id": task.task_id, "domain": task.domain, "accuracy": accuracy})
        logger.info("Task %s completed: accuracy=%.2f, domain=%s", task.task_id, accuracy, task.domain)
        return result

    def few_shot_classify(self, support: List[Example], queries: List[Dict[str, float]],
                          domain: str = "general") -> List[Tuple[str, float]]:
        """Convenience method for quick few-shot classification."""
        self.proto_net.fit(support)
        self.maml.meta_update(domain, support)
        results: List[Tuple[str, float]] = []
        for qf in queries:
            adapted = self.maml.adapt(domain, qf)
            label, conf = self.proto_net.predict(adapted)
            results.append((label, conf))
        return results

    def online_update(self, new_example: Example) -> None:
        """Incrementally update prototypes with a single new example."""
        existing = self.proto_net.prototypes.get(new_example.label, {})
        lr = 0.05
        for k, v in new_example.features.items():
            existing[k] = existing.get(k, v) * (1 - lr) + v * lr
        self.proto_net.prototypes[new_example.label] = existing

    def get_domain_performance(self) -> Dict[str, Dict[str, float]]:
        perf: Dict[str, Dict[str, float]] = {}
        for domain, accs in self.domain_accuracy.items():
            perf[domain] = {
                "mean_accuracy": statistics.mean(accs),
                "min_accuracy": min(accs),
                "max_accuracy": max(accs),
                "task_count": len(accs),
            }
        return perf

    def recommend_k_shot(self, domain: str) -> int:
        """Estimate optimal k-shot count based on domain history."""
        accs = self.domain_accuracy.get(domain, [])
        if not accs or statistics.mean(accs) > 0.85:
            return 3
        if statistics.mean(accs) > 0.70:
            return 5
        return 10

    @staticmethod
    def text_to_features(text: str) -> Dict[str, float]:
        """Convert text to a simple bag-of-words feature vector."""
        words = text.lower().split()
        features: Dict[str, float] = defaultdict(float)
        for word in words:
            features[word] += 1.0
        total = sum(features.values()) or 1.0
        return {k: v / total for k, v in features.items()}
