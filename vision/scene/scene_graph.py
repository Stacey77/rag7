"""Scene graph: represent objects and their spatial relationships as a graph."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SceneNode:
    """A node representing a detected object.

    Attributes:
        node_id: Unique identifier.
        class_name: Object class label.
        bbox: Bounding box ``(x1, y1, x2, y2)``.
        confidence: Detection confidence.
        attributes: Free-form attribute dict.
    """

    node_id: int
    class_name: str
    bbox: Tuple[float, float, float, float]
    confidence: float
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SceneEdge:
    """A directed edge between two scene nodes.

    Attributes:
        source_id: ID of the source node.
        target_id: ID of the target node.
        relation: Relationship string, e.g. ``"on"`` or ``"next_to"``.
        confidence: Relationship confidence.
    """

    source_id: int
    target_id: int
    relation: str
    confidence: float = 1.0


class SceneGraph:
    """Build and query a graph of objects and their spatial relationships.

    Nodes represent detected objects; edges encode spatial relations
    computed by :class:`~vision.scene.spatial_relations.SpatialRelations`.

    Example::

        graph = SceneGraph()
        graph.build_from_detections(detections)
        neighbours = graph.get_neighbours(node_id=0)
    """

    def __init__(self) -> None:
        self.nodes: Dict[int, SceneNode] = {}
        self.edges: List[SceneEdge] = []
        self._next_id = 0

    def add_node(
        self,
        class_name: str,
        bbox: Tuple[float, float, float, float],
        confidence: float,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Add a new object node.

        Args:
            class_name: Object class label.
            bbox: Bounding box.
            confidence: Detection confidence.
            attributes: Optional extra attributes.

        Returns:
            The new node's integer ID.
        """
        node = SceneNode(
            node_id=self._next_id,
            class_name=class_name,
            bbox=bbox,
            confidence=confidence,
            attributes=attributes or {},
        )
        self.nodes[self._next_id] = node
        self._next_id += 1
        return node.node_id

    def add_edge(
        self,
        source_id: int,
        target_id: int,
        relation: str,
        confidence: float = 1.0,
    ) -> None:
        """Add a directed relationship edge.

        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            relation: Relation type string.
            confidence: Confidence score.
        """
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Both node IDs must exist before adding an edge.")
        self.edges.append(
            SceneEdge(source_id=source_id, target_id=target_id,
                      relation=relation, confidence=confidence)
        )

    def build_from_detections(self, detections: List[Any]) -> None:
        """Populate the graph from a list of detection results.

        Args:
            detections: List of objects with ``class_name``, ``bbox``,
                        and ``confidence`` attributes.
        """
        self.nodes.clear()
        self.edges.clear()
        self._next_id = 0

        for det in detections:
            self.add_node(det.class_name, det.bbox, det.confidence)

        # Compute pairwise spatial relations
        from vision.scene.spatial_relations import SpatialRelations

        sr = SpatialRelations()
        node_ids = list(self.nodes.keys())
        for i in range(len(node_ids)):
            for j in range(len(node_ids)):
                if i == j:
                    continue
                ni = self.nodes[node_ids[i]]
                nj = self.nodes[node_ids[j]]
                relations = sr.compute(ni.bbox, nj.bbox)
                for rel, conf in relations.items():
                    if conf > 0:
                        self.add_edge(node_ids[i], node_ids[j], rel, conf)

    def get_neighbours(self, node_id: int) -> List[Tuple[int, str]]:
        """Return neighbouring nodes connected by outgoing edges.

        Args:
            node_id: Source node ID.

        Returns:
            List of ``(target_id, relation)`` tuples.
        """
        return [
            (e.target_id, e.relation)
            for e in self.edges
            if e.source_id == node_id
        ]

    def to_dict(self) -> dict:
        """Serialise the scene graph to a plain dictionary."""
        return {
            "nodes": [
                {
                    "id": n.node_id,
                    "class": n.class_name,
                    "bbox": list(n.bbox),
                    "confidence": n.confidence,
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "relation": e.relation,
                    "confidence": e.confidence,
                }
                for e in self.edges
            ],
        }

    def __len__(self) -> int:
        return len(self.nodes)
