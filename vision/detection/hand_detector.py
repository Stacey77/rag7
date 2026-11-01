"""Hand detector using MediaPipe."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class HandDetectionResult:
    """Result for a single detected hand.

    Attributes:
        bbox: Bounding box ``(x1, y1, x2, y2)`` in pixel coordinates.
        landmarks: Array of shape ``(21, 3)`` – ``(x, y, z)`` per keypoint.
        handedness: ``"Left"`` or ``"Right"``.
        confidence: Detection confidence score.
    """

    bbox: Tuple[float, float, float, float]
    landmarks: np.ndarray  # (21, 3)
    handedness: str
    confidence: float


class HandDetector:
    """Detect hands and their 21 keypoint landmarks using MediaPipe.

    Example::

        detector = HandDetector(max_hands=2)
        hands = detector.detect(image)
        for hand in hands:
            print(hand.handedness, hand.bbox)
    """

    def __init__(
        self,
        max_hands: int = 2,
        detection_confidence: float = 0.5,
        tracking_confidence: float = 0.5,
    ) -> None:
        """
        Args:
            max_hands: Maximum number of hands to detect.
            detection_confidence: Minimum confidence for detection.
            tracking_confidence: Minimum confidence for tracking.
        """
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence
        self._hands = None  # lazy

    def _load(self) -> None:
        """Lazily initialise the MediaPipe Hands solution."""
        try:
            import mediapipe as mp  # type: ignore

            mp_hands = mp.solutions.hands
            self._hands = mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=self.max_hands,
                min_detection_confidence=self.detection_confidence,
                min_tracking_confidence=self.tracking_confidence,
            )
            logger.info("Loaded MediaPipe Hands")
        except ImportError as exc:
            raise ImportError(
                "mediapipe is required for HandDetector. "
                "Install with: pip install mediapipe"
            ) from exc

    def detect(self, image: np.ndarray) -> List[HandDetectionResult]:
        """Detect hands and landmarks in *image*.

        Args:
            image: BGR numpy array of shape ``(H, W, 3)``.

        Returns:
            List of :class:`HandDetectionResult`.
        """
        if self._hands is None:
            self._load()

        try:
            h, w = image.shape[:2]
            rgb = image[..., ::-1].copy()
            result = self._hands.process(rgb)

            if not result.multi_hand_landmarks:
                return []

            detections: List[HandDetectionResult] = []
            handedness_list = result.multi_handedness or []
            for idx, hand_lms in enumerate(result.multi_hand_landmarks):
                xs = [lm.x * w for lm in hand_lms.landmark]
                ys = [lm.y * h for lm in hand_lms.landmark]
                zs = [lm.z for lm in hand_lms.landmark]
                landmarks = np.stack([xs, ys, zs], axis=1).astype(np.float32)

                x1, y1 = float(min(xs)), float(min(ys))
                x2, y2 = float(max(xs)), float(max(ys))

                side = "Right"
                conf = 0.0
                if idx < len(handedness_list):
                    classification = handedness_list[idx].classification[0]
                    side = classification.label
                    conf = float(classification.score)

                detections.append(
                    HandDetectionResult(
                        bbox=(x1, y1, x2, y2),
                        landmarks=landmarks,
                        handedness=side,
                        confidence=conf,
                    )
                )
            return detections
        except Exception as exc:
            logger.error("HandDetector.detect failed: %s", exc)
            return []

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._hands is not None:
            self._hands.close()
            self._hands = None
