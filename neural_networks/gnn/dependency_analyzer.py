"""Service dependency analysis using GNN-inspired graph algorithms."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class DependencyEdge:
    src: str
    dst: str
    edge_type: str = "http"  # http, grpc, db, queue
    weight: float = 1.0
    call_rate: float = 0.0   # calls per second


@dataclass
class DependencyGraph:
    services: Dict[str, Dict] = field(default_factory=dict)
    edges: List[DependencyEdge] = field(default_factory=list)
    adj_out: Dict[str, List[str]] = field(default_factory=dict)
    adj_in: Dict[str, List[str]] = field(default_factory=dict)


class DependencyAnalyzer:
    def __init__(self) -> None:
        self.graph = DependencyGraph()
        logger.info("DependencyAnalyzer initialised")

    def add_service(self, name: str, service_type: str = "microservice",
                    criticality: float = 0.5, replicas: int = 1) -> None:
        self.graph.services[name] = {
            "type": service_type,
            "criticality": criticality,
            "replicas": replicas,
        }
        self.graph.adj_out.setdefault(name, [])
        self.graph.adj_in.setdefault(name, [])
        logger.debug("Added service '%s'", name)

    def add_dependency(self, src: str, dst: str, edge_type: str = "http",
                       weight: float = 1.0, call_rate: float = 0.0) -> None:
        for svc in (src, dst):
            if svc not in self.graph.services:
                self.add_service(svc)
        edge = DependencyEdge(src=src, dst=dst, edge_type=edge_type,
                              weight=weight, call_rate=call_rate)
        self.graph.edges.append(edge)
        self.graph.adj_out[src].append(dst)
        self.graph.adj_in[dst].append(src)
        logger.debug("Added dependency %s -> %s (%s)", src, dst, edge_type)

    def analyze_impact(self, service: str) -> Dict[str, List[str]]:
        """BFS downstream and upstream impact of a service failure."""
        logger.info("Analyzing impact of '%s'", service)
        if service not in self.graph.services:
            return {"downstream": [], "upstream": []}

        def bfs(adj: Dict[str, List[str]], start: str) -> List[str]:
            visited: Set[str] = set()
            queue = deque([start])
            result = []
            while queue:
                node = queue.popleft()
                for nb in adj.get(node, []):
                    if nb not in visited:
                        visited.add(nb)
                        result.append(nb)
                        queue.append(nb)
            return result

        return {
            "downstream": bfs(self.graph.adj_out, service),
            "upstream": bfs(self.graph.adj_in, service),
        }

    def find_circular_deps(self) -> List[List[str]]:
        """DFS-based cycle detection (Tarjan-inspired)."""
        logger.info("Finding circular dependencies")
        visited: Set[str] = set()
        stack: List[str] = []
        in_stack: Set[str] = set()
        cycles: List[List[str]] = []

        def dfs(node: str) -> None:
            visited.add(node)
            stack.append(node)
            in_stack.add(node)
            for nb in self.graph.adj_out.get(node, []):
                if nb not in visited:
                    dfs(nb)
                elif nb in in_stack:
                    cycle_start = stack.index(nb)
                    cycle = stack[cycle_start:] + [nb]
                    if cycle not in cycles:
                        cycles.append(cycle)
                        logger.warning("Cycle detected: %s", " -> ".join(cycle))
            stack.pop()
            in_stack.discard(node)

        for svc in list(self.graph.services.keys()):
            if svc not in visited:
                dfs(svc)
        return cycles

    def compute_criticality_scores(self) -> Dict[str, float]:
        logger.info("Computing criticality scores")
        scores: Dict[str, float] = {}
        n = max(len(self.graph.services), 1)
        for svc in self.graph.services:
            in_degree = len(self.graph.adj_in.get(svc, []))
            out_degree = len(self.graph.adj_out.get(svc, []))
            impact = len(self.analyze_impact(svc)["downstream"])
            base = self.graph.services[svc].get("criticality", 0.5)
            score = base * 0.4 + (in_degree / n) * 0.2 + (impact / n) * 0.4
            scores[svc] = round(min(1.0, score), 4)
        return dict(sorted(scores.items(), key=lambda x: -x[1]))

    def suggest_refactoring(self) -> List[str]:
        logger.info("Generating refactoring suggestions")
        suggestions: List[str] = []
        cycles = self.find_circular_deps()
        for cycle in cycles:
            suggestions.append(
                f"Break circular dependency: {' -> '.join(cycle)}. "
                "Consider introducing an event/message queue.")
        scores = self.compute_criticality_scores()
        for svc, score in scores.items():
            in_deg = len(self.graph.adj_in.get(svc, []))
            out_deg = len(self.graph.adj_out.get(svc, []))
            if score > 0.7:
                suggestions.append(
                    f"'{svc}' is highly critical (score={score}). "
                    "Consider adding redundancy or circuit breakers.")
            if in_deg + out_deg > 6:
                suggestions.append(
                    f"'{svc}' has high coupling (in={in_deg}, out={out_deg}). "
                    "Consider splitting into smaller services.")
        if not suggestions:
            suggestions.append("No major refactoring needed. Dependency graph looks healthy.")
        return suggestions
