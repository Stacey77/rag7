"""Lineage graph visualization (ASCII + structured formats)."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class VisualizationOutput:
    format: str = "ascii"
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


def _indent(level: int) -> str:
    return "  " * level


class ASCIIRenderer:
    """Renders lineage as an ASCII tree."""

    def render_tree(self, root_name: str,
                    adjacency: Dict[str, List[str]],
                    max_depth: int = 5) -> str:
        lines: List[str] = []
        visited: set = set()

        def _recurse(node: str, depth: int) -> None:
            if depth > max_depth or node in visited:
                return
            visited.add(node)
            prefix = _indent(depth) + ("└── " if depth > 0 else "")
            lines.append(f"{prefix}{node}")
            for child in adjacency.get(node, []):
                _recurse(child, depth + 1)

        _recurse(root_name, 0)
        return "\n".join(lines)

    def render_dag(self, nodes: List[Dict[str, Any]],
                   edges: List[Dict[str, Any]]) -> str:
        id_to_name = {n["id"]: n.get("name", n["id"][:8]) for n in nodes}
        lines = ["=== Data Lineage DAG ===", ""]

        adjacency: Dict[str, List[str]] = {}
        for edge in edges:
            src = id_to_name.get(edge.get("source", ""), "?")
            tgt = id_to_name.get(edge.get("target", ""), "?")
            op = edge.get("operation", "->")
            lines.append(f"  {src}  --[{op}]-->  {tgt}")
            adjacency.setdefault(src, []).append(tgt)

        lines.append("")
        roots = {id_to_name[n["id"]] for n in nodes
                 if not any(id_to_name.get(e.get("target")) == id_to_name[n["id"]]
                            for e in edges)}
        if roots:
            lines.append("=== Tree View (from roots) ===")
            for root in sorted(roots):
                lines.append(self.render_tree(root, adjacency))
        return "\n".join(lines)


class MermaidRenderer:
    """Renders lineage as Mermaid flowchart syntax."""

    def render(self, nodes: List[Dict[str, Any]],
               edges: List[Dict[str, Any]]) -> str:
        id_to_name = {n["id"]: n.get("name", n["id"][:8]).replace(" ", "_") for n in nodes}
        lines = ["graph LR"]
        node_types = {n["id"]: n.get("type", "dataset") for n in nodes}

        for node in nodes:
            nid = node["id"]
            name = id_to_name[nid]
            ntype = node_types[nid]
            if ntype in ("transformation", "model"):
                lines.append(f"  {nid}[/{name}/]")
            elif ntype == "source":
                lines.append(f"  {nid}[('{name}')]")
            else:
                lines.append(f"  {nid}[{name}]")

        for edge in edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            op = edge.get("operation", "-->")
            lines.append(f"  {src} -->|{op}| {tgt}")

        return "\n".join(lines)


class DOTRenderer:
    """Renders lineage as GraphViz DOT format."""

    def render(self, nodes: List[Dict[str, Any]],
               edges: List[Dict[str, Any]]) -> str:
        id_to_name = {n["id"]: n.get("name", n["id"][:8]) for n in nodes}
        lines = ["digraph lineage {", '  rankdir=LR;', '  node [shape=box];']
        node_shapes = {"transformation": "ellipse", "model": "diamond",
                       "source": "cylinder", "dataset": "box"}
        for node in nodes:
            nid = node["id"]
            label = id_to_name[nid]
            shape = node_shapes.get(node.get("type", "dataset"), "box")
            lines.append(f'  "{nid}" [label="{label}", shape={shape}];')
        for edge in edges:
            src = edge.get("source", "")
            tgt = edge.get("target", "")
            op = edge.get("operation", "")
            lines.append(f'  "{src}" -> "{tgt}" [label="{op}"];')
        lines.append("}")
        return "\n".join(lines)


class LineageVisualizer:
    """
    Multi-format lineage visualizer supporting ASCII, Mermaid, DOT, and JSON.
    """

    def __init__(self) -> None:
        self._ascii = ASCIIRenderer()
        self._mermaid = MermaidRenderer()
        self._dot = DOTRenderer()
        logger.info("LineageVisualizer initialized")

    def visualize(self, lineage_dict: Dict[str, Any],
                  fmt: str = "ascii") -> VisualizationOutput:
        nodes = lineage_dict.get("nodes", [])
        edges = lineage_dict.get("edges", [])

        if fmt == "ascii":
            content = self._ascii.render_dag(nodes, edges)
        elif fmt == "mermaid":
            content = self._mermaid.render(nodes, edges)
        elif fmt == "dot":
            content = self._dot.render(nodes, edges)
        elif fmt == "json":
            content = json.dumps(lineage_dict, indent=2, default=str)
        else:
            content = f"Unsupported format: {fmt}"

        return VisualizationOutput(
            format=fmt,
            content=content,
            metadata={"node_count": len(nodes), "edge_count": len(edges)},
        )

    def upstream_tree(self, node_name: str,
                       lineage_dict: Dict[str, Any]) -> str:
        nodes = lineage_dict.get("nodes", [])
        edges = lineage_dict.get("edges", [])
        id_to_name = {n["id"]: n.get("name") for n in nodes}
        name_to_id = {n.get("name"): n["id"] for n in nodes}

        target_id = name_to_id.get(node_name)
        if not target_id:
            return f"Node '{node_name}' not found"

        adjacency: Dict[str, List[str]] = {}
        for edge in edges:
            tgt = id_to_name.get(edge.get("target", ""), "?")
            src = id_to_name.get(edge.get("source", ""), "?")
            adjacency.setdefault(tgt, []).append(src)

        return self._ascii.render_tree(node_name, adjacency)
