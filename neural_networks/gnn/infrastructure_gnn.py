"""Graph Neural Network for infrastructure topology analysis."""
from __future__ import annotations
import math
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class InfraNode:
    node_id: str
    node_type: str  # server, pod, service, database, gateway
    features: List[float] = field(default_factory=lambda: [0.0] * 8)
    cpu_util: float = 0.0
    memory_util: float = 0.0
    error_rate: float = 0.0
    latency_ms: float = 0.0


@dataclass
class InfraEdge:
    src: str
    dst: str
    weight: float = 1.0
    bandwidth_mbps: float = 1000.0
    latency_ms: float = 1.0


class GNNLayer:
    """Single message-passing layer: averages neighbour features."""

    def __init__(self, feature_dim: int = 8) -> None:
        self.feature_dim = feature_dim

    def forward(self, nodes: Dict[str, InfraNode],
                adj: Dict[str, List[str]]) -> Dict[str, List[float]]:
        updated: Dict[str, List[float]] = {}
        for nid, node in nodes.items():
            neighbours = adj.get(nid, [])
            if neighbours:
                agg = [0.0] * self.feature_dim
                for nb_id in neighbours:
                    nb = nodes[nb_id]
                    for i, f in enumerate(nb.features[:self.feature_dim]):
                        agg[i] += f
                agg = [a / len(neighbours) for a in agg]
                combined = [math.tanh(node.features[i] + agg[i])
                            for i in range(self.feature_dim)]
            else:
                combined = [math.tanh(f) for f in node.features[:self.feature_dim]]
            updated[nid] = combined
        return updated


class InfrastructureGNN:
    def __init__(self, feature_dim: int = 8, num_layers: int = 2) -> None:
        self.feature_dim = feature_dim
        self.nodes: Dict[str, InfraNode] = {}
        self.edges: List[InfraEdge] = []
        self.adj: Dict[str, List[str]] = {}
        self.layers = [GNNLayer(feature_dim) for _ in range(num_layers)]
        logger.info("InfrastructureGNN initialised with %d layers", num_layers)

    def add_node(self, node: InfraNode) -> None:
        if len(node.features) < self.feature_dim:
            node.features += [0.0] * (self.feature_dim - len(node.features))
        node.features[0] = node.cpu_util
        node.features[1] = node.memory_util
        node.features[2] = node.error_rate
        node.features[3] = node.latency_ms / 1000.0
        self.nodes[node.node_id] = node
        self.adj.setdefault(node.node_id, [])
        logger.debug("Added node '%s' (type=%s)", node.node_id, node.node_type)

    def add_edge(self, edge: InfraEdge) -> None:
        self.edges.append(edge)
        self.adj.setdefault(edge.src, []).append(edge.dst)
        self.adj.setdefault(edge.dst, []).append(edge.src)
        logger.debug("Added edge %s -> %s", edge.src, edge.dst)

    def forward_pass(self) -> Dict[str, List[float]]:
        logger.info("Running GNN forward pass over %d nodes", len(self.nodes))
        node_features = {nid: list(n.features[:self.feature_dim])
                         for nid, n in self.nodes.items()}
        for layer in self.layers:
            node_features = layer.forward(self.nodes, self.adj)
            for nid, feats in node_features.items():
                self.nodes[nid].features = feats
        return node_features

    def detect_bottlenecks(self) -> List[Tuple[str, float]]:
        logger.info("Detecting bottlenecks")
        self.forward_pass()
        scores = []
        for nid, node in self.nodes.items():
            degree = len(self.adj.get(nid, []))
            score = (node.cpu_util * 0.4 + node.memory_util * 0.3
                     + node.error_rate * 0.2 + (degree / (len(self.nodes) + 1e-9)) * 0.1)
            scores.append((nid, round(score, 4)))
        scores.sort(key=lambda x: -x[1])
        logger.info("Top bottleneck: %s", scores[0] if scores else "none")
        return scores

    def find_critical_paths(self, src: str, dst: str) -> List[List[str]]:
        logger.info("Finding critical paths from '%s' to '%s'", src, dst)
        if src not in self.nodes or dst not in self.nodes:
            return []
        paths: List[List[str]] = []
        queue: deque = deque([[src]])
        visited_paths: Set[str] = set()
        while queue:
            path = queue.popleft()
            current = path[-1]
            if current == dst:
                paths.append(path)
                continue
            if len(path) > len(self.nodes):
                continue
            for neighbour in self.adj.get(current, []):
                if neighbour not in path:
                    new_path = path + [neighbour]
                    key = "->".join(new_path)
                    if key not in visited_paths:
                        visited_paths.add(key)
                        queue.append(new_path)
        paths.sort(key=len)
        return paths[:3]

    def predict_failure_risk(self) -> Dict[str, float]:
        logger.info("Predicting failure risk for all nodes")
        self.forward_pass()
        risks = {}
        for nid, node in self.nodes.items():
            risk = min(1.0, node.cpu_util * 0.35 + node.memory_util * 0.35
                       + node.error_rate * 0.2 + node.latency_ms / 5000.0 * 0.1)
            risks[nid] = round(risk, 4)
        return risks
