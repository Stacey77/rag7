"""Data lineage tracking."""
from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class LineageNode:
    node_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    node_type: str = "dataset"   # dataset | transformation | model | report | source
    location: str = ""
    schema: Dict[str, str] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LineageEdge:
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str = ""
    target_id: str = ""
    operation: str = "derived_from"   # derived_from | transformed_by | used_by | written_to
    transformation_logic: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LineagePath:
    path_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    nodes: List[LineageNode] = field(default_factory=list)
    edges: List[LineageEdge] = field(default_factory=list)
    depth: int = 0


@dataclass
class ImpactAnalysis:
    source_node: str = ""
    affected_nodes: List[str] = field(default_factory=list)
    affected_count: int = 0
    paths: List[LineagePath] = field(default_factory=list)


class LineageTracker:
    """
    Tracks data lineage across transformations, pipelines, and models.
    Supports upstream/downstream impact analysis and lineage queries.
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, LineageNode] = {}
        self._edges: Dict[str, LineageEdge] = {}
        self._adj: Dict[str, List[str]] = {}       # source -> [edge_ids]
        self._rev_adj: Dict[str, List[str]] = {}   # target -> [edge_ids]
        logger.info("LineageTracker initialized")

    def register_node(self, name: str, node_type: str = "dataset",
                       location: str = "", schema: Optional[Dict[str, str]] = None,
                       properties: Optional[Dict[str, Any]] = None) -> LineageNode:
        # Check for existing node with same name
        existing = next((n for n in self._nodes.values() if n.name == name), None)
        if existing:
            return existing
        node = LineageNode(name=name, node_type=node_type, location=location,
                           schema=schema or {}, properties=properties or {})
        self._nodes[node.node_id] = node
        self._adj[node.node_id] = []
        self._rev_adj[node.node_id] = []
        logger.debug("Registered lineage node: %s (%s)", name, node_type)
        return node

    def add_lineage(self, source_name: str, target_name: str,
                    operation: str = "derived_from",
                    transformation_logic: str = "",
                    properties: Optional[Dict[str, Any]] = None) -> LineageEdge:
        source = self.get_or_create_node(source_name)
        target = self.get_or_create_node(target_name)
        edge = LineageEdge(source_id=source.node_id, target_id=target.node_id,
                           operation=operation, transformation_logic=transformation_logic,
                           properties=properties or {})
        self._edges[edge.edge_id] = edge
        self._adj[source.node_id].append(edge.edge_id)
        self._rev_adj[target.node_id].append(edge.edge_id)
        logger.debug("Lineage: %s -[%s]-> %s", source_name, operation, target_name)
        return edge

    def get_or_create_node(self, name: str) -> LineageNode:
        existing = next((n for n in self._nodes.values() if n.name == name), None)
        return existing if existing else self.register_node(name)

    def get_upstream(self, node_name: str, depth: int = 10) -> LineagePath:
        node = next((n for n in self._nodes.values() if n.name == node_name), None)
        if not node:
            return LineagePath()
        return self._traverse(node.node_id, direction="upstream", max_depth=depth)

    def get_downstream(self, node_name: str, depth: int = 10) -> LineagePath:
        node = next((n for n in self._nodes.values() if n.name == node_name), None)
        if not node:
            return LineagePath()
        return self._traverse(node.node_id, direction="downstream", max_depth=depth)

    def _traverse(self, start_id: str, direction: str, max_depth: int) -> LineagePath:
        from collections import deque
        visited: Set[str] = set()
        queue = deque([(start_id, 0)])
        result_nodes: List[LineageNode] = []
        result_edges: List[LineageEdge] = []
        max_d = 0

        while queue:
            node_id, depth = queue.popleft()
            if node_id in visited or depth > max_depth:
                continue
            visited.add(node_id)
            node = self._nodes.get(node_id)
            if node:
                result_nodes.append(node)
                max_d = max(max_d, depth)

            if direction == "upstream":
                edge_ids = self._rev_adj.get(node_id, [])
                next_fn = lambda e: e.source_id
            else:
                edge_ids = self._adj.get(node_id, [])
                next_fn = lambda e: e.target_id

            for eid in edge_ids:
                edge = self._edges.get(eid)
                if edge:
                    result_edges.append(edge)
                    next_node = next_fn(edge)
                    if next_node not in visited:
                        queue.append((next_node, depth + 1))

        return LineagePath(nodes=result_nodes, edges=result_edges, depth=max_d)

    def impact_analysis(self, node_name: str) -> ImpactAnalysis:
        downstream = self.get_downstream(node_name)
        affected = [n.name for n in downstream.nodes if n.name != node_name]
        return ImpactAnalysis(
            source_node=node_name,
            affected_nodes=affected,
            affected_count=len(affected),
            paths=[downstream],
        )

    def list_nodes(self, node_type: Optional[str] = None) -> List[LineageNode]:
        if node_type:
            return [n for n in self._nodes.values() if n.node_type == node_type]
        return list(self._nodes.values())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n.node_id, "name": n.name, "type": n.node_type} for n in self._nodes.values()],
            "edges": [{"id": e.edge_id, "source": e.source_id, "target": e.target_id,
                       "operation": e.operation} for e in self._edges.values()],
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {"nodes": len(self._nodes), "edges": len(self._edges)}
