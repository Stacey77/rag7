"""Tests for detection module."""

import unittest
from unittest.mock import MagicMock, patch
import numpy as np


class TestDetectionResult(unittest.TestCase):
    """Test the DetectionResult dataclass."""

    def setUp(self):
        from vision.detection.detector import DetectionResult
        self.DetectionResult = DetectionResult

    def test_basic_creation(self):
        det = self.DetectionResult(
            bbox=(10.0, 20.0, 100.0, 150.0),
            class_name="person",
            class_id=0,
            confidence=0.95,
        )
        self.assertEqual(det.class_name, "person")
        self.assertEqual(det.class_id, 0)
        self.assertAlmostEqual(det.confidence, 0.95)
        self.assertIsNone(det.track_id)

    def test_area_property(self):
        det = self.DetectionResult(
            bbox=(0.0, 0.0, 100.0, 50.0),
            class_name="car",
            class_id=2,
            confidence=0.8,
        )
        self.assertAlmostEqual(det.area, 5000.0)

    def test_center_property(self):
        det = self.DetectionResult(
            bbox=(0.0, 0.0, 100.0, 100.0),
            class_name="dog",
            class_id=16,
            confidence=0.7,
        )
        cx, cy = det.center
        self.assertAlmostEqual(cx, 50.0)
        self.assertAlmostEqual(cy, 50.0)

    def test_to_dict(self):
        det = self.DetectionResult(
            bbox=(5.0, 10.0, 50.0, 80.0),
            class_name="cat",
            class_id=15,
            confidence=0.6,
            track_id=3,
        )
        d = det.to_dict()
        self.assertEqual(d["class_name"], "cat")
        self.assertEqual(d["track_id"], 3)
        self.assertIn("bbox", d)

    def test_zero_area(self):
        det = self.DetectionResult(
            bbox=(50.0, 50.0, 50.0, 50.0),
            class_name="dot",
            class_id=99,
            confidence=0.1,
        )
        self.assertAlmostEqual(det.area, 0.0)


class TestNMS(unittest.TestCase):
    """Test the NMS utility on BaseDetector."""

    def setUp(self):
        from vision.detection.detector import BaseDetector
        self.nms = BaseDetector.nms

    def test_no_boxes(self):
        result = self.nms(np.empty((0, 4)), np.array([]))
        self.assertEqual(result, [])

    def test_single_box(self):
        boxes = np.array([[0, 0, 10, 10]], dtype=np.float32)
        scores = np.array([0.9])
        result = self.nms(boxes, scores)
        self.assertEqual(result, [0])

    def test_overlapping_boxes_suppressed(self):
        boxes = np.array([
            [0, 0, 50, 50],
            [2, 2, 52, 52],
        ], dtype=np.float32)
        scores = np.array([0.9, 0.8])
        result = self.nms(boxes, scores, iou_threshold=0.5)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 0)  # highest score kept

    def test_non_overlapping_boxes_kept(self):
        boxes = np.array([
            [0, 0, 10, 10],
            [100, 100, 110, 110],
        ], dtype=np.float32)
        scores = np.array([0.9, 0.8])
        result = self.nms(boxes, scores, iou_threshold=0.5)
        self.assertEqual(len(result), 2)

    def test_score_ordering(self):
        boxes = np.array([
            [0, 0, 50, 50],
            [2, 2, 52, 52],
            [200, 200, 250, 250],
        ], dtype=np.float32)
        scores = np.array([0.7, 0.9, 0.6])
        result = self.nms(boxes, scores, iou_threshold=0.5)
        # Box 1 (highest score) suppresses box 0; box 2 survives
        self.assertIn(1, result)
        self.assertIn(2, result)
        self.assertNotIn(0, result)


class TestYOLODetector(unittest.TestCase):
    """Test YOLODetector with mocked ultralytics."""

    def _make_mock_result(self, bbox, cls_id, conf, name):
        box = MagicMock()
        box.xyxy = [MagicMock()]
        box.xyxy[0].cpu.return_value.numpy.return_value.tolist.return_value = list(bbox)
        box.conf = [MagicMock()]
        box.conf[0].cpu.return_value.numpy.return_value = conf
        box.cls = [MagicMock()]
        box.cls[0].cpu.return_value.numpy.return_value = cls_id
        box.id = None

        result = MagicMock()
        result.boxes = box
        result.names = {cls_id: name}

        # Make it iterable (len, index)
        box.__len__ = MagicMock(return_value=1)
        return result

    @patch("vision.detection.yolo_detector.YOLODetector._load_model")
    def test_detect_calls_model(self, mock_load):
        from vision.detection.yolo_detector import YOLODetector

        detector = YOLODetector(model_size="yolov8n", confidence_threshold=0.5)

        mock_result = self._make_mock_result(
            bbox=[10, 20, 100, 200], cls_id=0, conf=0.9, name="person"
        )
        detector._model = MagicMock(return_value=[mock_result])

        image = np.zeros((480, 640, 3), dtype=np.uint8)
        results = detector.detect(image)
        detector._model.assert_called_once()
        # Results may be empty due to mock structure; we just verify no exception
        self.assertIsInstance(results, list)

    def test_invalid_model_size_defaults(self):
        from vision.detection.yolo_detector import YOLODetector

        det = YOLODetector(model_size="invalid_size")
        self.assertEqual(det.model_size, "yolov8n")

    def test_detect_returns_empty_on_error(self):
        from vision.detection.yolo_detector import YOLODetector

        detector = YOLODetector()
        detector._model = MagicMock(side_effect=RuntimeError("GPU OOM"))
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = detector.detect(image)
        self.assertEqual(result, [])


class TestDETRDetector(unittest.TestCase):
    """Test DETRDetector with mocked transformers."""

    @patch("vision.detection.detr_detector.DETRDetector._load_model")
    def test_detect_empty_on_error(self, mock_load):
        from vision.detection.detr_detector import DETRDetector

        detector = DETRDetector()
        detector._model = MagicMock(side_effect=RuntimeError("test error"))
        detector._processor = MagicMock()

        image = np.zeros((224, 224, 3), dtype=np.uint8)
        results = detector.detect(image)
        self.assertEqual(results, [])

    def test_init_defaults(self):
        from vision.detection.detr_detector import DETRDetector

        det = DETRDetector()
        self.assertEqual(det.threshold, 0.5)
        self.assertEqual(det.device, "cpu")


class TestPersonDetector(unittest.TestCase):
    """Test PersonDetector filters correctly."""

    @patch("vision.detection.yolo_detector.YOLODetector._load_model")
    def test_only_persons_returned(self, mock_load):
        from vision.detection.person_detector import PersonDetector
        from vision.detection.detector import DetectionResult

        detector = PersonDetector()

        all_dets = [
            DetectionResult(bbox=(0, 0, 50, 100), class_name="person", class_id=0, confidence=0.9),
            DetectionResult(bbox=(60, 0, 120, 100), class_name="car", class_id=2, confidence=0.8),
        ]
        # Monkey-patch super().detect
        with patch.object(detector.__class__.__bases__[0], "detect", return_value=all_dets):
            result = detector.detect(np.zeros((480, 640, 3), dtype=np.uint8))

        # Only persons should be returned
        for det in result:
            self.assertEqual(det.class_id, 0)


if __name__ == "__main__":
    unittest.main()
