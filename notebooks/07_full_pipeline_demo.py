"""
07_full_pipeline_demo.py — Full Vision Pipeline Demo
=====================================================
Initialises VisionPipeline, runs process_frame, find_object, and
analyze_scene on a synthetic image and prints the results.
Works standalone with just numpy; all modules use mocked back-ends when
their heavy dependencies are absent.
"""

from __future__ import annotations

import json
import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def make_synthetic_image(height: int = 480, width: int = 640) -> np.ndarray:
    """Return a random RGB numpy image."""
    rng = np.random.default_rng(2024)
    image = rng.integers(0, 256, (height, width, 3), dtype=np.uint8)
    # Insert colour blobs to hint at 'objects'
    image[80:180, 120:260] = [210, 40, 40]
    image[280:380, 350:490] = [40, 210, 40]
    return image


# ---------------------------------------------------------------------------
# Demo helpers
# ---------------------------------------------------------------------------


def demo_process_frame(pipeline, image: np.ndarray) -> None:
    """Call process_frame and log the result."""
    logger.info("--- process_frame ---")
    try:
        result = pipeline.process_frame(image)
        logger.info("Detections : %d", len(result.detections))
        logger.info("Depth map  : %s",
                    result.depth_map.shape if result.depth_map is not None else "N/A")
        logger.info("Tracks     : %d", len(result.tracks))
        logger.info("Poses      : %d", len(result.poses))
    except Exception as exc:
        logger.warning("process_frame error: %s", exc)


def demo_find_object(pipeline, image: np.ndarray) -> None:
    """Call find_object with a text query and log the score."""
    logger.info("--- find_object ---")
    try:
        result = pipeline.find_object(image, "red object")
        logger.info("find_object result: %s", json.dumps(result, default=str))
    except Exception as exc:
        logger.warning("find_object error: %s", exc)


def demo_analyze_scene(pipeline, image: np.ndarray) -> None:
    """Call analyze_scene and log the description."""
    logger.info("--- analyze_scene ---")
    try:
        result = pipeline.analyze_scene(image)
        logger.info("description : %s", result.get("description", ""))
        logger.info("detections  : %d object(s)", len(result.get("detections", [])))
        logger.info("depth       : %s", result.get("depth_available", False))
    except Exception as exc:
        logger.warning("analyze_scene error: %s", exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Initialise the pipeline and run all demo steps."""
    logger.info("=== Full Vision Pipeline Demo ===")

    from vision.vision_pipeline import VisionPipeline

    pipeline = VisionPipeline(
        device="cpu",
        enable_detection=True,
        enable_segmentation=False,
        enable_depth=False,
        enable_tracking=False,
        enable_pose=False,
        enable_clip=False,
    )
    logger.info("VisionPipeline initialised on device=cpu")

    image = make_synthetic_image()
    logger.info("Synthetic image shape: %s", image.shape)

    demo_process_frame(pipeline, image)
    demo_find_object(pipeline, image)
    demo_analyze_scene(pipeline, image)

    logger.info("=== Demo complete ===")


if __name__ == "__main__":
    main()
