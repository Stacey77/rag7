# Demo Scripts (`notebooks/`)

Standalone Python demonstration scripts for the robotics AGI vision pipeline.
Each script works with just **numpy** installed; optional heavy dependencies
(PyTorch, ultralytics, transformers, etc.) are loaded lazily and skipped with
a warning if not present.

## Quick Start

```bash
# From the repository root
pip install -e .           # install the vision package
cd notebooks

python 01_object_detection_demo.py
python 02_segmentation_demo.py
python 03_depth_estimation_demo.py
python 04_tracking_demo.py
python 05_pose_estimation_demo.py
python 06_vision_language_demo.py
python 07_full_pipeline_demo.py
```

## Script Overview

| Script | Description |
|--------|-------------|
| `01_object_detection_demo.py` | YOLODetector & DETRDetector on a synthetic image |
| `02_segmentation_demo.py` | SemanticSegmentor, InstanceSegmentor & SAMSegmentor |
| `03_depth_estimation_demo.py` | MonocularDepthEstimator & PointCloudGenerator |
| `04_tracking_demo.py` | MultiObjectTracker & ByteTracker over synthetic frames |
| `05_pose_estimation_demo.py` | HumanPoseEstimator & HandPoseEstimator |
| `06_vision_language_demo.py` | CLIPInterface, ImageCaptioner & VisualQA |
| `07_full_pipeline_demo.py` | Full VisionPipeline end-to-end demo |

## Optional Dependencies

Install all optional deps to unlock every demo:

```bash
pip install ultralytics torch torchvision transformers timm mediapipe opencv-python
```

## Notes

* All scripts generate synthetic images with `numpy`—no camera or dataset is
  required.
* Output images (annotations, depth maps, etc.) are saved to `/tmp/` when
  `opencv-python` is installed.
* Scripts are importable and can be integrated into notebooks by converting
  them with `jupytext` if desired.
