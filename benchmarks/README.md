# Benchmarks

Performance benchmarks for the robotics AGI vision pipeline.

## Quick Start

```bash
# From the repository root
pip install -e .
cd benchmarks

# FPS benchmark (all modules, CPU, 100 iterations)
python benchmark_fps.py

# FPS benchmark with custom options
python benchmark_fps.py --device cuda --iterations 200 --modules detection tracking

# Accuracy benchmark
python benchmark_accuracy.py
python benchmark_accuracy.py --iou-threshold 0.75 --pck-threshold 0.1
```

## Scripts

### `benchmark_fps.py`

Measures frames-per-second for each vision module using synthetic random
images (no GPU or real data required).

**Modules benchmarked:**

| Module | Class |
|--------|-------|
| `detection` | `YOLODetector` |
| `segmentation` | `SemanticSegmentor` |
| `depth` | `MonocularDepthEstimator` |
| `tracking` | `MultiObjectTracker` |
| `optical_flow` | `OpticalFlow` |
| `pipeline` | `VisionPipeline` (end-to-end) |

**CLI arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--device` | `cpu` | Compute device (`cpu` or `cuda`) |
| `--iterations` | `100` | Iterations per module |
| `--modules` | all | Space-separated list of modules to benchmark |

**Sample output:**

```
FPS Benchmark  device=cpu  iterations=100

--------------------------------------------
Module               FPS          ms/frame
--------------------------------------------
detection           45.3          22.07
depth               12.8          78.20
optical_flow       320.1           3.12
pipeline           210.5           4.75
segmentation        18.4          54.35
tracking           895.3           1.12
--------------------------------------------
```

### `benchmark_accuracy.py`

Computes accuracy metrics using synthetic ground-truth and prediction data.
No model weights are required.

**Metrics:**

| Metric | Description |
|--------|-------------|
| Detection mAP@0.5 | Mean Average Precision at IoU ≥ 0.5 |
| Tracking MOTA | Multiple Object Tracking Accuracy |
| Pose PCK@0.2 | Percentage of Correct Keypoints at 20 % of bbox diagonal |

**CLI arguments:**

| Argument | Default | Description |
|----------|---------|-------------|
| `--iou-threshold` | `0.5` | IoU threshold for detection/tracking TP matching |
| `--pck-threshold` | `0.2` | Normalised distance threshold for PCK |

## Interpreting Results

- **FPS:** Higher is better.  CPU FPS is much lower than GPU; use `--device cuda` for realistic numbers.
- **mAP:** 1.0 = perfect detection; 0.0 = no correct detections at the chosen IoU threshold.
- **MOTA:** Values near 1.0 indicate excellent tracking; negative values are possible with many ID switches or false positives.
- **PCK:** 1.0 = all keypoints within the distance threshold.

## Notes

- Modules with missing dependencies (e.g., `ultralytics`, `torch`) are
  automatically skipped with a `SKIP` message.
- Benchmarks use deterministic synthetic data (seeded RNG) for
  reproducibility.
