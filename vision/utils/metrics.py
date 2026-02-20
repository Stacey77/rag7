"""Evaluation metrics for detection, segmentation, tracking, and pose."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def compute_iou(
    box1: Tuple[float, float, float, float],
    box2: Tuple[float, float, float, float],
) -> float:
    """Compute Intersection over Union between two bounding boxes.

    Args:
        box1: ``(x1, y1, x2, y2)``.
        box2: ``(x1, y1, x2, y2)``.

    Returns:
        IoU in ``[0, 1]``.
    """
    ix1, iy1 = max(box1[0], box2[0]), max(box1[1], box2[1])
    ix2, iy2 = min(box1[2], box2[2]), min(box1[3], box2[3])
    iw = max(0.0, ix2 - ix1)
    ih = max(0.0, iy2 - iy1)
    inter = iw * ih
    area1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    area2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
    union = area1 + area2 - inter
    return float(inter / union) if union > 0 else 0.0


def compute_map(
    predictions: List[Dict[str, Any]],
    ground_truth: List[Dict[str, Any]],
    iou_threshold: float = 0.5,
    num_classes: Optional[int] = None,
) -> float:
    """Compute mean Average Precision (mAP) @ *iou_threshold*.

    Args:
        predictions: List of dicts with ``"bbox"``, ``"class_id"``,
                     ``"score"`` keys.
        ground_truth: List of dicts with ``"bbox"``, ``"class_id"`` keys.
        iou_threshold: IoU threshold for a match.
        num_classes: Total number of classes; inferred if ``None``.

    Returns:
        mAP float in ``[0, 1]``.
    """
    if not predictions or not ground_truth:
        return 0.0

    all_class_ids = set(d["class_id"] for d in predictions) | set(d["class_id"] for d in ground_truth)
    if num_classes is not None:
        all_class_ids = set(range(num_classes))

    aps: List[float] = []
    for cls_id in all_class_ids:
        preds_cls = sorted(
            [p for p in predictions if p["class_id"] == cls_id],
            key=lambda x: x["score"],
            reverse=True,
        )
        gts_cls = [g for g in ground_truth if g["class_id"] == cls_id]
        if not gts_cls:
            continue

        matched = [False] * len(gts_cls)
        tp = np.zeros(len(preds_cls))
        fp = np.zeros(len(preds_cls))

        for i, pred in enumerate(preds_cls):
            best_iou, best_j = 0.0, -1
            for j, gt in enumerate(gts_cls):
                iou = compute_iou(pred["bbox"], gt["bbox"])
                if iou > best_iou:
                    best_iou, best_j = iou, j
            if best_iou >= iou_threshold and not matched[best_j]:
                tp[i] = 1
                matched[best_j] = True
            else:
                fp[i] = 1

        cum_tp = np.cumsum(tp)
        cum_fp = np.cumsum(fp)
        recall = cum_tp / len(gts_cls)
        precision = cum_tp / (cum_tp + cum_fp + 1e-8)

        # Compute area under PR curve via 11-point interpolation
        ap = 0.0
        for thr in np.linspace(0, 1, 11):
            prec_at_thr = precision[recall >= thr]
            ap += float(prec_at_thr.max()) if len(prec_at_thr) > 0 else 0.0
        aps.append(ap / 11.0)

    return float(np.mean(aps)) if aps else 0.0


def compute_mota(
    tracks: List[Dict[str, Any]],
    ground_truth: List[Dict[str, Any]],
    iou_threshold: float = 0.5,
) -> float:
    """Compute Multi-Object Tracking Accuracy (MOTA).

    MOTA = 1 - (FN + FP + IDSW) / GT

    Args:
        tracks: List of dicts per frame with ``"frame"``, ``"track_id"``,
                ``"bbox"`` keys.
        ground_truth: List of dicts with ``"frame"``, ``"object_id"``,
                      ``"bbox"`` keys.
        iou_threshold: IoU threshold for a valid match.

    Returns:
        MOTA score (can be negative in degenerate cases).
    """
    if not ground_truth:
        return 0.0

    frames = set(g["frame"] for g in ground_truth)
    fp_total = fn_total = idsw_total = 0
    gt_total = len(ground_truth)
    prev_assignment: Dict[int, int] = {}  # track_id -> object_id

    for frame in sorted(frames):
        frame_tracks = [t for t in tracks if t["frame"] == frame]
        frame_gts = [g for g in ground_truth if g["frame"] == frame]

        # Greedy IoU matching
        used_tracks: set = set()
        used_gts: set = set()
        assignment: Dict[int, int] = {}

        for gt in frame_gts:
            best_iou, best_tid = 0.0, None
            for trk in frame_tracks:
                if trk["track_id"] in used_tracks:
                    continue
                iou = compute_iou(trk["bbox"], gt["bbox"])
                if iou > best_iou:
                    best_iou = iou
                    best_tid = trk["track_id"]
            if best_iou >= iou_threshold and best_tid is not None:
                assignment[best_tid] = gt["object_id"]
                used_tracks.add(best_tid)
                used_gts.add(gt["object_id"])

        fn_total += len(frame_gts) - len(used_gts)
        fp_total += len(frame_tracks) - len(used_tracks)

        # Identity switches
        for tid, oid in assignment.items():
            if tid in prev_assignment and prev_assignment[tid] != oid:
                idsw_total += 1
        prev_assignment = assignment

    mota = 1.0 - (fn_total + fp_total + idsw_total) / gt_total
    return float(mota)


def compute_pck(
    predictions: List[np.ndarray],
    ground_truth: List[np.ndarray],
    threshold: float = 0.2,
    ref_dist: Optional[float] = None,
) -> float:
    """Compute Percentage of Correct Keypoints (PCK).

    Args:
        predictions: List of keypoint arrays, each of shape ``(K, 2)`` or
                     ``(K, 3)``.
        ground_truth: List of ground-truth arrays, same shape.
        threshold: Fraction of the reference distance for a correct keypoint.
        ref_dist: Reference distance in pixels.  If ``None``, uses the
                  diagonal of the bounding box encompassing all GT keypoints.

    Returns:
        PCK score in ``[0, 1]``.
    """
    if not predictions or not ground_truth:
        return 0.0

    correct = total = 0
    for pred, gt in zip(predictions, ground_truth):
        pred_xy = pred[:, :2]
        gt_xy = gt[:, :2]

        if ref_dist is None:
            x_range = gt_xy[:, 0].max() - gt_xy[:, 0].min()
            y_range = gt_xy[:, 1].max() - gt_xy[:, 1].min()
            dist_ref = float(np.sqrt(x_range ** 2 + y_range ** 2)) + 1e-8
        else:
            dist_ref = ref_dist

        dists = np.linalg.norm(pred_xy - gt_xy, axis=1)
        correct += int((dists < threshold * dist_ref).sum())
        total += len(dists)

    return float(correct / total) if total > 0 else 0.0
