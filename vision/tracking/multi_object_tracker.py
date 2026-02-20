"""Multi-object tracker using a Kalman filter + IoU association."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from vision.detection.detector import DetectionResult

logger = logging.getLogger(__name__)


@dataclass
class Track:
    """Represents a single tracked object.

    Attributes:
        track_id: Unique identifier.
        bbox: Latest bounding box ``(x1, y1, x2, y2)``.
        class_name: Class label.
        class_id: Integer class index.
        confidence: Latest detection confidence.
        age: Number of frames since the track was created.
        hits: Number of times the track has been successfully matched.
        time_since_update: Frames since last successful association.
        state: ``"tentative"``, ``"confirmed"``, or ``"deleted"``.
    """

    track_id: int
    bbox: Tuple[float, float, float, float]
    class_name: str
    class_id: int
    confidence: float
    age: int = 0
    hits: int = 0
    time_since_update: int = 0
    state: str = "tentative"
    kalman_state: Optional[np.ndarray] = None  # [cx, cy, w, h, vx, vy, vw, vh]


def _bbox_to_state(bbox: Tuple[float, float, float, float]) -> np.ndarray:
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    w = x2 - x1
    h = y2 - y1
    return np.array([cx, cy, w, h, 0, 0, 0, 0], dtype=np.float32)


def _state_to_bbox(state: np.ndarray) -> Tuple[float, float, float, float]:
    cx, cy, w, h = state[:4]
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def _iou(box_a: Tuple, box_b: Tuple) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


class MultiObjectTracker:
    """Kalman-filter-based multi-object tracker with IoU assignment.

    Implements the SORT (Simple Online and Realtime Tracking) algorithm core.

    Example::

        tracker = MultiObjectTracker(max_age=5, min_hits=3)
        for frame_dets in detections_per_frame:
            tracks = tracker.update(frame_dets)
    """

    # Constant-velocity Kalman filter matrices (8-state: cx,cy,w,h,vx,vy,vw,vh)
    _F = np.eye(8, dtype=np.float32)  # state transition
    _F[0, 4] = _F[1, 5] = _F[2, 6] = _F[3, 7] = 1.0

    _H = np.eye(4, 8, dtype=np.float32)  # measurement matrix

    def __init__(
        self,
        max_age: int = 5,
        min_hits: int = 3,
        iou_threshold: float = 0.3,
    ) -> None:
        """
        Args:
            max_age: Frames without match before a track is deleted.
            min_hits: Minimum hits before a track is confirmed.
            iou_threshold: Minimum IoU for a valid detection-track association.
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self._tracks: List[Track] = []
        self._next_id = 1

    def update(self, detections: List[DetectionResult]) -> List[Track]:
        """Update tracks with new detections.

        Args:
            detections: List of :class:`~vision.detection.detector.DetectionResult`
                        from the current frame.

        Returns:
            List of active (confirmed) :class:`Track` objects.
        """
        # --- Predict new positions ---
        for track in self._tracks:
            if track.kalman_state is not None:
                track.kalman_state = self._F @ track.kalman_state
                track.bbox = _state_to_bbox(track.kalman_state)
            track.age += 1
            track.time_since_update += 1

        # --- Association ---
        matched, unmatched_dets, unmatched_trks = self._associate(detections)

        # --- Update matched tracks ---
        for det_idx, trk_idx in matched:
            det = detections[det_idx]
            trk = self._tracks[trk_idx]
            trk.bbox = det.bbox
            trk.confidence = det.confidence
            trk.hits += 1
            trk.time_since_update = 0
            trk.kalman_state = _bbox_to_state(det.bbox)
            if trk.hits >= self.min_hits:
                trk.state = "confirmed"

        # --- Create new tracks ---
        for det_idx in unmatched_dets:
            det = detections[det_idx]
            new_track = Track(
                track_id=self._next_id,
                bbox=det.bbox,
                class_name=det.class_name,
                class_id=det.class_id,
                confidence=det.confidence,
                hits=1,
                kalman_state=_bbox_to_state(det.bbox),
            )
            self._next_id += 1
            self._tracks.append(new_track)

        # --- Remove stale tracks ---
        self._tracks = [
            t for t in self._tracks if t.time_since_update <= self.max_age
        ]
        # Mark those that have been unseen too long as deleted
        for t in self._tracks:
            if t.time_since_update > 0:
                t.state = "tentative" if t.hits < self.min_hits else "confirmed"

        return [t for t in self._tracks if t.state == "confirmed"]

    def _associate(
        self, detections: List[DetectionResult]
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        """Greedy IoU-based assignment."""
        if not self._tracks or not detections:
            return [], list(range(len(detections))), list(range(len(self._tracks)))

        iou_matrix = np.zeros(
            (len(detections), len(self._tracks)), dtype=np.float32
        )
        for d_i, det in enumerate(detections):
            for t_j, trk in enumerate(self._tracks):
                iou_matrix[d_i, t_j] = _iou(det.bbox, trk.bbox)

        matched: List[Tuple[int, int]] = []
        used_dets: set = set()
        used_trks: set = set()

        # Greedy matching by descending IoU
        flat_order = np.argsort(-iou_matrix, axis=None)
        for idx in flat_order:
            d_i, t_j = divmod(int(idx), len(self._tracks))
            if iou_matrix[d_i, t_j] < self.iou_threshold:
                break
            if d_i not in used_dets and t_j not in used_trks:
                matched.append((d_i, t_j))
                used_dets.add(d_i)
                used_trks.add(t_j)

        unmatched_dets = [i for i in range(len(detections)) if i not in used_dets]
        unmatched_trks = [j for j in range(len(self._tracks)) if j not in used_trks]
        return matched, unmatched_dets, unmatched_trks

    def reset(self) -> None:
        """Clear all tracks."""
        self._tracks.clear()
        self._next_id = 1
