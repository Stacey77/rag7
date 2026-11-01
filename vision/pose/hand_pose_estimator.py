"""Hand pose estimator with gesture recognition using MediaPipe."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Finger tip landmark IDs in MediaPipe Hand model
_TIP_IDS = [4, 8, 12, 16, 20]   # thumb, index, middle, ring, pinky
_MCP_IDS = [2, 5, 9, 13, 17]    # MCP joints for finger-open heuristic


@dataclass
class HandPoseResult:
    """Pose result for a single hand.

    Attributes:
        landmarks: Array of shape ``(21, 3)`` – ``(x, y, z)`` per keypoint.
        handedness: ``"Left"`` or ``"Right"``.
        gesture: Recognised gesture string.
        confidence: Detection confidence.
    """

    landmarks: np.ndarray  # (21, 3)
    handedness: str
    gesture: str
    confidence: float


class HandPoseEstimator:
    """Estimate hand keypoints and recognise gestures using MediaPipe Hands.

    Returns 21 hand landmarks per detected hand.

    Example::

        estimator = HandPoseEstimator(max_hands=2)
        results = estimator.detect(image)
        for r in results:
            print(r.gesture, r.handedness)
    """

    def __init__(
        self,
        max_hands: int = 2,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
    ) -> None:
        """
        Args:
            max_hands: Maximum number of hands to detect per frame.
            detection_confidence: Minimum detection confidence.
            tracking_confidence: Minimum tracking confidence.
        """
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        self._hands = None  # lazy

    def _load(self) -> None:
        """Lazily load MediaPipe Hands."""
        try:
            import mediapipe as mp  # type: ignore

            self._hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=self.max_hands,
                min_detection_confidence=self.detection_confidence,
                min_tracking_confidence=self.tracking_confidence,
            )
            logger.info("Loaded MediaPipe Hands for pose estimation")
        except ImportError as exc:
            raise ImportError(
                "mediapipe is required for HandPoseEstimator. "
                "Install with: pip install mediapipe"
            ) from exc

    def detect(self, image: np.ndarray) -> List[HandPoseResult]:
        """Detect hands and recognise gestures in *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of :class:`HandPoseResult`.
        """
        if self._hands is None:
            self._load()

        try:
            h, w = image.shape[:2]
            rgb = image[..., ::-1].copy()
            output = self._hands.process(rgb)

            if not output.multi_hand_landmarks:
                return []

            results: List[HandPoseResult] = []
            handedness_list = output.multi_handedness or []

            for idx, hand_lms in enumerate(output.multi_hand_landmarks):
                xs = [lm.x * w for lm in hand_lms.landmark]
                ys = [lm.y * h for lm in hand_lms.landmark]
                zs = [lm.z for lm in hand_lms.landmark]
                landmarks = np.stack([xs, ys, zs], axis=1).astype(np.float32)

                side, conf = "Right", 0.0
                if idx < len(handedness_list):
                    cls = handedness_list[idx].classification[0]
                    side = cls.label
                    conf = float(cls.score)

                gesture = self.classify_gesture(landmarks)
                results.append(
                    HandPoseResult(
                        landmarks=landmarks,
                        handedness=side,
                        gesture=gesture,
                        confidence=conf,
                    )
                )
            return results
        except Exception as exc:
            logger.error("HandPoseEstimator.detect failed: %s", exc)
            return []

    def classify_gesture(self, landmarks: np.ndarray) -> str:
        """Classify a gesture from 21 hand landmarks.

        Args:
            landmarks: Array of shape ``(21, 3)`` – ``(x, y, z)``.

        Returns:
            One of ``"open"``, ``"fist"``, ``"thumbs_up"``, ``"peace"``,
            ``"ok"``, or ``"unknown"``.
        """
        try:
            tips = landmarks[_TIP_IDS]
            mcps = landmarks[_MCP_IDS]
            wrist = landmarks[0]

            # Finger is extended if tip is farther from wrist than MCP
            extended = np.linalg.norm(tips - wrist, axis=1) > np.linalg.norm(mcps - wrist, axis=1)
            # extended = [thumb, index, middle, ring, pinky]

            if extended.sum() == 5:
                return "open"
            if extended.sum() == 0:
                return "fist"

            # Thumbs-up: only thumb extended
            if extended[0] and not any(extended[1:]):
                return "thumbs_up"

            # Peace: index + middle extended
            if not extended[0] and extended[1] and extended[2] and not extended[3] and not extended[4]:
                return "peace"

            # OK: thumb + index close (simplified)
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            if np.linalg.norm(thumb_tip - index_tip) < 30:
                return "ok"

            return "unknown"
        except Exception:
            return "unknown"

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._hands is not None:
            self._hands.close()
            self._hands = None
