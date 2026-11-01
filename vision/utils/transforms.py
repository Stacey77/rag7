"""Image transformation and tensor conversion utilities."""

from __future__ import annotations

import logging
from typing import Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


def resize_with_aspect(
    image: np.ndarray,
    size: Union[int, Tuple[int, int]],
    interpolation: int = 1,  # cv2.INTER_LINEAR
) -> np.ndarray:
    """Resize *image* to fit within *size* while preserving aspect ratio.

    Args:
        image: Numpy array of shape ``(H, W, ...)`` or ``(H, W)``.
        size: Target size as ``(width, height)`` or a single int for the
              longer edge.
        interpolation: OpenCV interpolation flag.

    Returns:
        Resized numpy array.
    """
    import cv2

    h, w = image.shape[:2]
    if isinstance(size, int):
        scale = size / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
    else:
        target_w, target_h = size
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(image, (new_w, new_h), interpolation=interpolation)


def normalize(
    image: np.ndarray,
    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
) -> np.ndarray:
    """Normalise a float image in ``[0, 1]`` using channel-wise mean/std.

    Args:
        image: Float32 RGB array of shape ``(H, W, 3)`` in ``[0, 1]``.
        mean: Per-channel mean.
        std: Per-channel standard deviation.

    Returns:
        Normalised float32 array.
    """
    mean_arr = np.array(mean, dtype=np.float32)
    std_arr = np.array(std, dtype=np.float32)
    return (image.astype(np.float32) - mean_arr) / (std_arr + 1e-8)


def denormalize(
    tensor,
    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
) -> np.ndarray:
    """Reverse channel-wise normalisation.

    Args:
        tensor: Torch tensor of shape ``(C, H, W)`` or numpy array ``(H, W, C)``.
        mean: Per-channel mean used during normalisation.
        std: Per-channel std used during normalisation.

    Returns:
        Float32 numpy array of shape ``(H, W, 3)`` in ``[0, 1]``.
    """
    mean_arr = np.array(mean, dtype=np.float32)
    std_arr = np.array(std, dtype=np.float32)
    try:
        arr = tensor.cpu().numpy()  # torch tensor
    except AttributeError:
        arr = np.array(tensor)

    if arr.ndim == 3 and arr.shape[0] == 3:
        arr = arr.transpose(1, 2, 0)  # CHW -> HWC

    result = arr * std_arr + mean_arr
    return np.clip(result, 0.0, 1.0).astype(np.float32)


def to_tensor(image: np.ndarray):
    """Convert a BGR or RGB uint8 numpy array to a normalised torch tensor.

    Args:
        image: Numpy array of shape ``(H, W, 3)`` dtype uint8.

    Returns:
        Float32 torch tensor of shape ``(3, H, W)`` in ``[0, 1]``.
    """
    try:
        import torch
    except ImportError as exc:
        raise ImportError("torch is required for to_tensor.") from exc

    arr = image.astype(np.float32) / 255.0
    tensor = torch.from_numpy(arr).permute(2, 0, 1)  # HWC -> CHW
    return tensor


def from_tensor(tensor) -> np.ndarray:
    """Convert a float torch tensor back to a uint8 numpy array.

    Args:
        tensor: Float32 tensor of shape ``(3, H, W)`` in ``[0, 1]``.

    Returns:
        uint8 numpy array of shape ``(H, W, 3)``.
    """
    try:
        arr = tensor.cpu().numpy()
    except AttributeError:
        arr = np.array(tensor)

    if arr.ndim == 3 and arr.shape[0] == 3:
        arr = arr.transpose(1, 2, 0)  # CHW -> HWC

    return np.clip(arr * 255.0, 0, 255).astype(np.uint8)
