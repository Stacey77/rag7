"""
Main vision pipeline that orchestrates all computer vision modules.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, List, Optional, Union

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the vision pipeline."""

    device: str = "cuda"
    enable_detection: bool = True
    enable_segmentation: bool = False
    enable_depth: bool = False
    enable_tracking: bool = False
    enable_pose: bool = False
    enable_clip: bool = False
    detection_model: str = "yolov8n"
    detection_confidence: float = 0.5
    segmentation_model: str = "deeplabv3plus"
    depth_model: str = "midas"


@dataclass
class FrameResult:
    """Result of processing a single frame."""

    image: np.ndarray
    detections: List[Any] = field(default_factory=list)
    segmentation: Optional[np.ndarray] = None
    depth_map: Optional[np.ndarray] = None
    tracks: List[Any] = field(default_factory=list)
    poses: List[Any] = field(default_factory=list)
    scene_description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class VisionPipeline:
    """
    Orchestrates all computer vision modules for a robotics AGI system.

    Supports lazy loading of heavy models and configurable module activation.

    Example::

        pipeline = VisionPipeline(device="cuda", enable_detection=True)
        result = pipeline.process_frame(image)
        objects = pipeline.find_object(image, "red cup")
    """

    def __init__(
        self,
        device: str = "cuda",
        enable_detection: bool = True,
        enable_segmentation: bool = False,
        enable_depth: bool = False,
        enable_tracking: bool = False,
        enable_pose: bool = False,
        enable_clip: bool = False,
        detection_model: str = "yolov8n",
        detection_confidence: float = 0.5,
        segmentation_model: str = "deeplabv3plus",
        depth_model: str = "midas",
        config: Optional[PipelineConfig] = None,
    ) -> None:
        """
        Initialise the vision pipeline.

        Args:
            device: Compute device, ``"cuda"`` or ``"cpu"``.
            enable_detection: Whether to run object detection.
            enable_segmentation: Whether to run semantic segmentation.
            enable_depth: Whether to run depth estimation.
            enable_tracking: Whether to run multi-object tracking.
            enable_pose: Whether to run human pose estimation.
            enable_clip: Whether to load the CLIP model.
            detection_model: YOLO model variant.
            detection_confidence: Minimum detection confidence threshold.
            segmentation_model: Segmentation architecture name.
            depth_model: Depth estimation model name.
            config: Optional :class:`PipelineConfig` overrides all other args.
        """
        if config is not None:
            self.config = config
        else:
            self.config = PipelineConfig(
                device=device,
                enable_detection=enable_detection,
                enable_segmentation=enable_segmentation,
                enable_depth=enable_depth,
                enable_tracking=enable_tracking,
                enable_pose=enable_pose,
                enable_clip=enable_clip,
                detection_model=detection_model,
                detection_confidence=detection_confidence,
                segmentation_model=segmentation_model,
                depth_model=depth_model,
            )

        # Lazy-loaded module references
        self._detector = None
        self._segmentor = None
        self._depth_estimator = None
        self._tracker = None
        self._pose_estimator = None
        self._clip = None
        self._scene_analyzer = None

        logger.info("VisionPipeline created with config: %s", self.config)

    # ------------------------------------------------------------------
    # Lazy property accessors
    # ------------------------------------------------------------------

    @property
    def detector(self):
        """Lazily load the object detector."""
        if self._detector is None and self.config.enable_detection:
            from vision.detection.yolo_detector import YOLODetector

            self._detector = YOLODetector(
                model_size=self.config.detection_model,
                confidence_threshold=self.config.detection_confidence,
                device=self.config.device,
            )
        return self._detector

    @property
    def segmentor(self):
        """Lazily load the semantic segmentor."""
        if self._segmentor is None and self.config.enable_segmentation:
            from vision.segmentation.semantic_segmentor import SemanticSegmentor

            self._segmentor = SemanticSegmentor(
                model_name=self.config.segmentation_model,
                device=self.config.device,
            )
        return self._segmentor

    @property
    def depth_estimator(self):
        """Lazily load the depth estimator."""
        if self._depth_estimator is None and self.config.enable_depth:
            from vision.depth.depth_estimator import MonocularDepthEstimator

            self._depth_estimator = MonocularDepthEstimator(
                model_name=self.config.depth_model,
                device=self.config.device,
            )
        return self._depth_estimator

    @property
    def tracker(self):
        """Lazily load the multi-object tracker."""
        if self._tracker is None and self.config.enable_tracking:
            from vision.tracking.multi_object_tracker import MultiObjectTracker

            self._tracker = MultiObjectTracker()
        return self._tracker

    @property
    def pose_estimator(self):
        """Lazily load the human pose estimator."""
        if self._pose_estimator is None and self.config.enable_pose:
            from vision.pose.human_pose_estimator import HumanPoseEstimator

            self._pose_estimator = HumanPoseEstimator(device=self.config.device)
        return self._pose_estimator

    @property
    def clip(self):
        """Lazily load the CLIP interface."""
        if self._clip is None and self.config.enable_clip:
            from vision.vlm.clip_interface import CLIPInterface

            self._clip = CLIPInterface(device=self.config.device)
        return self._clip

    @property
    def scene_analyzer(self):
        """Lazily load the scene analyser."""
        if self._scene_analyzer is None:
            from vision.scene.scene_analyzer import SceneAnalyzer

            self._scene_analyzer = SceneAnalyzer()
        return self._scene_analyzer

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def process_frame(self, image: np.ndarray) -> FrameResult:
        """
        Run all enabled modules on a single image frame.

        Args:
            image: BGR or RGB numpy array of shape ``(H, W, 3)``.

        Returns:
            :class:`FrameResult` containing outputs from all enabled modules.
        """
        if image is None or image.size == 0:
            raise ValueError("process_frame received an empty image")

        result = FrameResult(image=image)

        if self.config.enable_detection and self.detector is not None:
            try:
                result.detections = self.detector.detect(image)
            except Exception as exc:  # pragma: no cover
                logger.error("Detection failed: %s", exc)

        if self.config.enable_segmentation and self.segmentor is not None:
            try:
                result.segmentation = self.segmentor.segment(image)
            except Exception as exc:  # pragma: no cover
                logger.error("Segmentation failed: %s", exc)

        if self.config.enable_depth and self.depth_estimator is not None:
            try:
                result.depth_map = self.depth_estimator.estimate(image)
            except Exception as exc:  # pragma: no cover
                logger.error("Depth estimation failed: %s", exc)

        if self.config.enable_tracking and self.tracker is not None:
            try:
                result.tracks = self.tracker.update(result.detections)
            except Exception as exc:  # pragma: no cover
                logger.error("Tracking failed: %s", exc)

        if self.config.enable_pose and self.pose_estimator is not None:
            try:
                result.poses = self.pose_estimator.detect_poses(image)
            except Exception as exc:  # pragma: no cover
                logger.error("Pose estimation failed: %s", exc)

        return result

    def process_stream(
        self,
        video_source: Union[int, str],
        max_frames: Optional[int] = None,
    ) -> Generator[FrameResult, None, None]:
        """
        Process a video stream frame by frame.

        Args:
            video_source: Camera index or path to a video file.
            max_frames: Maximum number of frames to yield; ``None`` for unlimited.

        Yields:
            :class:`FrameResult` for each processed frame.
        """
        import cv2  # type: ignore

        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video source: {video_source}")

        frame_count = 0
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                yield self.process_frame(frame)
                frame_count += 1
                if max_frames is not None and frame_count >= max_frames:
                    break
        finally:
            cap.release()

    def find_object(
        self, image: np.ndarray, query: str
    ) -> Dict[str, Any]:
        """
        Locate a described object in an image using CLIP.

        Args:
            image: Input image as a numpy array.
            query: Natural-language description of the object.

        Returns:
            Dict with ``"score"`` (float) and optionally ``"region"`` (bbox).
        """
        if not self.config.enable_clip:
            self.config.enable_clip = True
            self._clip = None  # force reload

        if self.clip is None:
            return {"score": 0.0, "region": None, "error": "CLIP not available"}

        try:
            score = self.clip.classify(image, [query, "other"])[0]
            return {"score": float(score), "query": query}
        except Exception as exc:  # pragma: no cover
            logger.error("find_object failed: %s", exc)
            return {"score": 0.0, "region": None, "error": str(exc)}

    def analyze_scene(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Perform full scene understanding on an image.

        Runs detection, depth, and scene analysis, then combines results into
        a unified scene description dictionary.

        Args:
            image: Input image as a numpy array.

        Returns:
            Dict containing detected objects, depth, and a text description.
        """
        frame_result = self.process_frame(image)
        scene_info: Dict[str, Any] = {
            "detections": frame_result.detections,
            "depth_available": frame_result.depth_map is not None,
        }

        try:
            description = self.scene_analyzer.generate_description(
                image, frame_result.detections
            )
            scene_info["description"] = description
        except Exception as exc:  # pragma: no cover
            logger.error("Scene analysis failed: %s", exc)
            scene_info["description"] = ""

        return scene_info

    def enable_module(self, module: str) -> None:
        """
        Dynamically enable a pipeline module by name.

        Args:
            module: One of ``"detection"``, ``"segmentation"``, ``"depth"``,
                    ``"tracking"``, ``"pose"``, ``"clip"``.
        """
        attr = f"enable_{module}"
        if hasattr(self.config, attr):
            setattr(self.config, attr, True)
        else:
            raise ValueError(f"Unknown module: {module}")

    def disable_module(self, module: str) -> None:
        """
        Dynamically disable a pipeline module by name.

        Args:
            module: Module name (same options as :meth:`enable_module`).
        """
        attr = f"enable_{module}"
        if hasattr(self.config, attr):
            setattr(self.config, attr, False)
        else:
            raise ValueError(f"Unknown module: {module}")
