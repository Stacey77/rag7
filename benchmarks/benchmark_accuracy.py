"""
benchmark_accuracy.py — Accuracy Benchmarks
============================================
Measures accuracy metrics for detection, tracking, and pose estimation using
synthetic ground-truth and prediction data.

Metrics implemented:
  - IoU and mAP for object detection
  - MOTA for multi-object tracking
  - PCK for pose estimation

Usage::

    python benchmarks/benchmark_accuracy.py
"""

from __future__ import annotations

import argparse
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Detection metrics
# ---------------------------------------------------------------------------


def compute_iou(
    box_a: Tuple[float, float, float, float],
    box_b: Tuple[float, float, float, float],
) -> float:
    """Compute Intersection-over-Union between two bounding boxes.

    Args:
        box_a: ``(x1, y1, x2, y2)`` for the first box.
        box_b: ``(x1, y1, x2, y2)`` for the second box.

    Returns:
        IoU value in ``[0, 1]``.
    """
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union_area = area_a + area_b - inter_area

    if union_area <= 0:
        return 0.0
    return inter_area / union_area


def compute_ap(
    precisions: List[float],
    recalls: List[float],
) -> float:
    """Compute Average Precision using the 11-point interpolation.

    Args:
        precisions: Precision values at different thresholds.
        recalls: Recall values at different thresholds.

    Returns:
        Average Precision value in ``[0, 1]``.
    """
    ap = 0.0
    for recall_level in np.linspace(0, 1, 11):
        p_at_r = [
            p for p, r in zip(precisions, recalls) if r >= recall_level
        ]
        ap += max(p_at_r) if p_at_r else 0.0
    return ap / 11.0


def compute_map(
    predictions: List[List[dict]],
    ground_truths: List[List[dict]],
    iou_threshold: float = 0.5,
) -> float:
    """Compute mean Average Precision (mAP) at a given IoU threshold.

    Each prediction/GT dict should have keys ``"bbox"`` (4-tuple) and
    ``"class_id"`` (int).  Predictions also require ``"confidence"`` (float).

    Args:
        predictions: Per-image list of prediction dicts.
        ground_truths: Per-image list of ground-truth dicts.
        iou_threshold: IoU threshold for a true-positive match.

    Returns:
        mAP value in ``[0, 1]``.
    """
    # Collect all class IDs
    all_classes = set()
    for img_preds in predictions:
        for p in img_preds:
            all_classes.add(p["class_id"])
    for img_gts in ground_truths:
        for g in img_gts:
            all_classes.add(g["class_id"])

    per_class_ap: List[float] = []
    for cls_id in all_classes:
        tp_list: List[int] = []
        fp_list: List[int] = []
        n_gt = sum(
            sum(1 for g in gts if g["class_id"] == cls_id)
            for gts in ground_truths
        )
        if n_gt == 0:
            continue

        # Flatten and sort by descending confidence
        all_preds: List[Tuple[float, int, dict]] = []
        for img_idx, img_preds in enumerate(predictions):
            for p in img_preds:
                if p["class_id"] == cls_id:
                    all_preds.append((p["confidence"], img_idx, p))
        all_preds.sort(key=lambda x: -x[0])

        matched: List[set] = [set() for _ in predictions]
        for conf, img_idx, pred in all_preds:
            gts_for_img = [g for g in ground_truths[img_idx] if g["class_id"] == cls_id]
            best_iou, best_gt_idx = 0.0, -1
            for gt_idx, gt in enumerate(gts_for_img):
                if gt_idx in matched[img_idx]:
                    continue
                iou = compute_iou(pred["bbox"], gt["bbox"])
                if iou > best_iou:
                    best_iou, best_gt_idx = iou, gt_idx

            if best_iou >= iou_threshold and best_gt_idx >= 0:
                tp_list.append(1)
                fp_list.append(0)
                matched[img_idx].add(best_gt_idx)
            else:
                tp_list.append(0)
                fp_list.append(1)

        tp_cum = np.cumsum(tp_list)
        fp_cum = np.cumsum(fp_list)
        recalls = (tp_cum / max(n_gt, 1)).tolist()
        precisions = (tp_cum / (tp_cum + fp_cum + 1e-9)).tolist()
        per_class_ap.append(compute_ap(precisions, recalls))

    return float(np.mean(per_class_ap)) if per_class_ap else 0.0


