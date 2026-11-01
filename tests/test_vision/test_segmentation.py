"""Tests for segmentation module."""

import unittest
from unittest.mock import MagicMock, patch
import numpy as np

try:
    import torch
    import torchvision
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class TestSemanticSegmentor(unittest.TestCase):
    """Tests for SemanticSegmentor (mocked model)."""

    @unittest.skipUnless(TORCH_AVAILABLE, "torch not installed")
    @patch("vision.segmentation.semantic_segmentor.SemanticSegmentor._load_model")
    def test_segment_returns_correct_shape(self, mock_load):
        from vision.segmentation.semantic_segmentor import SemanticSegmentor
        import torch

        seg = SemanticSegmentor()
        # Simulate model output
        h, w = 240, 320
        fake_output = torch.zeros(1, 21, h, w)
        fake_output[0, 5, :, :] = 1.0  # class 5 everywhere

        model_mock = MagicMock()
        model_mock.return_value = {"out": fake_output}
        seg._model = model_mock

        import torchvision.transforms as T
        seg._transform = T.Compose([T.ToTensor()])

        image = np.zeros((h, w, 3), dtype=np.uint8)
        result = seg.segment(image)
        self.assertEqual(result.shape[:2], (h, w))
        self.assertEqual(result.dtype, np.int32)

    def test_get_class_name_valid(self):
        from vision.segmentation.semantic_segmentor import SemanticSegmentor, VOC_CLASSES

        seg = SemanticSegmentor()
        self.assertEqual(seg.get_class_name(0), "background")
        self.assertEqual(seg.get_class_name(15), "person")

    def test_get_class_name_invalid(self):
        from vision.segmentation.semantic_segmentor import SemanticSegmentor

        seg = SemanticSegmentor()
        name = seg.get_class_name(999)
        self.assertIn("999", name)

    def test_colorize_returns_bgr(self):
        from vision.segmentation.semantic_segmentor import SemanticSegmentor

        seg = SemanticSegmentor()
        seg_map = np.array([[0, 1], [2, 5]], dtype=np.int32)
        coloured = seg.colorize(seg_map)
        self.assertEqual(coloured.shape, (2, 2, 3))
        self.assertEqual(coloured.dtype, np.uint8)

    @patch("vision.segmentation.semantic_segmentor.SemanticSegmentor._load_model")
    def test_segment_falls_back_on_error(self, mock_load):
        from vision.segmentation.semantic_segmentor import SemanticSegmentor

        seg = SemanticSegmentor()
        seg._model = MagicMock(side_effect=RuntimeError("test"))
        seg._transform = MagicMock(return_value=MagicMock())

        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = seg.segment(image)
        self.assertEqual(result.shape, (100, 100))
        self.assertTrue((result == 0).all())

    def test_invalid_backbone_defaults(self):
        from vision.segmentation.semantic_segmentor import SemanticSegmentor

        seg = SemanticSegmentor(backbone="nonexistent")
        self.assertEqual(seg.backbone, "resnet50")


class TestInstanceSegmentor(unittest.TestCase):
    """Tests for InstanceSegmentor (mocked model)."""

    def test_init_defaults(self):
        from vision.segmentation.instance_segmentor import InstanceSegmentor

        seg = InstanceSegmentor()
        self.assertEqual(seg.score_threshold, 0.5)
        self.assertEqual(seg.device, "cpu")

    @unittest.skipUnless(TORCH_AVAILABLE, "torch not installed")
    @patch("vision.segmentation.instance_segmentor.InstanceSegmentor._load_model")
    def test_segment_returns_list(self, mock_load):
        import torch
        from vision.segmentation.instance_segmentor import InstanceSegmentor

        seg = InstanceSegmentor(score_threshold=0.5)
        h, w = 100, 100

        fake_output = {
            "boxes": torch.tensor([[10., 10., 50., 50.], [20., 20., 60., 60.]]),
            "labels": torch.tensor([1, 3]),
            "scores": torch.tensor([0.9, 0.4]),
            "masks": torch.zeros(2, 1, h, w),
        }
        fake_output["masks"][0, 0, 20:40, 20:40] = 1.0

        seg._model = MagicMock(return_value=[fake_output])

        import torchvision.transforms as T
        seg._transform = T.ToTensor()

        image = np.zeros((h, w, 3), dtype=np.uint8)
        result = seg.segment(image)
        self.assertIsInstance(result, list)
        # Only score >= 0.5 should be returned (index 0)
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result[0].score, 0.5)

    @patch("vision.segmentation.instance_segmentor.InstanceSegmentor._load_model")
    def test_segment_empty_on_error(self, mock_load):
        from vision.segmentation.instance_segmentor import InstanceSegmentor

        seg = InstanceSegmentor()
        seg._model = MagicMock(side_effect=RuntimeError("boom"))
        seg._transform = MagicMock()

        result = seg.segment(np.zeros((100, 100, 3), dtype=np.uint8))
        self.assertEqual(result, [])


class TestInstanceMask(unittest.TestCase):
    """Test InstanceMask dataclass."""

    def test_fields(self):
        from vision.segmentation.instance_segmentor import InstanceMask

        mask = np.ones((50, 50), dtype=np.uint8)
        inst = InstanceMask(
            mask=mask,
            class_name="person",
            class_id=1,
            score=0.88,
            bbox=(10.0, 10.0, 60.0, 60.0),
        )
        self.assertEqual(inst.class_name, "person")
        self.assertAlmostEqual(inst.score, 0.88)
        self.assertEqual(inst.mask.shape, (50, 50))


class TestSAMSegmentor(unittest.TestCase):
    """Smoke tests for SAMSegmentor interface."""

    def test_init(self):
        from vision.segmentation.sam_segmentor import SAMSegmentor

        sam = SAMSegmentor(device="cpu")
        self.assertEqual(sam.device, "cpu")
        self.assertIsNone(sam._predictor)
        self.assertIsNone(sam._hf_model)

    @patch("vision.segmentation.sam_segmentor.SAMSegmentor._load")
    def test_segment_with_points_returns_list(self, mock_load):
        from vision.segmentation.sam_segmentor import SAMSegmentor

        sam = SAMSegmentor()
        sam._use_hf = False
        sam._predictor = MagicMock()

        h, w = 100, 100
        fake_mask = np.zeros((h, w), dtype=np.uint8)
        sam._predictor.set_image = MagicMock()
        sam._sam_predict_points = MagicMock(return_value=[fake_mask])

        image = np.zeros((h, w, 3), dtype=np.uint8)
        result = sam.segment_with_points(image, points=[(50, 50)])
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
