"""
benchmark_fps.py — FPS Benchmark
==================================
Measures frames-per-second for each vision module using synthetic images.

Usage::

    python benchmarks/benchmark_fps.py
    python benchmarks/benchmark_fps.py --device cpu --iterations 50
    python benchmarks/benchmark_fps.py --modules detection depth tracking
"""

from __future__ import annotations

import argparse
import logging
import time
from typing import Callable, Dict, List, Optional

import numpy as np

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Synthetic data helpers
# ---------------------------------------------------------------------------

_RNG = np.random.default_rng(42)


def _make_image(height: int = 480, width: int = 640) -> np.ndarray:
    """Return a random uint8 RGB image."""
    return _RNG.integers(0, 256, (height, width, 3), dtype=np.uint8)


def _make_detections(n: int = 3):
    """Return a list of synthetic DetectionResult objects."""
    from vision.detection.detector import DetectionResult

    return [
        DetectionResult(
            bbox=(float(i * 80), 50.0, float(i * 80 + 70), 120.0),
            class_name="object",
            class_id=i,
            confidence=0.9,
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# Benchmark functions per module
# ---------------------------------------------------------------------------


def _bench_yolo(device: str, iterations: int) -> float:
    from vision.detection.yolo_detector import YOLODetector

    det = YOLODetector(model_size="yolov8n", confidence_threshold=0.5, device=device)
    img = _make_image()
    # Warm-up
    try:
        det.detect(img)
    except Exception:
        pass
    start = time.perf_counter()
    for _ in range(iterations):
        try:
            det.detect(img)
        except Exception:
            pass
    elapsed = time.perf_counter() - start
    return iterations / elapsed


def _bench_segmentor(device: str, iterations: int) -> float:
    from vision.segmentation.semantic_segmentor import SemanticSegmentor

    seg = SemanticSegmentor(device=device)
    img = _make_image()
    try:
        seg.segment(img)
    except Exception:
        pass
    start = time.perf_counter()
    for _ in range(iterations):
        try:
            seg.segment(img)
        except Exception:
            pass
    return iterations / (time.perf_counter() - start)


def _bench_depth(device: str, iterations: int) -> float:
    from vision.depth.depth_estimator import MonocularDepthEstimator

    est = MonocularDepthEstimator(model_name="midas", device=device)
    img = _make_image()
    try:
        est.estimate(img)
    except Exception:
        pass
    start = time.perf_counter()
    for _ in range(iterations):
        try:
            est.estimate(img)
        except Exception:
            pass
    return iterations / (time.perf_counter() - start)


def _bench_tracker(device: str, iterations: int) -> float:
    from vision.tracking.multi_object_tracker import MultiObjectTracker

    tracker = MultiObjectTracker()
    dets = _make_detections()
    start = time.perf_counter()
    for _ in range(iterations):
        try:
            tracker.update(dets)
        except Exception:
            pass
    return iterations / (time.perf_counter() - start)


def _bench_optical_flow(device: str, iterations: int) -> float:
    from vision.motion.optical_flow import OpticalFlow

    flow = OpticalFlow()
    prev = _make_image()
    curr = _make_image()
    try:
        flow.compute(prev, curr)
    except Exception:
        pass
    start = time.perf_counter()
    for _ in range(iterations):
        try:
            flow.compute(prev, curr)
        except Exception:
            pass
    return iterations / (time.perf_counter() - start)


def _bench_pipeline(device: str, iterations: int) -> float:
    from vision.vision_pipeline import VisionPipeline

    pipeline = VisionPipeline(
        device=device,
        enable_detection=True,
        enable_segmentation=False,
        enable_depth=False,
        enable_tracking=False,
    )
    img = _make_image()
    # Pre-load the lazy detector with a stub
    from unittest.mock import MagicMock

    mock_det = MagicMock()
    mock_det.detect.return_value = []
    pipeline._detector = mock_det

    start = time.perf_counter()
    for _ in range(iterations):
        pipeline.process_frame(img)
    return iterations / (time.perf_counter() - start)


# ---------------------------------------------------------------------------
# Module registry
# ---------------------------------------------------------------------------

_BENCHMARKS: Dict[str, Callable[[str, int], float]] = {
    "detection": _bench_yolo,
    "segmentation": _bench_segmentor,
    "depth": _bench_depth,
    "tracking": _bench_tracker,
    "optical_flow": _bench_optical_flow,
    "pipeline": _bench_pipeline,
}

ALL_MODULES = list(_BENCHMARKS.keys())

# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_table(results: Dict[str, Optional[float]]) -> None:
    """Print a formatted FPS table to stdout."""
    col_w = 20
    header = f"{'Module':<{col_w}} {'FPS':>10}  {'ms/frame':>10}"
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)
    for module, fps in sorted(results.items()):
        if fps is None:
            print(f"{module:<{col_w}} {'SKIP':>10}  {'N/A':>10}")
        else:
            ms = 1000.0 / fps if fps > 0 else float("inf")
            print(f"{module:<{col_w}} {fps:>10.1f}  {ms:>10.2f}")
    print(sep)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Benchmark FPS for vision pipeline modules."
    )
    parser.add_argument(
        "--device", default="cpu", help="Compute device (default: cpu)."
    )
    parser.add_argument(
        "--iterations", type=int, default=100,
        help="Number of iterations per module (default: 100)."
    )
    parser.add_argument(
        "--modules", nargs="+", default=ALL_MODULES,
        choices=ALL_MODULES,
        help="Modules to benchmark (default: all).",
    )
    return parser.parse_args()


def main() -> None:
    """Run FPS benchmarks for selected modules."""
    args = parse_args()
    print(f"\nFPS Benchmark  device={args.device}  iterations={args.iterations}\n")

    results: Dict[str, Optional[float]] = {}
    for module in args.modules:
        bench_fn = _BENCHMARKS[module]
        print(f"Benchmarking {module}...", flush=True)
        try:
            fps = bench_fn(args.device, args.iterations)
            results[module] = fps
        except ImportError as exc:
            print(f"  SKIP — missing dependency: {exc}")
            results[module] = None
        except Exception as exc:
            print(f"  SKIP — error: {exc}")
            results[module] = None

    print()
    print_table(results)
    print()


if __name__ == "__main__":
    main()
