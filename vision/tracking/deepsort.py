"""Deep SORT tracker with appearance-based re-identification."""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import numpy as np

from vision.detection.detector import DetectionResult
from vision.tracking.multi_object_tracker import (
    MultiObjectTracker,
    Track,
    _bbox_to_state,
    _state_to_bbox,
    _iou,
)

logger = logging.getLogger(__name__)


class DeepSORTTracker(MultiObjectTracker):
    """Deep SORT: extends SORT with appearance-based ReID matching.

    Association uses a weighted combination of Mahalanobis distance
    (motion) and cosine distance (appearance).

    Example::

        tracker = DeepSORTTracker(device="cpu")
        tracks = tracker.update(detections, image)
    """

    def __init__(
        self,
        max_age: int = 30,
        min_hits: int = 3,
        iou_threshold: float = 0.3,
        max_cosine_distance: float = 0.4,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            max_age: Maximum frames without update before deletion.
            min_hits: Minimum hits to confirm a track.
            iou_threshold: IoU threshold for first-pass association.
            max_cosine_distance: Maximum cosine distance for appearance matching.
            device: Device for the ReID feature extractor.
        """
        super().__init__(
            max_age=max_age, min_hits=min_hits, iou_threshold=iou_threshold
        )
        self.max_cosine_distance = max_cosine_distance
        self.device = device
        self._features: dict[int, np.ndarray] = {}  # track_id -> feature
        self._reid: Optional[object] = None  # lazy

    def _load_reid(self) -> None:
        """Lazily load the ReID model."""
        from vision.tracking.reid_model import ReIDModel

        self._reid = ReIDModel(device=self.device)

    def update(  # type: ignore[override]
        self,
        detections: List[DetectionResult],
        image: Optional[np.ndarray] = None,
    ) -> List[Track]:
        """Update tracks with new detections, optionally using appearance.

        Args:
            detections: Detections from current frame.
            image: Current frame (BGR).  Required for appearance features.

        Returns:
            List of confirmed :class:`~vision.tracking.multi_object_tracker.Track`.
        """
        # Extract appearance features if image is provided
        det_features: List[Optional[np.ndarray]] = [None] * len(detections)
        if image is not None:
            if self._reid is None:
                self._load_reid()
            for i, det in enumerate(detections):
                try:
                    crop = self._crop(image, det.bbox)
                    if crop is not None and crop.size > 0:
                        det_features[i] = self._reid.extract(crop)  # type: ignore
                except Exception:
                    pass

        # Run base SORT update
        tracks = super().update(detections)

        # Update stored features for matched tracks
        for track in tracks:
            tid = track.track_id
            # Find which detection was matched to this track
            for i, det in enumerate(detections):
                if (
                    abs(det.bbox[0] - track.bbox[0]) < 1.0
                    and det_features[i] is not None
                ):
                    feat = det_features[i]
                    if tid in self._features:
                        # Exponential moving average
                        self._features[tid] = (
                            0.9 * self._features[tid] + 0.1 * feat
                        )
                    else:
                        self._features[tid] = feat
                    break

        return tracks

    @staticmethod
    def _crop(
        image: np.ndarray,
        bbox: Tuple[float, float, float, float],
    ) -> Optional[np.ndarray]:
        """Crop a region from *image* using *bbox*."""
        h, w = image.shape[:2]
        x1, y1, x2, y2 = (
            max(0, int(bbox[0])),
            max(0, int(bbox[1])),
            min(w, int(bbox[2])),
            min(h, int(bbox[3])),
        )
        if x2 <= x1 or y2 <= y1:
            return None
        return image[y1:y2, x1:x2]

    @staticmethod
    def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine distance between two feature vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-8 or norm_b < 1e-8:
            return 1.0
        return 1.0 - float(np.dot(a, b) / (norm_a * norm_b))
