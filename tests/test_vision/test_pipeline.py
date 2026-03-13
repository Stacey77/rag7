"""Tests for VisionPipeline."""

import unittest
from unittest.mock import MagicMock, patch
import numpy as np


class TestVisionPipelineInit(unittest.TestCase):
    """Test VisionPipeline initialisation."""

    def test_default_init(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline()
        self.assertTrue(pipeline.config.enable_detection)
        self.assertFalse(pipeline.config.enable_segmentation)
        self.assertFalse(pipeline.config.enable_depth)
        self.assertFalse(pipeline.config.enable_clip)

    def test_custom_init(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline(
            device="cpu",
            enable_detection=False,
            enable_segmentation=True,
        )
        self.assertFalse(pipeline.config.enable_detection)
        self.assertTrue(pipeline.config.enable_segmentation)

    def test_config_object_overrides_params(self):
        from vision.vision_pipeline import VisionPipeline, PipelineConfig

        cfg = PipelineConfig(device="cpu", enable_detection=False)
        pipeline = VisionPipeline(enable_detection=True, config=cfg)
        # Config takes precedence
        self.assertFalse(pipeline.config.enable_detection)

    def test_lazy_detector_is_none_initially(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline(enable_detection=True)
        self.assertIsNone(pipeline._detector)

    def test_lazy_detector_loaded_on_first_access(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline(enable_detection=True)

        # YOLODetector is lazily imported inside the property, so patch its
        # constructor at the source module level.
        with patch("vision.detection.yolo_detector.YOLODetector.__init__",
                   return_value=None) as mock_init:
            det = pipeline.detector
            # Detector was created (lazy load triggered)
            self.assertIsNotNone(pipeline._detector)


class TestVisionPipelineProcessFrame(unittest.TestCase):
    """Test process_frame behaviour."""

    def setUp(self):
        from vision.vision_pipeline import VisionPipeline

        self.pipeline = VisionPipeline(
            device="cpu",
            enable_detection=True,
            enable_segmentation=False,
            enable_depth=False,
            enable_tracking=False,
        )

    def test_process_frame_raises_on_empty_image(self):
        with self.assertRaises(ValueError):
            self.pipeline.process_frame(np.array([]))

    def test_process_frame_returns_frame_result(self):
        from vision.vision_pipeline import FrameResult

        # Mock the detector so no model is loaded
        mock_det = MagicMock()
        mock_det.detect.return_value = []
        self.pipeline._detector = mock_det

        image = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.pipeline.process_frame(image)
        self.assertIsInstance(result, FrameResult)
        self.assertIsNone(result.depth_map)
        self.assertIsNone(result.segmentation)

    def test_process_frame_calls_detector(self):
        mock_det = MagicMock()
        mock_det.detect.return_value = []
        self.pipeline._detector = mock_det

        image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.pipeline.process_frame(image)
        mock_det.detect.assert_called_once()

    def test_process_frame_disabled_detection_not_called(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline(enable_detection=False)
        mock_det = MagicMock()
        pipeline._detector = mock_det

        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = pipeline.process_frame(image)
        # Detector not called since disabled
        mock_det.detect.assert_not_called()
        self.assertEqual(result.detections, [])


class TestVisionPipelineFindObject(unittest.TestCase):
    """Test find_object with mocked CLIP."""

    def test_find_object_with_clip_disabled_enables_it(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline(enable_clip=False)
        pipeline._clip = MagicMock()
        pipeline._clip.classify = MagicMock(return_value=np.array([0.8, 0.2]))

        # enable_clip is False; find_object should flip it
        result = pipeline.find_object(np.zeros((100, 100, 3), dtype=np.uint8), "cup")
        self.assertIn("score", result)

    def test_find_object_returns_score_zero_when_no_clip(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline(enable_clip=True)
        pipeline._clip = None  # explicitly no CLIP

        result = pipeline.find_object(np.zeros((100, 100, 3), dtype=np.uint8), "chair")
        self.assertAlmostEqual(result["score"], 0.0)


class TestVisionPipelineEnableDisable(unittest.TestCase):
    """Test enable_module / disable_module."""

    def test_enable_module(self):
        from vision.vision_pipeline import VisionPipeline

        p = VisionPipeline(enable_depth=False)
        p.enable_module("depth")
        self.assertTrue(p.config.enable_depth)

    def test_disable_module(self):
        from vision.vision_pipeline import VisionPipeline

        p = VisionPipeline(enable_detection=True)
        p.disable_module("detection")
        self.assertFalse(p.config.enable_detection)

    def test_unknown_module_raises(self):
        from vision.vision_pipeline import VisionPipeline

        p = VisionPipeline()
        with self.assertRaises(ValueError):
            p.enable_module("nonexistent")


class TestVisionPipelineAnalyzeScene(unittest.TestCase):
    """Test analyze_scene with mocked sub-modules."""

    def test_analyze_scene_returns_dict(self):
        from vision.vision_pipeline import VisionPipeline

        pipeline = VisionPipeline(enable_detection=True)

        mock_det = MagicMock()
        mock_det.detect.return_value = []
        pipeline._detector = mock_det

        mock_scene = MagicMock()
        mock_scene.generate_description.return_value = "An empty scene."
        pipeline._scene_analyzer = mock_scene

        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = pipeline.analyze_scene(image)
        self.assertIsInstance(result, dict)
        self.assertIn("detections", result)
        self.assertIn("description", result)


class TestFrameResult(unittest.TestCase):
    """Test FrameResult dataclass."""

    def test_defaults(self):
        from vision.vision_pipeline import FrameResult

        img = np.zeros((10, 10, 3), dtype=np.uint8)
        fr = FrameResult(image=img)
        self.assertEqual(fr.detections, [])
        self.assertIsNone(fr.depth_map)
        self.assertEqual(fr.tracks, [])
        self.assertEqual(fr.scene_description, "")


if __name__ == "__main__":
    unittest.main()
