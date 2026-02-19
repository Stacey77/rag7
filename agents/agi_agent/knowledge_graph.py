"""Knowledge graph for context and relationship mapping."""
from __future__ import annotations

import json
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Node:
    """A node in the knowledge graph."""
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    node_type: str = "concept"
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Edge:
    """A directed edge between two nodes."""
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    relation: str = "related_to"
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GraphQuery:
    """Query specification for knowledge graph traversal."""
    start_node: Optional[str] = None
    relation_filter: Optional[str] = None
    node_type_filter: Optional[str] = None
    max_depth: int = 3
    max_results: int = 50


@dataclass
class GraphQueryResult:
    """Result of a knowledge graph query."""
    nodes: List[Node] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    paths: List[List[str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class KnowledgeGraph:
    """
    In-memory knowledge graph supporting nodes, directed edges,
    BFS/DFS traversal, shortest path, and semantic search.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Edge] = {}
        self._adj: Dict[str, List[str]] = defaultdict(list)    # node_id -> [edge_ids]
        self._rev_adj: Dict[str, List[str]] = defaultdict(list) # node_id -> [incoming edge_ids]
        self._label_index: Dict[str, Set[str]] = defaultdict(set)  # label -> node_ids
        self._type_index: Dict[str, Set[str]] = defaultdict(set)   # type -> node_ids
        logger.info("KnowledgeGraph initialized")

    # ------------------------------------------------------------------ nodes

    def add_node(self, label: str, node_type: str = "concept", properties: Optional[Dict[str, Any]] = None) -> Node:
        node = Node(label=label, node_type=node_type, properties=properties or {})
        self._nodes[node.node_id] = node
        self._label_index[label.lower()].add(node.node_id)
        self._type_index[node_type].add(node.node_id)
        logger.debug("Added node '%s' (%s)", label, node.node_id)
        return node

    def get_node(self, node_id: str) -> Optional[Node]:
        return self._nodes.get(node_id)

    def find_by_label(self, label: str) -> List[Node]:
        ids = self._label_index.get(label.lower(), set())
        return [self._nodes[nid] for nid in ids if nid in self._nodes]

    def find_by_type(self, node_type: str) -> List[Node]:
        ids = self._type_index.get(node_type, set())
        return [self._nodes[nid] for nid in ids if nid in self._nodes]

    def update_node(self, node_id: str, properties: Dict[str, Any]) -> bool:
        node = self._nodes.get(node_id)
        if not node:
            return False
        node.properties.update(properties)
        node.updated_at = datetime.utcnow()
        return True

    def remove_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        # Remove incident edges
        for eid in list(self._adj[node_id]):
            self._remove_edge_by_id(eid)
        for eid in list(self._rev_adj[node_id]):
            self._remove_edge_by_id(eid)
        node = self._nodes.pop(node_id)
        self._label_index[node.label.lower()].discard(node_id)
        self._type_index[node.node_type].discard(node_id)
        return True

    # ------------------------------------------------------------------ edges

    def add_edge(self, source_id: str, target_id: str, relation: str = "related_to",
                 weight: float = 1.0, properties: Optional[Dict[str, Any]] = None) -> Optional[Edge]:
        if source_id not in self._nodes or target_id not in self._nodes:
            logger.warning("Cannot add edge: node(s) not found")
            return None
        edge = Edge(source_id=source_id, target_id=target_id, relation=relation,
                    weight=weight, properties=properties or {})
        self._edges[edge.edge_id] = edge
        self._adj[source_id].append(edge.edge_id)
        self._rev_adj[target_id].append(edge.edge_id)
        return edge

    def _remove_edge_by_id(self, edge_id: str) -> None:
        edge = self._edges.pop(edge_id, None)
        if edge:
            self._adj[edge.source_id] = [e for e in self._adj[edge.source_id] if e != edge_id]
            self._rev_adj[edge.target_id] = [e for e in self._rev_adj[edge.target_id] if e != edge_id]

    def get_neighbors(self, node_id: str, relation: Optional[str] = None) -> List[Node]:
        neighbors: List[Node] = []
        for eid in self._adj.get(node_id, []):
            edge = self._edges.get(eid)
            if edge and (relation is None or edge.relation == relation):
                target = self._nodes.get(edge.target_id)
                if target:
                    neighbors.append(target)
        return neighbors

    # ---------------------------------------------------------------- traversal

    def bfs(self, start_id: str, max_depth: int = 3, relation: Optional[str] = None) -> GraphQueryResult:
        visited: Set[str] = set()
        queue: deque = deque([(start_id, 0, [start_id])])
        result_nodes: List[Node] = []
        result_edges: List[Edge] = []
        paths: List[List[str]] = []

        while queue:
            current_id, depth, path = queue.popleft()
            if current_id in visited or depth > max_depth:
                continue
            visited.add(current_id)
            node = self._nodes.get(current_id)
            if node:
                result_nodes.append(node)
                paths.append(path)

            if depth < max_depth:
                for eid in self._adj.get(current_id, []):
                    edge = self._edges.get(eid)
                    if edge and (relation is None or edge.relation == relation):
                        result_edges.append(edge)
                        if edge.target_id not in visited:
                            queue.append((edge.target_id, depth + 1, path + [edge.target_id]))

        return GraphQueryResult(nodes=result_nodes, edges=result_edges, paths=paths,
                                metadata={"visited": len(visited), "start": start_id})

    def shortest_path(self, source_id: str, target_id: str) -> List[str]:
        """BFS-based shortest path between two nodes."""
        if source_id == target_id:
            return [source_id]
        visited: Set[str] = {source_id}
        queue: deque = deque([(source_id, [source_id])])
        while queue:
            current, path = queue.popleft()
            for eid in self._adj.get(current, []):
                edge = self._edges.get(eid)
                if not edge:
                    continue
                nxt = edge.target_id
                if nxt == target_id:
                    return path + [nxt]
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return []

    def query(self, gq: GraphQuery) -> GraphQueryResult:
        if gq.start_node:
            result = self.bfs(gq.start_node, max_depth=gq.max_depth, relation=gq.relation_filter)
        else:
            nodes = list(self._nodes.values())
            if gq.node_type_filter:
                nodes = [n for n in nodes if n.node_type == gq.node_type_filter]
            result = GraphQueryResult(nodes=nodes[:gq.max_results], edges=[],
                                      metadata={"total_nodes": len(self._nodes)})
        return result

    def semantic_search(self, query: str, top_k: int = 10) -> List[Tuple[Node, float]]:
        """Simple token-overlap similarity search."""
        query_tokens = set(query.lower().split())
        scored: List[Tuple[Node, float]] = []
        for node in self._nodes.values():
            node_tokens = set((node.label + " " + node.node_type).lower().split())
            node_tokens |= {str(v).lower() for v in node.properties.values()}
            overlap = len(query_tokens & node_tokens)
            if overlap:
                score = overlap / len(query_tokens | node_tokens)
                scored.append((node, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def add_context(self, subject: str, predicate: str, obj: str) -> Tuple[Node, Edge, Node]:
        """Convenience triple-store style insertion."""
        s_nodes = self.find_by_label(subject)
        s_node = s_nodes[0] if s_nodes else self.add_node(subject)
        o_nodes = self.find_by_label(obj)
        o_node = o_nodes[0] if o_nodes else self.add_node(obj)
        edge = self.add_edge(s_node.node_id, o_node.node_id, relation=predicate)
        return s_node, edge, o_node  # type: ignore[return-value]

    # ------------------------------------------------------------------ stats

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "node_types": {t: len(ids) for t, ids in self._type_index.items()},
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {"id": n.node_id, "label": n.label, "type": n.node_type, "properties": n.properties}
                for n in self._nodes.values()
            ],
            "edges": [
                {"id": e.edge_id, "source": e.source_id, "target": e.target_id,
                 "relation": e.relation, "weight": e.weight}
                for e in self._edges.values()
            ],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KnowledgeGraph":
        kg = cls()
        for nd in data.get("nodes", []):
            node = Node(node_id=nd["id"], label=nd["label"], node_type=nd.get("type", "concept"),
                        properties=nd.get("properties", {}))
            kg._nodes[node.node_id] = node
            kg._label_index[node.label.lower()].add(node.node_id)
            kg._type_index[node.node_type].add(node.node_id)
        for ed in data.get("edges", []):
            edge = Edge(edge_id=ed["id"], source_id=ed["source"], target_id=ed["target"],
                        relation=ed["relation"], weight=ed.get("weight", 1.0))
            kg._edges[edge.edge_id] = edge
            kg._adj[edge.source_id].append(edge.edge_id)
            kg._rev_adj[edge.target_id].append(edge.edge_id)
        return kg
