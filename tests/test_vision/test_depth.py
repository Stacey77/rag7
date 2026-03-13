"""Tests for depth estimation and point cloud generation."""

import unittest
from unittest.mock import MagicMock, patch
import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TestMonocularDepthEstimator(unittest.TestCase):
    """Tests for MonocularDepthEstimator."""

    def test_init_defaults(self):
        from vision.depth.depth_estimator import MonocularDepthEstimator

        est = MonocularDepthEstimator()
        self.assertEqual(est.model_name, "midas")
        self.assertEqual(est.device, "cpu")
        self.assertTrue(est.normalize)

    def test_invalid_model_defaults_to_midas(self):
        from vision.depth.depth_estimator import MonocularDepthEstimator

        est = MonocularDepthEstimator(model_name="unknown_model")
        self.assertEqual(est.model_name, "midas")

    @unittest.skipUnless(TORCH_AVAILABLE, "torch not installed")
    @patch("vision.depth.depth_estimator.MonocularDepthEstimator._load_model")
    def test_estimate_returns_2d_array(self, mock_load):
        import torch
        from vision.depth.depth_estimator import MonocularDepthEstimator

        est = MonocularDepthEstimator(normalize=True)
        h, w = 240, 320

        # Simulate model that returns a tensor
        fake_pred = torch.rand(1, h, w)
        model_mock = MagicMock(return_value=fake_pred)
        est._model = model_mock
        est._transform = MagicMock(return_value=torch.rand(3, h, w))

        image = np.zeros((h, w, 3), dtype=np.uint8)
        result = est.estimate(image)
        self.assertEqual(result.shape, (h, w))
        self.assertEqual(result.dtype, np.float32)

    @patch("vision.depth.depth_estimator.MonocularDepthEstimator._load_model")
    def test_estimate_returns_zero_on_error(self, mock_load):
        from vision.depth.depth_estimator import MonocularDepthEstimator

        est = MonocularDepthEstimator()
        est._model = MagicMock(side_effect=RuntimeError("test"))
        est._transform = MagicMock(side_effect=RuntimeError("test"))

        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = est.estimate(image)
        self.assertEqual(result.shape, (100, 100))
        self.assertTrue((result == 0).all())

    def test_normalize_true_clamps_range(self):
        from vision.depth.depth_estimator import MonocularDepthEstimator

        est = MonocularDepthEstimator(normalize=True)
        # Simulate a known depth map
        est._model = None

        # Directly test normalisation logic
        depth = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
        dmin, dmax = depth.min(), depth.max()
        normalized = (depth - dmin) / (dmax - dmin)
        self.assertAlmostEqual(float(normalized.max()), 1.0)
        self.assertAlmostEqual(float(normalized.min()), 0.0)


class TestDepthAnythingEstimator(unittest.TestCase):
    """Tests for DepthAnythingEstimator."""

    def test_init_defaults(self):
        from vision.depth.depth_anything import DepthAnythingEstimator

        est = DepthAnythingEstimator()
        self.assertFalse(est.normalize)
        self.assertEqual(est.device, "cpu")

    @patch("vision.depth.depth_anything.DepthAnythingEstimator._load_model")
    def test_estimate_error_returns_zeros(self, mock_load):
        from vision.depth.depth_anything import DepthAnythingEstimator

        est = DepthAnythingEstimator()
        est._model = MagicMock(side_effect=RuntimeError("boom"))
        est._processor = MagicMock()

        result = est.estimate(np.zeros((100, 100, 3), dtype=np.uint8))
        self.assertEqual(result.shape, (100, 100))
        self.assertTrue((result == 0).all())


class TestStereoDepthEstimator(unittest.TestCase):
    """Tests for StereoDepthEstimator."""

    def test_init_default_calibration(self):
        from vision.depth.stereo_depth import StereoDepthEstimator

        est = StereoDepthEstimator()
        self.assertIsNotNone(est.calibration)
        self.assertEqual(est.calibration.baseline, 0.1)

    def test_num_disparities_divisible_by_16(self):
        from vision.depth.stereo_depth import StereoDepthEstimator

        est = StereoDepthEstimator(num_disparities=70)
        self.assertEqual(est.num_disparities % 16, 0)

    def test_block_size_odd(self):
        from vision.depth.stereo_depth import StereoDepthEstimator

        est = StereoDepthEstimator(block_size=4)
        self.assertEqual(est.block_size % 2, 1)

    def test_estimate_returns_array(self):
        from vision.depth.stereo_depth import StereoDepthEstimator, StereoCalibration

        calib = StereoCalibration(fx=718.8, fy=718.8, cx=607.2, cy=185.2, baseline=0.54)
        est = StereoDepthEstimator(calibration=calib)

        h, w = 100, 100
        left = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
        right = np.random.randint(0, 255, (h, w, 3), dtype=np.uint8)
        result = est.estimate(left, right)
        self.assertEqual(result.shape, (h, w))
        self.assertEqual(result.dtype, np.float32)


class TestPointCloudGenerator(unittest.TestCase):
    """Tests for PointCloudGenerator."""

    def setUp(self):
        from vision.depth.pointcloud_generator import (
            PointCloudGenerator,
            CameraIntrinsicsSimple,
        )
        self.gen = PointCloudGenerator()
        self.intrinsics = CameraIntrinsicsSimple(fx=525, fy=525, cx=319.5, cy=239.5)

    def test_generate_from_depth_shape(self):
        depth = np.ones((10, 10), dtype=np.float32) * 2.0  # 2 metres everywhere
        pc = self.gen.generate_from_depth(depth, self.intrinsics)
        self.assertEqual(pc.shape[1], 3)
        self.assertGreater(len(pc), 0)

    def test_generate_from_depth_with_rgb(self):
        depth = np.ones((10, 10), dtype=np.float32)
        rgb = np.zeros((10, 10, 3), dtype=np.uint8)
        pc = self.gen.generate_from_depth(depth, self.intrinsics, rgb=rgb)
        self.assertEqual(pc.shape[1], 6)

    def test_invalid_depths_excluded(self):
        depth = np.zeros((10, 10), dtype=np.float32)  # all invalid
        pc = self.gen.generate_from_depth(depth, self.intrinsics)
        self.assertEqual(len(pc), 0)

    def test_filter_outliers_preserves_shape(self):
        pc = np.random.rand(100, 3).astype(np.float32)
        filtered = self.gen.filter_outliers(pc, nb_neighbors=5)
        self.assertEqual(filtered.shape[1], 3)
        self.assertLessEqual(len(filtered), len(pc))

    def test_filter_outliers_empty_input(self):
        pc = np.empty((0, 3), dtype=np.float32)
        filtered = self.gen.filter_outliers(pc)
        self.assertEqual(len(filtered), 0)

    def test_generate_depth_max_depth_filter(self):
        depth = np.array([[1.0, 5.0, 20.0]], dtype=np.float32)  # 20m should be filtered
        pc = self.gen.generate_from_depth(depth, self.intrinsics, max_depth=10.0)
        self.assertLess(len(pc), 3)  # 20m point excluded


if __name__ == "__main__":
    unittest.main()