# ---------------------------------------------------------------------------
# Tracking metrics
# ---------------------------------------------------------------------------


def compute_mota(
    gt_tracks: List[List[dict]],
    pred_tracks: List[List[dict]],
    iou_threshold: float = 0.5,
) -> float:
    """Compute Multiple Object Tracking Accuracy (MOTA).

    MOTA = 1 - (FP + FN + IDSW) / GT

    Each track dict should have keys ``"bbox"`` (4-tuple) and ``"id"`` (int).

    Args:
        gt_tracks: Per-frame list of ground-truth track dicts.
        pred_tracks: Per-frame list of predicted track dicts.
        iou_threshold: IoU threshold for a true-positive match.

    Returns:
        MOTA value (can be negative for bad trackers).
    """
    total_gt = 0
    total_fp = 0
    total_fn = 0
    total_idsw = 0
    prev_gt_to_pred: Dict[int, int] = {}

    for frame_gt, frame_pred in zip(gt_tracks, pred_tracks):
        total_gt += len(frame_gt)
        matched_pred: set = set()
        cur_gt_to_pred: Dict[int, int] = {}

        for gt in frame_gt:
            best_iou, best_pred_idx = 0.0, -1
            for p_idx, pred in enumerate(frame_pred):
                if p_idx in matched_pred:
                    continue
                iou = compute_iou(gt["bbox"], pred["bbox"])
                if iou > best_iou:
                    best_iou, best_pred_idx = iou, p_idx

            if best_iou >= iou_threshold and best_pred_idx >= 0:
                matched_pred.add(best_pred_idx)
                pred_id = frame_pred[best_pred_idx]["id"]
                cur_gt_to_pred[gt["id"]] = pred_id
                # Check ID switch
                if gt["id"] in prev_gt_to_pred and prev_gt_to_pred[gt["id"]] != pred_id:
                    total_idsw += 1
            else:
                total_fn += 1

        total_fp += len(frame_pred) - len(matched_pred)
        prev_gt_to_pred = cur_gt_to_pred

    if total_gt == 0:
        return 0.0
    return 1.0 - (total_fp + total_fn + total_idsw) / total_gt


# ---------------------------------------------------------------------------
# Pose metrics
# ---------------------------------------------------------------------------


def compute_pck(
    predicted_kpts: np.ndarray,
    gt_kpts: np.ndarray,
    threshold: float = 0.2,
    bbox_size: Optional[float] = None,
) -> float:
    """Compute Percentage of Correct Keypoints (PCK).

    A keypoint is considered correct when its Euclidean distance to the
    ground-truth is within ``threshold × bbox_size`` (or simply
    ``threshold`` if ``bbox_size`` is ``None``).

    Only the X and Y coordinates (columns 0 and 1) are used when keypoints
    have 3 columns (e.g. ``(N, 3)`` with a visibility/depth channel); the
    third coordinate is ignored so that 2D and 3D keypoint arrays are both
    accepted without modification.

    Args:
        predicted_kpts: Predicted keypoints of shape ``(N, 2)`` or ``(N, 3)``.
        gt_kpts: Ground-truth keypoints of the same shape.
        threshold: Fraction of bbox_size (or absolute pixel distance).
        bbox_size: Reference size; usually the diagonal of the bounding box.

    Returns:
        PCK value in ``[0, 1]``.
    """
    if predicted_kpts.shape != gt_kpts.shape:
        raise ValueError(
            f"Shape mismatch: {predicted_kpts.shape} vs {gt_kpts.shape}"
        )

    dists = np.linalg.norm(predicted_kpts[:, :2] - gt_kpts[:, :2], axis=1)
    thr = threshold * bbox_size if bbox_size is not None else threshold
    return float(np.mean(dists <= thr))


# ---------------------------------------------------------------------------
# Synthetic data generators
# ---------------------------------------------------------------------------


