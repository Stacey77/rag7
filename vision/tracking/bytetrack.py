"""ByteTrack multi-object tracker implementation."""

from __future__ import annotations

import logging
from typing import List, Tuple

import numpy as np

from vision.detection.detector import DetectionResult
from vision.tracking.multi_object_tracker import (
    MultiObjectTracker,
    Track,
    _bbox_to_state,
    _iou,
)

logger = logging.getLogger(__name__)


class ByteTracker(MultiObjectTracker):
    """ByteTrack: two-stage IoU association that retains low-confidence detections.

    High-confidence detections are matched first; leftover tracks are then
    associated with low-confidence detections, reducing identity switches.

    Reference: Zhang et al., "ByteTrack: Multi-Object Tracking by Associating
    Every Detection Box" (ECCV 2022).

    Example::

        tracker = ByteTracker(high_thresh=0.6, low_thresh=0.1)
        for dets in stream:
            tracks = tracker.update(dets)
    """

    def __init__(
        self,
        max_age: int = 30,
        min_hits: int = 3,
        iou_threshold: float = 0.3,
        high_thresh: float = 0.6,
        low_thresh: float = 0.1,
    ) -> None:
        """
        Args:
            max_age: Frames without match before deletion.
            min_hits: Minimum hits to confirm a track.
            iou_threshold: IoU threshold for association.
            high_thresh: Confidence threshold separating high/low detections.
            low_thresh: Minimum confidence to consider a detection.
        """
        super().__init__(
            max_age=max_age,
            min_hits=min_hits,
            iou_threshold=iou_threshold,
        )
        self.high_thresh = high_thresh
        self.low_thresh = low_thresh

    def update(self, detections: List[DetectionResult]) -> List[Track]:  # type: ignore[override]
        """Two-stage update: high-conf detections first, then low-conf.

        Args:
            detections: List of detections from the current frame.

        Returns:
            List of confirmed :class:`~vision.tracking.multi_object_tracker.Track`.
        """
        high_dets = [d for d in detections if d.confidence >= self.high_thresh]
        low_dets = [
            d
            for d in detections
            if self.low_thresh <= d.confidence < self.high_thresh
        ]

        # Stage 1: associate ALL tracks with high-confidence detections
        active_tracks = list(self._tracks)
        lost_tracks: list = []  # reserved for future re-id extension

        matched1, unmatched_high, unmatched_trks1 = self._associate_stage(
            high_dets, active_tracks
        )
        self._apply_matches(matched1, high_dets, active_tracks)

        # Stage 2: associate unmatched active tracks with low-confidence dets
        remaining_tracks = [active_tracks[i] for i in unmatched_trks1]
        matched2, _, _ = self._associate_stage(low_dets, remaining_tracks)
        self._apply_matches(matched2, low_dets, remaining_tracks)

        # Create new tracks from still-unmatched high-confidence detections
        for det_idx in unmatched_high:
            det = high_dets[det_idx]
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

        # Age all tracks that were NOT matched this frame
        matched_track_ids = {
            active_tracks[t_j].track_id
            for _, t_j in matched1
        } | {
            remaining_tracks[t_j].track_id
            for _, t_j in matched2
        }
        for track in self._tracks:
            track.age += 1
            if track.track_id not in matched_track_ids:
                track.time_since_update += 1

        # Remove old tracks
        self._tracks = [
            t for t in self._tracks if t.time_since_update <= self.max_age
        ]
        return [t for t in self._tracks if t.state == "confirmed"]

    def _associate_stage(
        self,
        detections: List[DetectionResult],
        tracks: List[Track],
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        """IoU-based greedy association for one stage."""
        if not tracks or not detections:
            return [], list(range(len(detections))), list(range(len(tracks)))

        iou_matrix = np.zeros((len(detections), len(tracks)), dtype=np.float32)
        for d_i, det in enumerate(detections):
            for t_j, trk in enumerate(tracks):
                iou_matrix[d_i, t_j] = _iou(det.bbox, trk.bbox)

        matched: List[Tuple[int, int]] = []
        used_dets: set = set()
        used_trks: set = set()
        for idx in np.argsort(-iou_matrix, axis=None):
            d_i, t_j = divmod(int(idx), len(tracks))
            if iou_matrix[d_i, t_j] < self.iou_threshold:
                break
            if d_i not in used_dets and t_j not in used_trks:
                matched.append((d_i, t_j))
                used_dets.add(d_i)
                used_trks.add(t_j)

        unmatched_dets = [i for i in range(len(detections)) if i not in used_dets]
        unmatched_trks = [j for j in range(len(tracks)) if j not in used_trks]
        return matched, unmatched_dets, unmatched_trks

    def _apply_matches(
        self,
        matched: List[Tuple[int, int]],
        detections: List[DetectionResult],
        tracks: List[Track],
    ) -> None:
        """Apply matched associations to update track states."""
        for det_idx, trk_idx in matched:
            det = detections[det_idx]
            trk = tracks[trk_idx]
            trk.bbox = det.bbox
            trk.confidence = det.confidence
            trk.hits += 1
            trk.time_since_update = 0
            trk.kalman_state = _bbox_to_state(det.bbox)
            if trk.hits >= self.min_hits:
                trk.state = "confirmed"
