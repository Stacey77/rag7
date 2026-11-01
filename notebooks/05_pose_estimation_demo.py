"""
05_pose_estimation_demo.py — Pose Estimation Demo
==================================================
Demonstrates HumanPoseEstimator and HandPoseEstimator with a synthetic image.
Works standalone with just numpy; heavy models load only when their
dependencies (mediapipe, mmpose, etc.) are installed.
"""

from __future__ import annotations

import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def make_synthetic_image(height: int = 480, width: int = 640) -> np.ndarray:
    """Return a random RGB numpy image."""
    rng = np.random.default_rng(17)
    return rng.integers(0, 256, (height, width, 3), dtype=np.uint8)


# ---------------------------------------------------------------------------
# Pose demo helpers
# ---------------------------------------------------------------------------


def demo_human_pose(image: np.ndarray) -> None:
    """Run HumanPoseEstimator and log keypoint information."""
    logger.info("--- HumanPoseEstimator demo ---")
    try:
        from vision.pose.human_pose_estimator import HumanPoseEstimator

        estimator = HumanPoseEstimator(device="cpu")
        poses = estimator.detect_poses(image)
        logger.info("Detected %d human pose(s).", len(poses))
        for i, pose in enumerate(poses[:3]):
            kpts = getattr(pose, "keypoints", None)
            logger.info("  Pose %d: keypoints=%s", i, kpts.shape if kpts is not None else "N/A")
    except ImportError as exc:
        logger.warning("HumanPoseEstimator skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("HumanPoseEstimator error: %s", exc)


def demo_hand_pose(image: np.ndarray) -> None:
    """Run HandPoseEstimator and log hand landmark information."""
    logger.info("--- HandPoseEstimator demo ---")
    try:
        from vision.pose.hand_pose_estimator import HandPoseEstimator

        estimator = HandPoseEstimator(device="cpu")
        hands = estimator.detect_hands(image)
        logger.info("Detected %d hand(s).", len(hands))
        for i, hand in enumerate(hands[:3]):
            logger.info("  Hand %d: %s", i, hand)
    except ImportError as exc:
        logger.warning("HandPoseEstimator skipped (missing deps): %s", exc)
    except Exception as exc:
        logger.warning("HandPoseEstimator error: %s", exc)


def visualise_skeleton(
    image: np.ndarray,
    keypoints: np.ndarray,
    output_path: str = "/tmp/skeleton.png",
) -> None:
    """Draw skeleton keypoints on *image* and save to *output_path*."""
    try:
        import cv2  # type: ignore

        vis = image.copy()
        for kp in keypoints:
            x, y = int(kp[0]), int(kp[1])
            cv2.circle(vis, (x, y), 4, (0, 255, 255), -1)
        cv2.imwrite(output_path, vis)
        logger.info("Saved skeleton visualisation to %s", output_path)
    except ImportError:
        logger.info("cv2 not available; skipping skeleton save.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the pose estimation demo."""
    logger.info("=== Pose Estimation Demo ===")
    image = make_synthetic_image()
    logger.info("Synthetic image shape: %s", image.shape)

    demo_human_pose(image)
    demo_hand_pose(image)

    # Visualise synthetic skeleton
    rng = np.random.default_rng(42)
    synthetic_kpts = rng.uniform(50, 430, (17, 2)).astype(np.float32)
    visualise_skeleton(image, synthetic_kpts)

    logger.info("=== Demo complete ===")


if __name__ == "__main__":
    main()
