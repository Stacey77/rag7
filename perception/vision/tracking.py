"""
Multi-object tracking module for the rag7 perception system.

Implements IoU-based multi-object tracking using a simple
Hungarian-style greedy matching algorithm.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple


class Track:
    """Represents a single tracked object across frames.

    Attributes:
        track_id: Unique integer track identifier.
        bbox: Bounding box [x1, y1, x2, y2].
        label: Class label string.
        age: Number of frames this track has existed.
        hits: Number of consecutive frames with a detection.
        last_seen: Frame index of the last successful update.
    """

    _id_counter = 0

    def __init__(self, bbox: List[float], label: str) -> None:
        """Initialize a new track from an initial detection."""
        Track._id_counter += 1
        self.track_id = Track._id_counter
        self.bbox = list(bbox)
        self.label = label
        self.age: int = 1
        self.hits: int = 1
        self.last_seen: int = 0


class ObjectTracker:
    """IoU-based multi-object tracker.

    Maintains a set of active tracks and matches incoming detections to
    existing tracks using Intersection-over-Union (IoU) overlap.

    Args:
        max_age: Maximum frames a track can persist without a detection.
        min_hits: Minimum consecutive hits before a track is reported.
    """

    def __init__(self, max_age: int = 30, min_hits: int = 3) -> None:
        """Initialize the object tracker."""
        self._logger = logging.getLogger("rag7.perception.tracking")
        self._max_age = max_age
        self._min_hits = min_hits
        self._tracks: List[Track] = []
        self._frame_count: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, detections: List[Any]) -> List[Dict[str, Any]]:
        """Update tracks with the latest set of detections.

        Args:
            detections: List of detection objects or dicts, each with
                ``bbox`` (list[float]) and ``label`` (str) attributes/keys.

        Returns:
            List of active track dictionaries with ``id``, ``bbox``,
            and ``label`` keys.
        """
        self._frame_count += 1
        det_bboxes = []
        det_labels = []

        for det in detections:
            if hasattr(det, "bbox"):
                det_bboxes.append(det.bbox)
                det_labels.append(getattr(det, "label", "unknown"))
            elif isinstance(det, dict):
                det_bboxes.append(det.get("bbox", [0, 0, 1, 1]))
                det_labels.append(det.get("label", "unknown"))

        # Greedy IoU matching
        matched, unmatched_dets, unmatched_trks = self._match(det_bboxes)

        # Update matched tracks
        for det_idx, trk_idx in matched:
            self._tracks[trk_idx].bbox = det_bboxes[det_idx]
            self._tracks[trk_idx].label = det_labels[det_idx]
            self._tracks[trk_idx].hits += 1
            self._tracks[trk_idx].age = 0
            self._tracks[trk_idx].last_seen = self._frame_count

        # Create new tracks for unmatched detections
        for det_idx in unmatched_dets:
            self._tracks.append(Track(det_bboxes[det_idx], det_labels[det_idx]))

        # Age out unmatched existing tracks
        for trk_idx in unmatched_trks:
            self._tracks[trk_idx].age += 1

        # Remove dead tracks
        self._tracks = [t for t in self._tracks if t.age <= self._max_age]

        # Return confirmed tracks
        return [
            {"id": t.track_id, "bbox": t.bbox, "label": t.label}
            for t in self._tracks
            if t.hits >= self._min_hits
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _match(
        self, det_bboxes: List[List[float]]
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        """Greedily match detections to existing tracks using IoU.

        Args:
            det_bboxes: List of detection bounding boxes.

        Returns:
            Tuple of (matched pairs, unmatched det indices,
            unmatched track indices).
        """
        if not self._tracks or not det_bboxes:
            return [], list(range(len(det_bboxes))), list(range(len(self._tracks)))

        iou_matrix = [
            [self._iou(det, trk.bbox) for trk in self._tracks]
            for det in det_bboxes
        ]

        matched: List[Tuple[int, int]] = []
        used_trks: set = set()
        used_dets: set = set()

        # Greedy best-match assignment
        for det_idx in range(len(det_bboxes)):
            best_iou = 0.3  # IoU threshold
            best_trk = -1
            for trk_idx in range(len(self._tracks)):
                if trk_idx in used_trks:
                    continue
                if iou_matrix[det_idx][trk_idx] > best_iou:
                    best_iou = iou_matrix[det_idx][trk_idx]
                    best_trk = trk_idx
            if best_trk >= 0:
                matched.append((det_idx, best_trk))
                used_dets.add(det_idx)
                used_trks.add(best_trk)

        unmatched_dets = [i for i in range(len(det_bboxes)) if i not in used_dets]
        unmatched_trks = [i for i in range(len(self._tracks)) if i not in used_trks]
        return matched, unmatched_dets, unmatched_trks

    @staticmethod
    def _iou(box_a: List[float], box_b: List[float]) -> float:
        """Compute Intersection-over-Union between two bounding boxes.

        Args:
            box_a: Bounding box [x1, y1, x2, y2].
            box_b: Bounding box [x1, y1, x2, y2].

        Returns:
            IoU score in the range [0, 1].
        """
        xa = max(box_a[0], box_b[0])
        ya = max(box_a[1], box_b[1])
        xb = min(box_a[2], box_b[2])
        yb = min(box_a[3], box_b[3])
        inter = max(0.0, xb - xa) * max(0.0, yb - ya)
        area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
        area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
        union = area_a + area_b - inter
        return inter / union if union > 0 else 0.0
