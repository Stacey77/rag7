"""Human pose estimator using MediaPipe Pose."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# MediaPipe landmark indices for key joints
_KEYPOINT_NAMES = [
    "nose", "left_eye_inner", "left_eye", "left_eye_outer",
    "right_eye_inner", "right_eye", "right_eye_outer",
    "left_ear", "right_ear", "mouth_left", "mouth_right",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_pinky", "right_pinky",
    "left_index", "right_index", "left_thumb", "right_thumb",
    "left_hip", "right_hip", "left_knee", "right_knee",
    "left_ankle", "right_ankle", "left_heel", "right_heel",
    "left_foot_index", "right_foot_index",
]

# Simplified 17-keypoint subset (COCO-compatible)
COCO_KEYPOINTS_17 = [0, 2, 5, 7, 8, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]


@dataclass
class PoseResult:
    """Result for a single person's pose.

    Attributes:
        keypoints: Array of shape ``(17, 3)`` – ``(x, y, visibility)``.
        bbox: Bounding box ``(x1, y1, x2, y2)`` in pixels.
        score: Overall pose confidence.
        action: Optional recognised action label.
    """

    keypoints: np.ndarray  # (17, 3)
    bbox: Tuple[float, float, float, float]
    score: float
    action: Optional[str] = None


class HumanPoseEstimator:
    """Detect human body poses using MediaPipe Pose.

    Returns 17 COCO-compatible keypoints per person.

    Example::

        estimator = HumanPoseEstimator()
        poses = estimator.detect_poses(image)
        for pose in poses:
            print(pose.action, pose.score)
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        model_complexity: int = 1,
        device: str = "cpu",
    ) -> None:
        """
        Args:
            min_detection_confidence: Detection confidence threshold.
            min_tracking_confidence: Tracking confidence threshold.
            model_complexity: MediaPipe model complexity (0, 1, or 2).
            device: Not directly used; kept for interface consistency.
        """
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.model_complexity = model_complexity
        self.device = device
        self._pose = None  # lazy

    def _load(self) -> None:
        """Lazily load MediaPipe Pose."""
        try:
            import mediapipe as mp  # type: ignore

            mp_pose = mp.solutions.pose
            self._pose = mp_pose.Pose(
                static_image_mode=False,
                model_complexity=self.model_complexity,
                min_detection_confidence=self.min_detection_confidence,
                min_tracking_confidence=self.min_tracking_confidence,
            )
            logger.info("Loaded MediaPipe Pose (complexity=%d)", self.model_complexity)
        except ImportError as exc:
            raise ImportError(
                "mediapipe is required for HumanPoseEstimator. "
                "Install with: pip install mediapipe"
            ) from exc

    def detect_poses(self, image: np.ndarray) -> List[PoseResult]:
        """Detect poses in *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of :class:`PoseResult`.  MediaPipe Pose detects at most
            one person per call; extend with a person-detection loop for
            multi-person scenarios.
        """
        if self._pose is None:
            self._load()

        try:
            h, w = image.shape[:2]
            rgb = image[..., ::-1].copy()
            results = self._pose.process(rgb)

            if not results.pose_landmarks:
                return []

            lms = results.pose_landmarks.landmark
            all_kps = np.array(
                [[lm.x * w, lm.y * h, lm.visibility] for lm in lms],
                dtype=np.float32,
            )  # (33, 3)

            # Downsample to 17 COCO keypoints
            kps_17 = all_kps[COCO_KEYPOINTS_17]  # (17, 3)

            xs = kps_17[:, 0]
            ys = kps_17[:, 1]
            bbox = (float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max()))
            score = float(kps_17[:, 2].mean())

            action = self.classify_action(kps_17)

            return [PoseResult(keypoints=kps_17, bbox=bbox, score=score, action=action)]
        except Exception as exc:
            logger.error("HumanPoseEstimator.detect_poses failed: %s", exc)
            return []

    def classify_action(self, keypoints: np.ndarray) -> str:
        """Heuristic action classification from 17 keypoints.

        Args:
            keypoints: Array of shape ``(17, 3)`` in ``(x, y, visibility)``.

        Returns:
            One of ``"standing"``, ``"sitting"``, ``"lying"``, or ``"unknown"``.
        """
        try:
            # Hip = index 11/12, ankle = index 15/16 in 17-kp layout
            left_hip_y = keypoints[11, 1]
            left_ankle_y = keypoints[15, 1]
            right_hip_y = keypoints[12, 1]
            right_ankle_y = keypoints[16, 1]
            nose_y = keypoints[0, 1]

            hip_y = (left_hip_y + right_hip_y) / 2
            ankle_y = (left_ankle_y + right_ankle_y) / 2

            vertical_span = abs(ankle_y - nose_y)
            hip_to_ankle = abs(ankle_y - hip_y)

            if vertical_span < 60:
                return "lying"
            if hip_to_ankle < vertical_span * 0.35:
                return "sitting"
            return "standing"
        except Exception:
            return "unknown"

    def is_fallen(self, keypoints: np.ndarray) -> bool:
        """Detect whether the person has fallen.

        Args:
            keypoints: Array of shape ``(17, 3)``.

        Returns:
            ``True`` if the pose indicates a fall.
        """
        action = self.classify_action(keypoints)
        return action == "lying"

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._pose is not None:
            self._pose.close()
            self._pose = None
