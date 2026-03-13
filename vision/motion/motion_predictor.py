"""Predict future positions of tracked objects from optical flow history."""

from __future__ import annotations

import logging
from collections import deque
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class MotionPredictor:
    """Predict future object positions using velocity history.

    Maintains a short history of centre positions per track ID and
    extrapolates using a linear (constant-velocity) model.

    Example::

        predictor = MotionPredictor(history_len=5)
        predictor.update(track_id=1, position=(320, 240))
        future = predictor.predict(track_id=1, steps=3)
    """

    def __init__(self, history_len: int = 10) -> None:
        """
        Args:
            history_len: Number of past positions to retain per track.
        """
        self.history_len = history_len
        # track_id -> deque of (x, y) positions
        self._history: Dict[int, deque] = {}

    def update(
        self,
        track_id: int,
        position: Tuple[float, float],
    ) -> None:
        """Record the current position of *track_id*.

        Args:
            track_id: Unique track identifier.
            position: ``(x, y)`` centre pixel coordinates.
        """
        if track_id not in self._history:
            self._history[track_id] = deque(maxlen=self.history_len)
        self._history[track_id].append(position)

    def predict(
        self,
        track_id: int,
        steps: int = 1,
    ) -> Optional[List[Tuple[float, float]]]:
        """Predict the next *steps* positions for *track_id*.

        Uses the mean velocity over the observed history.

        Args:
            track_id: Track to predict.
            steps: Number of future frames to predict.

        Returns:
            List of ``(x, y)`` positions for the next *steps* frames,
            or ``None`` if not enough history.
        """
        history = self._history.get(track_id)
        if history is None or len(history) < 2:
            return None

        pts = np.array(list(history), dtype=np.float64)  # (N, 2)
        velocities = np.diff(pts, axis=0)  # (N-1, 2)
        mean_vel = velocities.mean(axis=0)  # (2,)

        last = pts[-1]
        predictions: List[Tuple[float, float]] = []
        for i in range(1, steps + 1):
            pos = last + mean_vel * i
            predictions.append((float(pos[0]), float(pos[1])))
        return predictions

    def update_batch(
        self, tracks: List[Tuple[int, Tuple[float, float]]]
    ) -> None:
        """Batch-update multiple tracks at once.

        Args:
            tracks: List of ``(track_id, (x, y))`` tuples.
        """
        for tid, pos in tracks:
            self.update(tid, pos)

    def predict_all(
        self, steps: int = 1
    ) -> Dict[int, Optional[List[Tuple[float, float]]]]:
        """Predict future positions for all active tracks.

        Args:
            steps: Number of frames ahead to predict.

        Returns:
            Dict mapping ``track_id`` to predicted positions list.
        """
        return {tid: self.predict(tid, steps) for tid in self._history}

    def remove_track(self, track_id: int) -> None:
        """Remove the history for *track_id*."""
        self._history.pop(track_id, None)
