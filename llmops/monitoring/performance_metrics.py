"""Performance metrics tracking for LLM models over time."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

import numpy as np
from loguru import logger


@dataclass
class MetricSnapshot:
    """A snapshot of model performance metrics at a point in time.

    Attributes:
        accuracy: Fraction of correct predictions.
        precision: Precision score (TP / (TP + FP)).
        recall: Recall score (TP / (TP + FN)).
        f1_score: Harmonic mean of precision and recall.
        auc_roc: Area under the ROC curve.
        n_samples: Number of evaluation samples.
        recorded_at: UTC timestamp of the snapshot.
        model_id: Identifier of the evaluated model.
    """

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    n_samples: int
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    model_id: str = "default"


class PerformanceMetrics:
    """Track and compute model performance metrics over time.

    Accumulates per-prediction labels and scores to compute standard
    classification metrics, and retains a time-series history of
    :class:`MetricSnapshot` objects for trend analysis.

    Attributes:
        history: Ordered list of metric snapshots.
        _y_true: Accumulated ground-truth labels.
        _y_pred: Accumulated predicted labels.
        _y_scores: Accumulated probability scores for AUC computation.
    """

    def __init__(self) -> None:
        """Initialise the performance metrics tracker."""
        self.history: list[MetricSnapshot] = []
        self._y_true: list[int] = []
        self._y_pred: list[int] = []
        self._y_scores: list[float] = []
        logger.info("PerformanceMetrics initialised")

    def record_prediction(
        self,
        y_true: int,
        y_pred: int,
        y_score: float | None = None,
    ) -> None:
        """Record a single prediction for metric accumulation.

        Args:
            y_true: Ground-truth label (0 or 1).
            y_pred: Predicted label (0 or 1).
            y_score: Optional probability score for the positive class (0–1).

        Raises:
            ValueError: If labels are not 0 or 1, or if score is outside [0, 1].
        """
        if y_true not in (0, 1):
            raise ValueError(f"y_true must be 0 or 1, got {y_true}")
        if y_pred not in (0, 1):
            raise ValueError(f"y_pred must be 0 or 1, got {y_pred}")
        if y_score is not None and not 0.0 <= y_score <= 1.0:
            raise ValueError(f"y_score must be in [0, 1], got {y_score}")

        self._y_true.append(y_true)
        self._y_pred.append(y_pred)
        self._y_scores.append(y_score if y_score is not None else float(y_pred))

    def record_batch(
        self,
        y_true: list[int],
        y_pred: list[int],
        y_scores: list[float] | None = None,
    ) -> None:
        """Record a batch of predictions.

        Args:
            y_true: List of ground-truth labels.
            y_pred: List of predicted labels.
            y_scores: Optional list of probability scores.

        Raises:
            ValueError: If lengths of input lists do not match.
        """
        if len(y_true) != len(y_pred):
            raise ValueError(
                f"Length mismatch: y_true={len(y_true)}, y_pred={len(y_pred)}"
            )
        if y_scores is not None and len(y_scores) != len(y_true):
            raise ValueError(
                f"Length mismatch: y_true={len(y_true)}, y_scores={len(y_scores)}"
            )

        scores_iter = y_scores or [None] * len(y_true)  # type: ignore[list-item]
        for yt, yp, ys in zip(y_true, y_pred, scores_iter):
            self.record_prediction(yt, yp, ys)

    def compute_snapshot(self, model_id: str = "default") -> MetricSnapshot:
        """Compute a metric snapshot from accumulated predictions.

        Args:
            model_id: Identifier to attach to the snapshot.

        Returns:
            :class:`MetricSnapshot` with all metrics computed.

        Raises:
            RuntimeError: If fewer than two predictions have been recorded.
        """
        if len(self._y_true) < 2:
            raise RuntimeError(
                "At least 2 predictions must be recorded before computing metrics"
            )

        yt = np.asarray(self._y_true, dtype=int)
        yp = np.asarray(self._y_pred, dtype=int)
        ys = np.asarray(self._y_scores, dtype=float)

        accuracy = float(np.mean(yt == yp))
        tp = int(np.sum((yt == 1) & (yp == 1)))
        fp = int(np.sum((yt == 0) & (yp == 1)))
        fn = int(np.sum((yt == 1) & (yp == 0)))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )
        auc = self._compute_auc(yt, ys)

        snapshot = MetricSnapshot(
            accuracy=round(accuracy, 4),
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1_score=round(f1, 4),
            auc_roc=round(auc, 4),
            n_samples=len(yt),
            model_id=model_id,
        )
        self.history.append(snapshot)
        logger.info(
            "Metrics snapshot: acc={:.4f}, f1={:.4f}, auc={:.4f} (n={})",
            accuracy,
            f1,
            auc,
            len(yt),
        )
        return snapshot

    def reset(self) -> None:
        """Clear accumulated predictions (keeps history)."""
        self._y_true.clear()
        self._y_pred.clear()
        self._y_scores.clear()
        logger.debug("Prediction buffer reset")

    def trend(self, metric: str = "f1_score") -> np.ndarray:
        """Return the time-series of a metric from history.

        Args:
            metric: Attribute name on :class:`MetricSnapshot` to extract.

        Returns:
            1-D numpy array of metric values over time.

        Raises:
            AttributeError: If ``metric`` is not a valid snapshot attribute.
            ValueError: If history is empty.
        """
        if not self.history:
            raise ValueError("No metric history available")
        if not hasattr(self.history[0], metric):
            raise AttributeError(f"MetricSnapshot has no attribute '{metric}'")
        return np.array([getattr(s, metric) for s in self.history])

    def _compute_auc(self, y_true: np.ndarray, y_scores: np.ndarray) -> float:
        """Compute AUC-ROC using the trapezoidal rule.

        Args:
            y_true: Binary ground-truth labels.
            y_scores: Probability scores for the positive class.

        Returns:
            AUC-ROC value between 0 and 1.
        """
        if len(np.unique(y_true)) < 2:
            return 0.5  # degenerate case

        thresholds = np.sort(np.unique(y_scores))[::-1]
        tprs = [0.0]
        fprs = [0.0]

        n_pos = int(np.sum(y_true == 1))
        n_neg = int(np.sum(y_true == 0))

        for thresh in thresholds:
            y_pred_t = (y_scores >= thresh).astype(int)
            tp = int(np.sum((y_true == 1) & (y_pred_t == 1)))
            fp = int(np.sum((y_true == 0) & (y_pred_t == 1)))
            tprs.append(tp / n_pos if n_pos > 0 else 0.0)
            fprs.append(fp / n_neg if n_neg > 0 else 0.0)

        tprs.append(1.0)
        fprs.append(1.0)
        return float(np.trapezoid(tprs, fprs))