def _make_detection_data(
    n_images: int = 20,
    n_objects: int = 3,
    noise_scale: float = 10.0,
) -> Tuple[List[List[dict]], List[List[dict]]]:
    """Return synthetic (ground_truths, predictions) detection lists."""
    rng = np.random.default_rng(0)
    gts: List[List[dict]] = []
    preds: List[List[dict]] = []

    for _ in range(n_images):
        img_gts: List[dict] = []
        img_preds: List[dict] = []
        for cls_id in range(n_objects):
            x1, y1 = float(rng.integers(10, 400)), float(rng.integers(10, 300))
            x2, y2 = x1 + 80.0, y1 + 60.0
            img_gts.append({"bbox": (x1, y1, x2, y2), "class_id": cls_id})
            # Prediction with small jitter
            dx, dy = float(rng.normal(0, noise_scale)), float(rng.normal(0, noise_scale))
            img_preds.append({
                "bbox": (x1 + dx, y1 + dy, x2 + dx, y2 + dy),
                "class_id": cls_id,
                "confidence": float(rng.uniform(0.6, 0.99)),
            })
        gts.append(img_gts)
        preds.append(img_preds)

    return gts, preds


def _make_tracking_data(
    n_frames: int = 30,
    n_tracks: int = 3,
) -> Tuple[List[List[dict]], List[List[dict]]]:
    """Return synthetic (gt_tracks, pred_tracks) tracking lists."""
    rng = np.random.default_rng(1)
    gt_tracks: List[List[dict]] = []
    pred_tracks: List[List[dict]] = []

    positions = rng.integers(50, 400, (n_tracks, 2)).astype(float)
    for frame_idx in range(n_frames):
        positions += rng.normal(0, 3, positions.shape)
        frame_gt, frame_pred = [], []
        for tid in range(n_tracks):
            x1, y1 = positions[tid]
            bbox = (x1, y1, x1 + 60.0, y1 + 40.0)
            frame_gt.append({"bbox": bbox, "id": tid})
            noise = rng.normal(0, 5, 4)
            pred_bbox = tuple(float(b + n) for b, n in zip(bbox, noise))
            frame_pred.append({"bbox": pred_bbox, "id": tid})
        gt_tracks.append(frame_gt)
        pred_tracks.append(frame_pred)

    return gt_tracks, pred_tracks


def _make_pose_data(
    n_poses: int = 50,
    n_kpts: int = 17,
    noise_scale: float = 5.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return synthetic (pred_kpts, gt_kpts) arrays of shape (N, 2)."""
    rng = np.random.default_rng(2)
    gt = rng.uniform(50, 400, (n_kpts, 2)).astype(np.float32)
    pred = gt + rng.normal(0, noise_scale, gt.shape).astype(np.float32)
    return pred, gt


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_table(results: Dict[str, float]) -> None:
    """Print a formatted accuracy table to stdout."""
    col_w = 25
    header = f"{'Metric':<{col_w}} {'Value':>10}"
    sep = "-" * (col_w + 12)
    print(sep)
    print(header)
    print(sep)
    for metric, value in results.items():
        print(f"{metric:<{col_w}} {value:>10.4f}")
    print(sep)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Accuracy benchmarks for vision pipeline modules."
    )
    parser.add_argument(
        "--iou-threshold", type=float, default=0.5,
        help="IoU threshold for detection/tracking metrics (default: 0.5).",
    )
    parser.add_argument(
        "--pck-threshold", type=float, default=0.2,
        help="PCK normalised distance threshold (default: 0.2).",
    )
    return parser.parse_args()


def main() -> None:
    """Run accuracy benchmarks and print results."""
    args = parse_args()
    results: Dict[str, float] = {}

    print("\nAccuracy Benchmarks\n")

    # Detection mAP
    print("Computing detection mAP...", flush=True)
    try:
        gts, preds = _make_detection_data()
        map_val = compute_map(preds, gts, iou_threshold=args.iou_threshold)
        results["Detection mAP@0.5"] = map_val
    except Exception as exc:
        print(f"  SKIP — {exc}")

    # Tracking MOTA
    print("Computing tracking MOTA...", flush=True)
    try:
        gt_tracks, pred_tracks = _make_tracking_data()
        mota = compute_mota(gt_tracks, pred_tracks, iou_threshold=args.iou_threshold)
        results["Tracking MOTA"] = mota
    except Exception as exc:
        print(f"  SKIP — {exc}")

    # Pose PCK
    print("Computing pose PCK...", flush=True)
    try:
        pred_kpts, gt_kpts = _make_pose_data()
        bbox_diag = float(np.sqrt(350.0**2 + 350.0**2))
        pck = compute_pck(pred_kpts, gt_kpts, threshold=args.pck_threshold, bbox_size=bbox_diag)
        results["Pose PCK@0.2"] = pck
    except Exception as exc:
        print(f"  SKIP — {exc}")

    print()
    print_table(results)
    print()


if __name__ == "__main__":
    main()
