"""
03_depth_estimation_demo.py — Depth Estimation Demo
=====================================================
Demonstrates MonocularDepthEstimator and PointCloudGenerator with a synthetic
image.  Works standalone with just numpy; heavy models load only when their
dependencies (torch, timm) are installed.
"""

from __future__ import annotations

import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def make_synthetic_image(height: int = 480, width: int = 640) -> np.ndarray:
    """Return a random RGB numpy image."""
    rng = np.random.default_rng(99)
    return rng.integers(0, 256, (height, width, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# Depth demo helpers
# ---------------------------------------------------------------------------


def demo_monocular_depth(image: np.ndarray) -> np.ndarray:
    """Run MonocularDepthEstimator and return (or synthesise) a depth map."""
    logger.info("--- MonocularDepthEstimator demo ---")
    try:
        from vision.depth.depth_estimator import MonocularDepthEstimator

        estimator = MonocularDepthEstimator(model_name="midas", device="cpu")
        depth_map = estimator.estimate(image)
        logger.info("Depth map shape: %s  min: %.3f  max: %.3f",
                    depth_map.shape, float(depth_map.min()), float(depth_map.max()))
        return depth_map
    except ImportError as exc:
        logger.warning("MonocularDepthEstimator skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("MonocularDepthEstimator error: %s", exc)

    # Fallback: synthetic depth map
    h, w = image.shape[:2]
    rng = np.random.default_rng(0)
    depth_map = rng.random((h, w)).astype(np.float32) * 10.0  # 0–10 m
    logger.info("Using synthetic depth map: shape=%s", depth_map.shape)
    return depth_map


def demo_pointcloud(image: np.ndarray, depth_map: np.ndarray) -> None:
    """Run PointCloudGenerator and report cloud shape."""
    logger.info("--- PointCloudGenerator demo ---")
    try:
        from vision.depth.pointcloud_generator import PointCloudGenerator

        # Simple pinhole intrinsics
        fx = fy = 525.0
        cx, cy = image.shape[1] / 2.0, image.shape[0] / 2.0
        generator = PointCloudGenerator(fx=fx, fy=fy, cx=cx, cy=cy)
        cloud = generator.generate(depth_map)
        logger.info("Point cloud shape: %s", cloud.shape)
    except ImportError as exc:
        logger.warning("PointCloudGenerator skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("PointCloudGenerator error: %s", exc)


def visualise_depth(depth_map: np.ndarray, output_path: str = "/tmp/depth.png") -> None:
    """Save a normalised depth visualisation to *output_path*."""
    try:
        import cv2  # type: ignore

        depth_norm = (depth_map - depth_map.min()) / (depth_map.ptp() + 1e-8)
        depth_uint8 = (depth_norm * 255).astype(np.uint8)
        depth_colour = cv2.applyColorMap(depth_uint8, cv2.COLORMAP_JET)
        cv2.imwrite(output_path, depth_colour)
        logger.info("Saved depth visualisation to %s", output_path)
    except ImportError:
        logger.info("cv2 not available; skipping depth save.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the depth estimation demo."""
    logger.info("=== Depth Estimation Demo ===")
    image = make_synthetic_image()
    logger.info("Synthetic image shape: %s", image.shape)

    depth_map = demo_monocular_depth(image)
    demo_pointcloud(image, depth_map)
    visualise_depth(depth_map)

    logger.info("=== Demo complete ===")


if __name__ == "__main__":
    main()
