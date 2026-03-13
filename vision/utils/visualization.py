"""Visualisation utilities for all vision module outputs."""

from __future__ import annotations

import logging
from typing import Any, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# Colour palette for segmentation masks
_PALETTE = [
    (220, 20, 60), (119, 11, 32), (0, 0, 142), (0, 0, 230), (106, 0, 228),
    (0, 60, 100), (0, 80, 100), (0, 0, 192), (250, 170, 30), (100, 170, 30),
    (220, 220, 0), (175, 116, 175), (250, 0, 30), (165, 42, 42), (255, 77, 255),
    (0, 226, 252), (182, 182, 255), (0, 82, 0), (120, 166, 157), (110, 76, 0),
]


def draw_detections(
    image: np.ndarray,
    detections: List[Any],
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2,
    font_scale: float = 0.5,
) -> np.ndarray:
    """Draw bounding boxes and labels on *image*.

    Args:
        image: BGR numpy array.
        detections: List of objects with ``bbox``, ``class_name``, and
                    ``confidence`` attributes.
        color: BGR box colour.
        thickness: Line thickness.
        font_scale: Label font scale.

    Returns:
        Annotated BGR image.
    """
    import cv2
    out = image.copy()
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det.bbox]
        cv2.rectangle(out, (x1, y1), (x2, y2), color, thickness)
        label = f"{det.class_name} {det.confidence:.2f}"
        if hasattr(det, "track_id") and det.track_id is not None:
            label = f"[{det.track_id}] {label}"
        cv2.putText(
            out, label, (x1, max(0, y1 - 5)),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness
        )
    return out


def draw_segmentation(
    image: np.ndarray,
    mask: np.ndarray,
    alpha: float = 0.5,
    palette: Optional[List[Tuple[int, int, int]]] = None,
) -> np.ndarray:
    """Overlay a segmentation mask on *image*.

    Args:
        image: BGR numpy array.
        mask: Integer segmentation map ``(H, W)`` or binary ``(H, W)`` uint8.
        alpha: Transparency of the overlay (0 = invisible, 1 = opaque).
        palette: Optional colour palette; defaults to a built-in one.

    Returns:
        Annotated BGR image.
    """
    if palette is None:
        palette = _PALETTE
    out = image.copy().astype(np.float32)
    colour_map = np.zeros_like(image, dtype=np.float32)

    unique_ids = np.unique(mask)
    for class_id in unique_ids:
        if class_id == 0:
            continue
        colour = palette[int(class_id) % len(palette)]
        colour_map[mask == class_id] = colour[::-1]  # RGB -> BGR

    overlay = out * (1 - alpha) + colour_map * alpha
    return np.clip(overlay, 0, 255).astype(np.uint8)


def draw_depth(
    depth_map: np.ndarray,
    colormap: int = 2,  # cv2.COLORMAP_JET
) -> np.ndarray:
    """Render a depth map as a colourised image.

    Args:
        depth_map: Float32 depth array ``(H, W)``.
        colormap: OpenCV colourmap constant.

    Returns:
        Colourised BGR image of shape ``(H, W, 3)``.
    """
    import cv2
    valid = depth_map[depth_map > 0]
    if valid.size == 0:
        return np.zeros((*depth_map.shape[:2], 3), dtype=np.uint8)
    dmin, dmax = valid.min(), valid.max()
    norm = np.where(depth_map > 0, (depth_map - dmin) / (dmax - dmin + 1e-8), 0.0)
    norm_u8 = (norm * 255).astype(np.uint8)
    return cv2.applyColorMap(norm_u8, colormap)


def draw_poses(
    image: np.ndarray,
    poses: List[Any],
    skeleton: Optional[List[Tuple[int, int]]] = None,
) -> np.ndarray:
    """Draw pose skeletons on *image*.

    Args:
        image: BGR numpy array.
        poses: List of objects with ``keypoints`` attribute of shape ``(17, 3)``.
        skeleton: List of ``(i, j)`` keypoint connection pairs; uses COCO if
                  ``None``.

    Returns:
        Annotated BGR image.
    """
    import cv2

    if skeleton is None:
        # COCO 17-keypoint skeleton
        skeleton = [
            (0, 1), (0, 2), (1, 3), (2, 4),
            (5, 7), (7, 9), (6, 8), (8, 10),
            (5, 6), (5, 11), (6, 12), (11, 12),
            (11, 13), (13, 15), (12, 14), (14, 16),
        ]

    out = image.copy()
    for pose in poses:
        kps = pose.keypoints  # (17, 3)
        for (i, j) in skeleton:
            if i < len(kps) and j < len(kps):
                xi, yi, vi = kps[i]
                xj, yj, vj = kps[j]
                if vi > 0.2 and vj > 0.2:
                    cv2.line(out, (int(xi), int(yi)), (int(xj), int(yj)), (0, 255, 0), 2)
        for x, y, v in kps:
            if v > 0.2:
                cv2.circle(out, (int(x), int(y)), 4, (0, 0, 255), -1)
    return out


def draw_tracks(
    image: np.ndarray,
    tracks: List[Any],
    thickness: int = 2,
) -> np.ndarray:
    """Visualise track bounding boxes with unique colours per ID.

    Args:
        image: BGR numpy array.
        tracks: List of track objects with ``track_id``, ``bbox``, and
                ``class_name`` attributes.
        thickness: Line thickness.

    Returns:
        Annotated BGR image.
    """
    import cv2
    out = image.copy()
    for track in tracks:
        tid = track.track_id
        colour = _id_colour(tid)
        x1, y1, x2, y2 = [int(v) for v in track.bbox]
        cv2.rectangle(out, (x1, y1), (x2, y2), colour, thickness)
        label = f"ID:{tid} {track.class_name}"
        cv2.putText(out, label, (x1, max(0, y1 - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour, thickness)
    return out


def create_3d_visualization(
    pointcloud: np.ndarray,
    title: str = "Point Cloud",
) -> Optional[Any]:
    """Create an interactive 3-D visualisation using Open3D.

    Args:
        pointcloud: Float32 array of shape ``(N, 3)`` or ``(N, 6)``.
        title: Window title.

    Returns:
        Open3D PointCloud object, or ``None`` if Open3D is unavailable.
    """
    try:
        import open3d as o3d  # type: ignore

        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pointcloud[:, :3])
        if pointcloud.shape[1] >= 6:
            pcd.colors = o3d.utility.Vector3dVector(pointcloud[:, 3:6])
        o3d.visualization.draw_geometries([pcd], window_name=title)
        return pcd
    except ImportError:
        logger.warning("open3d not installed; skipping 3D visualisation.")
        return None


def _id_colour(track_id: int) -> Tuple[int, int, int]:
    """Generate a stable BGR colour from a track ID."""
    import hashlib
    h = int(hashlib.md5(str(track_id).encode()).hexdigest()[:6], 16)
    r = (h & 0xFF0000) >> 16
    g = (h & 0x00FF00) >> 8
    b = h & 0x0000FF
    return (b, g, r)
