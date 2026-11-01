"""Scene analyser: classify scene type and generate text descriptions."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class SceneAnalyzer:
    """Analyse the scene content and generate natural-language descriptions.

    Combines detection results with a rule-based description generator.
    Optionally uses a VLM captioner for richer descriptions.

    Example::

        analyzer = SceneAnalyzer()
        desc = analyzer.generate_description(image, detections)
    """

    # Simple heuristics: map sets of class names to scene types
    _SCENE_HEURISTICS: Dict[str, List[str]] = {
        "kitchen": ["bottle", "cup", "bowl", "fork", "knife", "spoon", "microwave",
                    "oven", "refrigerator", "sink"],
        "office": ["laptop", "keyboard", "mouse", "monitor", "chair", "desk"],
        "outdoor": ["car", "bus", "truck", "bicycle", "person", "traffic light"],
        "living room": ["couch", "tv", "potted plant", "chair", "remote"],
        "bedroom": ["bed", "pillow", "lamp"],
    }

    def __init__(self, use_captioner: bool = False, device: str = "cpu") -> None:
        """
        Args:
            use_captioner: If ``True``, load an image captioner for richer
                           descriptions (requires transformers + BLIP).
            device: Compute device.
        """
        self.use_captioner = use_captioner
        self.device = device
        self._captioner = None

    def _load_captioner(self) -> None:
        """Lazily load the BLIP image captioner."""
        from vision.vlm.image_captioner import ImageCaptioner

        self._captioner = ImageCaptioner(device=self.device)

    def classify_scene(self, detections: List[Any]) -> str:
        """Classify the scene type from a list of detections.

        Args:
            detections: List of objects with a ``class_name`` attribute.

        Returns:
            Scene type string, e.g. ``"kitchen"``, or ``"unknown"``.
        """
        detected_classes = {d.class_name.lower() for d in detections}
        best_type, best_overlap = "unknown", 0

        for scene_type, class_list in self._SCENE_HEURISTICS.items():
            overlap = len(detected_classes & set(class_list))
            if overlap > best_overlap:
                best_overlap = overlap
                best_type = scene_type

        return best_type

    def generate_description(
        self,
        image: np.ndarray,
        detections: Optional[List[Any]] = None,
    ) -> str:
        """Generate a text description of the scene.

        Args:
            image: BGR numpy array.
            detections: Optional list of detection results.

        Returns:
            Natural-language scene description.
        """
        if self.use_captioner:
            if self._captioner is None:
                self._load_captioner()
            try:
                return self._captioner.caption(image)
            except Exception as exc:
                logger.warning("Captioner failed: %s; using rule-based fallback", exc)

        if detections is None:
            detections = []

        scene_type = self.classify_scene(detections)

        # Count occurrences of each class
        counts: Dict[str, int] = {}
        for det in detections:
            counts[det.class_name] = counts.get(det.class_name, 0) + 1

        if not counts:
            return f"A {scene_type} scene with no detected objects."

        object_str = ", ".join(
            f"{count} {name}" + ("s" if count > 1 else "")
            for name, count in sorted(counts.items())
        )
        return f"A {scene_type} scene containing {object_str}."

    def identify_main_objects(
        self, detections: List[Any], top_k: int = 5
    ) -> List[str]:
        """Return the top-K most prominent objects by confidence and size.

        Args:
            detections: List of detections.
            top_k: Maximum number of objects to return.

        Returns:
            List of class names sorted by prominence.
        """
        ranked = sorted(
            detections,
            key=lambda d: d.confidence * getattr(d, "area", 1.0),
            reverse=True,
        )
        return [d.class_name for d in ranked[:top_k]]
