"""Tests for multi-object tracking module."""

import unittest
from unittest.mock import MagicMock
import numpy as np


def _make_det(bbox, class_name="person", class_id=0, confidence=0.9):
    """Helper to create a DetectionResult."""
    from vision.detection.detector import DetectionResult
    return DetectionResult(
        bbox=bbox,
        class_name=class_name,
        class_id=class_id,
        confidence=confidence,
    )


class TestMultiObjectTracker(unittest.TestCase):
    """Tests for MultiObjectTracker."""

    def setUp(self):
        from vision.tracking.multi_object_tracker import MultiObjectTracker
        self.tracker = MultiObjectTracker(max_age=5, min_hits=1, iou_threshold=0.3)

    def test_empty_update_returns_empty(self):
        result = self.tracker.update([])
        self.assertEqual(result, [])

    def test_single_detection_creates_track(self):
        det = _make_det((10, 20, 100, 200))
        self.tracker.update([det])
        # Need min_hits=1, so this track should be confirmed after 1 hit
        result = self.tracker.update([det])
        self.assertGreater(len(result), 0)

    def test_track_ids_are_unique(self):
        dets = [
            _make_det((0, 0, 50, 50), class_name="car", class_id=2),
            _make_det((200, 200, 250, 250), class_name="person", class_id=0),
        ]
        self.tracker.update(dets)
        result = self.tracker.update(dets)
        ids = [t.track_id for t in result]
        self.assertEqual(len(ids), len(set(ids)), "Track IDs must be unique")

    def test_track_deleted_after_max_age(self):
        det = _make_det((10, 10, 60, 60))
        # Create track
        for _ in range(3):
            self.tracker.update([det])
        # Stop providing detection — track should die within max_age frames
        for _ in range(10):
            result = self.tracker.update([])
        self.assertEqual(len(result), 0)

    def test_iou_helper(self):
        from vision.tracking.multi_object_tracker import _iou
        # Perfect overlap
        self.assertAlmostEqual(_iou((0, 0, 10, 10), (0, 0, 10, 10)), 1.0)
        # No overlap
        self.assertAlmostEqual(_iou((0, 0, 10, 10), (20, 20, 30, 30)), 0.0)

    def test_reset_clears_tracks(self):
        det = _make_det((0, 0, 50, 50))
        for _ in range(3):
            self.tracker.update([det])
        self.tracker.reset()
        result = self.tracker.update([])
        self.assertEqual(result, [])
        self.assertEqual(self.tracker._next_id, 1)

    def test_track_state_tentative_then_confirmed(self):
        from vision.tracking.multi_object_tracker import MultiObjectTracker
        tracker = MultiObjectTracker(max_age=5, min_hits=3, iou_threshold=0.3)
        det = _make_det((0, 0, 50, 50))
        # First two updates: track is tentative
        tracker.update([det])
        internal = tracker._tracks
        self.assertEqual(len(internal), 1)
        self.assertEqual(internal[0].state, "tentative")
        # Third hit confirms
        tracker.update([det])
        tracker.update([det])
        confirmed = [t for t in tracker._tracks if t.state == "confirmed"]
        self.assertGreater(len(confirmed), 0)


class TestByteTracker(unittest.TestCase):
    """Tests for ByteTracker."""

    def setUp(self):
        from vision.tracking.bytetrack import ByteTracker
        self.tracker = ByteTracker(
            max_age=5, min_hits=1, iou_threshold=0.3,
            high_thresh=0.6, low_thresh=0.1,
        )

    def test_high_conf_creates_track(self):
        det = _make_det((0, 0, 50, 50), confidence=0.9)
        for _ in range(2):
            result = self.tracker.update([det])
        self.assertGreater(len(result), 0)

    def test_low_conf_below_threshold_ignored(self):
        det = _make_det((0, 0, 50, 50), confidence=0.05)
        result = self.tracker.update([det])
        self.assertEqual(result, [])

    def test_two_stage_association(self):
        # High-conf det creates a track; low-conf det sustains it
        det_high = _make_det((0, 0, 50, 50), confidence=0.9)
        det_low = _make_det((1, 1, 51, 51), confidence=0.3)

        self.tracker.update([det_high])
        self.tracker.update([det_high])  # confirm
        result = self.tracker.update([det_low])
        # Track should still exist due to stage-2 association
        self.assertGreater(len(result), 0)


class TestDeepSORTTracker(unittest.TestCase):
    """Tests for DeepSORTTracker."""

    def test_init_defaults(self):
        from vision.tracking.deepsort import DeepSORTTracker
        tracker = DeepSORTTracker()
        self.assertEqual(tracker.max_age, 30)
        self.assertEqual(tracker.max_cosine_distance, 0.4)

    def test_update_without_image(self):
        from vision.tracking.deepsort import DeepSORTTracker
        tracker = DeepSORTTracker(min_hits=1)
        det = _make_det((10, 10, 60, 60))
        result = tracker.update([det])
        self.assertIsInstance(result, list)

    def test_cosine_distance_identical(self):
        from vision.tracking.deepsort import DeepSORTTracker
        v = np.array([1.0, 0.0, 0.0])
        dist = DeepSORTTracker._cosine_distance(v, v)
        self.assertAlmostEqual(dist, 0.0)

    def test_cosine_distance_orthogonal(self):
        from vision.tracking.deepsort import DeepSORTTracker
        a = np.array([1.0, 0.0, 0.0])
        b = np.array([0.0, 1.0, 0.0])
        dist = DeepSORTTracker._cosine_distance(a, b)
        self.assertAlmostEqual(dist, 1.0)


class TestReIDModel(unittest.TestCase):
    """Tests for ReIDModel."""

    def test_cosine_distance_static(self):
        from vision.tracking.reid_model import ReIDModel
        a = np.array([1.0, 0.0])
        b = np.array([1.0, 0.0])
        self.assertAlmostEqual(ReIDModel.cosine_distance(a, b), 0.0)

    def test_cosine_distance_zero_vector(self):
        from vision.tracking.reid_model import ReIDModel
        a = np.zeros(3)
        b = np.array([1.0, 0.0, 0.0])
        dist = ReIDModel.cosine_distance(a, b)
        self.assertAlmostEqual(dist, 1.0)


if __name__ == "__main__":
    unittest.main()
