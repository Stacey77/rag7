"""
02_segmentation_demo.py — Segmentation Demo
============================================
Demonstrates SemanticSegmentor, InstanceSegmentor, and SAMSegmentor with a
synthetic image.  Works standalone with just numpy; heavy models are loaded
only when their dependencies are installed.
"""

from __future__ import annotations

import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def make_synthetic_image(height: int = 480, width: int = 640) -> np.ndarray:
    """Return a random RGB numpy image with some structure."""
    rng = np.random.default_rng(7)
    image = rng.integers(0, 256, (height, width, 3), dtype=np.uint8)
    image[50:200, 100:300] = [180, 60, 60]
    image[250:400, 320:520] = [60, 180, 60]
    return image


# ---------------------------------------------------------------------------
# Segmentor demos
# ---------------------------------------------------------------------------


def demo_semantic_segmentor(image: np.ndarray) -> None:
    """Run SemanticSegmentor and report output shape."""
    logger.info("--- SemanticSegmentor demo ---")
    try:
        from vision.segmentation.semantic_segmentor import SemanticSegmentor

        segmentor = SemanticSegmentor(device="cpu")
        mask = segmentor.segment(image)
        logger.info("Semantic mask shape: %s  dtype: %s", mask.shape, mask.dtype)
        logger.info("Unique class IDs in mask: %s", np.unique(mask).tolist())
    except ImportError as exc:
        logger.warning("SemanticSegmentor skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("SemanticSegmentor error: %s", exc)


def demo_instance_segmentor(image: np.ndarray) -> None:
    """Run InstanceSegmentor and report detected instances."""
    logger.info("--- InstanceSegmentor demo ---")
    try:
        from vision.segmentation.instance_segmentor import InstanceSegmentor

        segmentor = InstanceSegmentor(device="cpu")
        instances = segmentor.segment(image)
        logger.info("Instance segmentor returned: %s (type: %s)", instances, type(instances))
    except ImportError as exc:
        logger.warning("InstanceSegmentor skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("InstanceSegmentor error: %s", exc)


def demo_sam_segmentor(image: np.ndarray) -> None:
    """Run SAMSegmentor with a synthetic point prompt."""
    logger.info("--- SAMSegmentor demo ---")
    try:
        from vision.segmentation.sam_segmentor import SAMSegmentor

        segmentor = SAMSegmentor(device="cpu")
        # Point prompt at the centre of the image
        h, w = image.shape[:2]
        point = np.array([[w // 2, h // 2]], dtype=np.float32)
        result = segmentor.segment(image, point_coords=point)
        logger.info("SAM result type: %s", type(result))
    except ImportError as exc:
        logger.warning("SAMSegmentor skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("SAMSegmentor error: %s", exc)


def visualise_mask(mask: np.ndarray, output_path: str = "/tmp/segmentation.png") -> None:
    """Save a colour-coded segmentation mask to *output_path*."""
    try:
        import cv2  # type: ignore

        # Normalise mask to 0-255 for visualisation
        vis = (mask.astype(np.float32) / max(mask.max(), 1) * 255).astype(np.uint8)
        cv2.imwrite(output_path, vis)
        logger.info("Saved mask visualisation to %s", output_path)
    except ImportError:
        logger.info("cv2 not available; skipping mask save.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the segmentation demo."""
    logger.info("=== Segmentation Demo ===")
    image = make_synthetic_image()
    logger.info("Synthetic image shape: %s", image.shape)

    demo_semantic_segmentor(image)
    demo_instance_segmentor(image)
    demo_sam_segmentor(image)

    # Visualise a synthetic mask
    synthetic_mask = np.zeros((480, 640), dtype=np.uint8)
    synthetic_mask[50:200, 100:300] = 1
    synthetic_mask[250:400, 320:520] = 2
    visualise_mask(synthetic_mask)

    logger.info("=== Demo complete ===")


if __name__ == "__main__":
    main()
