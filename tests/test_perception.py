"""
Unit tests for the perception module of the RAG7 AGI Robotics Framework.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest

from perception.vision.object_detection import Detection, ObjectDetector
from perception.vision.segmentation import Segmenter
from perception.vision.tracking import ObjectTracker
from perception.slam.mapping import SLAMMapper
from perception.sensor_fusion import SensorFusion


# ===========================================================================
# TestObjectDetector
# ===========================================================================


class TestObjectDetector:
    """Tests for ObjectDetector."""

    @pytest.fixture
    def detector(self):
        return ObjectDetector(confidence_threshold=0.5)

    def test_detect_returns_list(self, detector):
        """detect should return a list."""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = detector.detect(image)
        assert isinstance(results, list)

    def test_detect_mock_detections(self, detector):
        """Mock detections should have the correct namedtuple fields."""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = detector.detect(image)
        for det in results:
            assert hasattr(det, "label")
            assert hasattr(det, "confidence")
            assert hasattr(det, "bbox")
            assert det.confidence >= 0.5

    def test_detect_empty_image(self, detector):
        """detect with an empty array should return empty list."""
        empty = np.array([])
        results = detector.detect(empty)
        assert results == []

    def test_detect_various_shapes(self, detector):
        """detect should work with different image sizes."""
        for h, w in [(240, 320), (720, 1280), (100, 100)]:
            img = np.zeros((h, w, 3), dtype=np.uint8)
            results = detector.detect(img)
            assert isinstance(results, list)

    def test_load_model_nonexistent(self, detector):
        """load_model with a bad path should return False gracefully."""
        result = detector.load_model("/nonexistent/model.pt")
        assert result is False


# ===========================================================================
# TestSegmenter
# ===========================================================================


class TestSegmenter:
    """Tests for Segmenter."""

    @pytest.fixture
    def segmenter(self):
        return Segmenter()

    def test_segment_returns_dict(self, segmenter):
        """segment should return a dict with masks, labels, scores."""
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = segmenter.segment(image)
        assert "masks" in result
        assert "labels" in result
        assert "scores" in result

    def test_segment_mask_shape(self, segmenter):
        """Mask array should have correct spatial dimensions."""
        image = np.zeros((120, 160, 3), dtype=np.uint8)
        result = segmenter.segment(image)
        if result["masks"].ndim == 3:
            _, h, w = result["masks"].shape
            assert h == 120
            assert w == 160

    def test_segment_labels_list(self, segmenter):
        """labels field should be a list of strings."""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = segmenter.segment(image)
        assert isinstance(result["labels"], list)
        assert all(isinstance(l, str) for l in result["labels"])

    def test_segment_empty_image(self, segmenter):
        """segment with empty array should return safe defaults."""
        empty = np.array([])
        result = segmenter.segment(empty)
        assert result["labels"] == []


# ===========================================================================
# TestObjectTracker
# ===========================================================================


class TestObjectTracker:
    """Tests for ObjectTracker."""

    @pytest.fixture
    def tracker(self):
        return ObjectTracker(max_age=5, min_hits=1)

    def _make_detection(self, bbox, label="object"):
        """Helper to build a detection dict."""
        return {"bbox": bbox, "label": label}

    def test_update_returns_list(self, tracker):
        """update should always return a list."""
        dets = [self._make_detection([0, 0, 50, 50])]
        tracks = tracker.update(dets)
        assert isinstance(tracks, list)

    def test_track_has_required_fields(self, tracker):
        """Each track should have id, bbox, label keys."""
        dets = [self._make_detection([10, 10, 60, 60, "person"])]
        tracker.update(dets)
        tracks = tracker.update(dets)
        for t in tracks:
            assert "id" in t
            assert "bbox" in t
            assert "label" in t

    def test_empty_detections(self, tracker):
        """update with no detections should not crash."""
        tracks = tracker.update([])
        assert isinstance(tracks, list)

    def test_track_persistence(self, tracker):
        """A track matched across multiple frames should persist."""
        det = self._make_detection([10, 10, 60, 60])
        for _ in range(5):
            tracker.update([det])
        tracks = tracker.update([det])
        assert len(tracks) >= 1

    def test_iou_identical_boxes(self, tracker):
        """IoU of identical boxes should be 1.0."""
        box = [0.0, 0.0, 10.0, 10.0]
        from perception.vision.tracking import ObjectTracker as OT

        iou = OT._iou(box, box)
        assert iou == pytest.approx(1.0)

    def test_iou_non_overlapping(self, tracker):
        """IoU of non-overlapping boxes should be 0.0."""
        box_a = [0, 0, 10, 10]
        box_b = [20, 20, 30, 30]
        from perception.vision.tracking import ObjectTracker as OT

        iou = OT._iou(box_a, box_b)
        assert iou == pytest.approx(0.0)


# ===========================================================================
# TestSLAMMapper
# ===========================================================================


class TestSLAMMapper:
    """Tests for SLAMMapper."""

    @pytest.fixture
    def mapper(self):
        return SLAMMapper(map_resolution=0.1, map_size=50)

    def test_get_map_shape(self, mapper):
        """get_map should return a square array of the configured size."""
        m = mapper.get_map()
        assert m.shape == (50, 50)

    def test_update_changes_map(self, mapper):
        """update should modify at least some cells in the map."""
        initial_map = mapper.get_map().copy()
        lidar = [2.0] * 36  # 36 rays at 2 metres
        mapper.update(lidar, {"x": 0.0, "y": 0.0, "theta": 0.0})
        updated_map = mapper.get_map()
        assert not np.array_equal(initial_map, updated_map)

    def test_localize_returns_pose(self, mapper):
        """localize should return a dict with x, y, theta keys."""
        lidar = [3.0] * 36
        pose = mapper.localize(lidar)
        assert "x" in pose
        assert "y" in pose
        assert "theta" in pose
        assert "confidence" in pose

    def test_update_with_empty_scan(self, mapper):
        """update with an empty scan should not crash."""
        mapper.update([], {"x": 0.0, "y": 0.0, "theta": 0.0})
        m = mapper.get_map()
        assert m is not None


# ===========================================================================
# TestSensorFusion
# ===========================================================================


class TestSensorFusion:
    """Tests for SensorFusion."""

    @pytest.fixture
    def fusion(self):
        return SensorFusion()

    def test_fuse_returns_dict(self, fusion):
        """fuse should return a dict with required keys."""
        result = fusion.fuse(None, None, None)
        assert "position" in result
        assert "orientation" in result
        assert "confidence" in result

    def test_fuse_with_lidar(self, fusion):
        """fuse should extract nearest obstacle from LiDAR."""
        lidar = [5.0, 3.0, 1.5, 4.0]
        result = fusion.fuse(None, lidar, None)
        assert len(result["obstacles"]) > 0
        assert result["obstacles"][0] == pytest.approx(1.5)

    def test_fuse_with_imu(self, fusion):
        """fuse should propagate IMU orientation values."""
        imu = {"roll": 0.1, "pitch": 0.2, "yaw": 1.0}
        result = fusion.fuse(None, None, imu)
        assert result["orientation"]["yaw"] == pytest.approx(1.0)

    def test_fuse_confidence_range(self, fusion):
        """Confidence should be in [0, 1]."""
        lidar = [2.0, 3.0]
        imu = {"yaw": 0.5}
        result = fusion.fuse(None, lidar, imu)
        assert 0.0 <= result["confidence"] <= 1.0

    def test_fuse_with_camera(self, fusion):
        """fuse with camera depth data should update position."""
        depth = np.ones((10, 10)) * 2.5
        camera = {"depth": depth}
        result = fusion.fuse(camera, None, None)
        assert "position" in result
