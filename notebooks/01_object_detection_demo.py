"""
01_object_detection_demo.py — Object Detection Demo
====================================================
Demonstrates YOLODetector and DETRDetector with a synthetic image.
Works standalone with just numpy; vision models are loaded only when
their dependencies (ultralytics, transformers) are installed.
"""

from __future__ import annotations

import logging
import os
import sys

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Synthetic image helpers
# ---------------------------------------------------------------------------


def make_synthetic_image(height: int = 480, width: int = 640) -> np.ndarray:
    """Return a random RGB numpy image of the given size."""
    rng = np.random.default_rng(42)
    image = rng.integers(0, 256, (height, width, 3), dtype=np.uint8)
    # Add a bright rectangle to act as a pseudo-object
    image[100:200, 150:300] = [200, 50, 50]
    image[250:350, 350:500] = [50, 200, 50]
    return image


# ---------------------------------------------------------------------------
# Detector demo helpers
# ---------------------------------------------------------------------------


def demo_yolo_detector(image: np.ndarray) -> None:
    """Run YOLODetector on *image* and print results."""
    logger.info("--- YOLODetector demo ---")
    try:
        from vision.detection.yolo_detector import YOLODetector

        detector = YOLODetector(
            model_size="yolov8n",
            confidence_threshold=0.5,
            device="cpu",
        )
        detections = detector.detect(image)
        logger.info("YOLODetector found %d object(s).", len(detections))
        for det in detections[:5]:
            logger.info("  %s", det.to_dict())
    except ImportError as exc:
        logger.warning("YOLODetector skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("YOLODetector error: %s", exc)


def demo_detr_detector(image: np.ndarray) -> None:
    """Run DETRDetector on *image* and print results."""
    logger.info("--- DETRDetector demo ---")
    try:
        from vision.detection.detr_detector import DETRDetector

        detector = DETRDetector(confidence_threshold=0.5, device="cpu")
        detections = detector.detect(image)
        logger.info("DETRDetector found %d object(s).", len(detections))
        for det in detections[:5]:
            logger.info("  %s", det.to_dict())
    except ImportError as exc:
        logger.warning("DETRDetector skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("DETRDetector error: %s", exc)


def demo_draw_detections(image: np.ndarray, output_path: str = "/tmp/detections.png") -> None:
    """Draw synthetic bounding boxes on *image* and save to *output_path*."""
    logger.info("--- Visualisation demo ---")
    try:
        from vision.detection.detector import DetectionResult

        # Create synthetic detections for visualisation
        fake_dets = [
            DetectionResult(
                bbox=(150.0, 100.0, 300.0, 200.0),
                class_name="person",
                class_id=0,
                confidence=0.92,
            ),
            DetectionResult(
                bbox=(350.0, 250.0, 500.0, 350.0),
                class_name="bottle",
                class_id=39,
                confidence=0.78,
            ),
        ]

        try:
            from vision.utils.visualization import draw_detections

            annotated = draw_detections(image.copy(), fake_dets)
            try:
                import cv2  # type: ignore

                cv2.imwrite(output_path, annotated)
                logger.info("Saved annotated image to %s", output_path)
            except ImportError:
                logger.info("cv2 not available; skipping image save.")
        except ImportError as exc:
            logger.warning("draw_detections not available: %s", exc)

        logger.info("Synthetic detections: %s", [d.to_dict() for d in fake_dets])
    except Exception as exc:
        logger.error("Visualisation demo error: %s", exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the object detection demo."""
    logger.info("=== Object Detection Demo ===")
    image = make_synthetic_image()
    logger.info("Synthetic image shape: %s dtype: %s", image.shape, image.dtype)

    demo_yolo_detector(image)
    demo_detr_detector(image)
    demo_draw_detections(image)

    logger.info("=== Demo complete ===")


if __name__ == "__main__":
    main()
