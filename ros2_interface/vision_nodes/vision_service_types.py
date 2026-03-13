"""
Service request/response dataclasses for the vision ROS2 node.

These dataclasses are used internally and in tests; they mirror the
structure of the JSON payloads exchanged over ROS2 String-based services.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class FindObjectRequest:
    """Request to locate a described object in the current scene.

    Attributes:
        query: Natural-language description of the object to find, e.g.
               ``"red coffee mug"``.
    """

    query: str


@dataclass
class FindObjectResponse:
    """Response from the find-object service.

    Attributes:
        found: Whether the object was located with sufficient confidence.
        bbox: Bounding box ``[x1, y1, x2, y2]`` in pixel coordinates, or an
              empty list when the object was not found.
        confidence: Detection confidence in ``[0, 1]``.
    """

    found: bool
    bbox: List[float] = field(default_factory=list)
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary suitable for JSON encoding."""
        return {
            "found": self.found,
            "bbox": self.bbox,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FindObjectResponse":
        """Deserialise from a plain dictionary."""
        return cls(
            found=bool(data.get("found", False)),
            bbox=list(data.get("bbox", [])),
            confidence=float(data.get("confidence", 0.0)),
        )


@dataclass
class AnalyzeSceneRequest:
    """Trigger request for a full scene analysis (no fields required)."""


@dataclass
class AnalyzeSceneResponse:
    """Response from the analyze-scene service.

    Attributes:
        description: Human-readable text description of the scene.
        objects: List of detected-object dictionaries.
        spatial_map: Dictionary mapping object IDs to 3-D spatial positions.
    """

    description: str = ""
    objects: List[Dict[str, Any]] = field(default_factory=list)
    spatial_map: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dictionary suitable for JSON encoding."""
        return {
            "description": self.description,
            "objects": self.objects,
            "spatial_map": self.spatial_map,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyzeSceneResponse":
        """Deserialise from a plain dictionary."""
        return cls(
            description=str(data.get("description", "")),
            objects=list(data.get("objects", [])),
            spatial_map=dict(data.get("spatial_map", {})),
        )
