"""
04_tracking_demo.py — Multi-Object Tracking Demo
=================================================
Demonstrates MultiObjectTracker and ByteTracker across a sequence of
synthetic frames.  Works standalone with just numpy.
"""

from __future__ import annotations

import logging
from typing import List

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def make_synthetic_detections(
    frame_idx: int,
    num_objects: int = 3,
) -> list:
    """Generate synthetic DetectionResult objects for a frame."""
    from vision.detection.detector import DetectionResult

    rng = np.random.default_rng(frame_idx)
    results = []
    for obj_id in range(num_objects):
        # Objects move slowly across frames
        x1 = float(50 + obj_id * 150 + frame_idx * 5)
        y1 = float(50 + obj_id * 80 + frame_idx * 3)
        x2, y2 = x1 + 80.0, y1 + 60.0
        results.append(
            DetectionResult(
                bbox=(x1, y1, x2, y2),
                class_name="person",
                class_id=0,
                confidence=float(rng.uniform(0.7, 0.99)),
            )
        )
    return results


# ---------------------------------------------------------------------------
# Tracker demos
# ---------------------------------------------------------------------------


def demo_multi_object_tracker(num_frames: int = 10) -> None:
    """Run MultiObjectTracker over synthetic frames and print track IDs."""
    logger.info("--- MultiObjectTracker demo ---")
    try:
        from vision.tracking.multi_object_tracker import MultiObjectTracker

        tracker = MultiObjectTracker()
        for frame_idx in range(num_frames):
            detections = make_synthetic_detections(frame_idx)
            tracks = tracker.update(detections)
            ids = [getattr(t, "track_id", getattr(t, "id", "?")) for t in tracks]
            logger.info("Frame %2d: %d track(s) — IDs: %s", frame_idx, len(tracks), ids)
    except ImportError as exc:
        logger.warning("MultiObjectTracker skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("MultiObjectTracker error: %s", exc)


def demo_bytetracker(num_frames: int = 10) -> None:
    """Run ByteTracker over synthetic frames and print track IDs."""
    logger.info("--- ByteTracker demo ---")
    try:
        from vision.tracking.bytetrack import ByteTracker

        tracker = ByteTracker()
        for frame_idx in range(num_frames):
            detections = make_synthetic_detections(frame_idx)
            tracks = tracker.update(detections)
            ids = [getattr(t, "track_id", getattr(t, "id", "?")) for t in tracks]
            logger.info("Frame %2d: %d track(s) — IDs: %s", frame_idx, len(tracks), ids)
    except ImportError as exc:
        logger.warning("ByteTracker skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("ByteTracker error: %s", exc)


def visualise_tracks(tracks: list, image: np.ndarray, output_path: str = "/tmp/tracks.png") -> None:
    """Draw bounding boxes with track IDs on *image* and save."""
    try:
        import cv2  # type: ignore

        vis = image.copy()
        for track in tracks:
            bbox = getattr(track, "bbox", None)
            tid = getattr(track, "track_id", getattr(track, "id", 0))
            if bbox is not None:
                x1, y1, x2, y2 = (int(v) for v in bbox)
                cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(vis, f"ID:{tid}", (x1, y1 - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv2.imwrite(output_path, vis)
        logger.info("Saved track visualisation to %s", output_path)
    except ImportError:
        logger.info("cv2 not available; skipping track visualisation.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the tracking demo."""
    logger.info("=== Multi-Object Tracking Demo ===")
    demo_multi_object_tracker(num_frames=10)
    demo_bytetracker(num_frames=10)
    logger.info("=== Demo complete ===")


if __name__ == "__main__":
    main()
