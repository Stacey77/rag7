"""
ROS2 Vision Node.

Bridges the vision pipeline with the ROS2 ecosystem.  All ROS2 imports are
guarded with try/except so this module can be imported and tested without a
ROS2 installation.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional ROS2 imports
# ---------------------------------------------------------------------------

_ROS2_AVAILABLE = False
try:
    import rclpy  # type: ignore
    from rclpy.node import Node  # type: ignore
    from sensor_msgs.msg import Image, PointCloud2  # type: ignore
    from std_msgs.msg import String  # type: ignore
    from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy  # type: ignore

    _ROS2_AVAILABLE = True
except ImportError:
    # Provide a minimal stub so the class definition below is valid even
    # without a ROS2 installation.
    class Node:  # type: ignore[no-redef]
        """Stub ROS2 Node base class used when rclpy is not installed."""

        def __init__(self, node_name: str, **kwargs: Any) -> None:
            self._node_name = node_name

        def get_logger(self):  # noqa: D102
            return logger

        def create_subscription(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
            return None

        def create_publisher(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
            return None

        def create_service(self, *args: Any, **kwargs: Any) -> None:  # noqa: D102
            return None

        def destroy_node(self) -> None:  # noqa: D102
            pass


class VisionNode(Node):
    """
    ROS2 node that wraps the vision pipeline.

    Subscribes to a camera topic, runs the vision pipeline on each frame,
    and publishes results on several topics.  Two services allow external
    nodes to query the pipeline.

    Topics
    ------
    Subscribed:
        /camera/image_raw  (sensor_msgs/Image)

    Published:
        /vision/detections        (std_msgs/String)  — JSON detections
        /vision/segmentation      (sensor_msgs/Image) — segmentation mask
        /vision/depth             (sensor_msgs/Image) — depth map
        /vision/poses             (std_msgs/String)  — JSON pose list
        /vision/scene_description (std_msgs/String)  — text description
        /vision/pointcloud        (sensor_msgs/PointCloud2)

    Services:
        /vision/find_object   — locate a described object, returns JSON bbox
        /vision/analyze_scene — full scene analysis, returns JSON
    """

    def __init__(
        self,
        device: str = "cpu",
        enable_detection: bool = True,
        enable_depth: bool = True,
        enable_tracking: bool = True,
        confidence_threshold: float = 0.5,
    ) -> None:
        super().__init__("vision_node")

        self.device = device
        self.enable_detection = enable_detection
        self.enable_depth = enable_depth
        self.enable_tracking = enable_tracking
        self.confidence_threshold = confidence_threshold

        # Pipeline is initialised lazily on first image
        self._pipeline: Optional[Any] = None
        # Last received image stored for service callbacks
        self._last_image: Optional[np.ndarray] = None

        if _ROS2_AVAILABLE:
            self._setup_ros_interfaces()
        else:
            logger.warning(
                "rclpy not available – VisionNode running in stub mode."
            )

    # ------------------------------------------------------------------
    # ROS2 interface setup
    # ------------------------------------------------------------------

    def _setup_ros_interfaces(self) -> None:
        """Create all ROS2 publishers, subscribers and services."""
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        # Subscriber
        self._image_sub = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            qos,
        )

        # Publishers
        self._det_pub = self.create_publisher(String, "/vision/detections", 10)
        self._seg_pub = self.create_publisher(Image, "/vision/segmentation", 10)
        self._depth_pub = self.create_publisher(Image, "/vision/depth", 10)
        self._pose_pub = self.create_publisher(String, "/vision/poses", 10)
        self._scene_pub = self.create_publisher(String, "/vision/scene_description", 10)
        self._pc_pub = self.create_publisher(PointCloud2, "/vision/pointcloud", 10)

        # Services (using std_srvs-style String srv via custom logic)
        # We import lazily to avoid hard dep on service types
        try:
            from std_srvs.srv import Trigger  # type: ignore  # noqa: F401
        except ImportError:
            pass

        logger.info("VisionNode ROS2 interfaces initialised.")

    # ------------------------------------------------------------------
    # Pipeline lazy init
    # ------------------------------------------------------------------

    @property
    def pipeline(self) -> Any:
        """Lazily create and return the VisionPipeline."""
        if self._pipeline is None:
            from vision.vision_pipeline import VisionPipeline

            self._pipeline = VisionPipeline(
                device=self.device,
                enable_detection=self.enable_detection,
                enable_depth=self.enable_depth,
                enable_tracking=self.enable_tracking,
                detection_confidence=self.confidence_threshold,
            )
            logger.info("VisionPipeline initialised inside VisionNode.")
        return self._pipeline

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------

    def image_callback(self, msg: Any) -> None:
        """
        Process an incoming ROS Image message.

        Converts the message to a numpy array, runs the vision pipeline,
        and publishes results to all output topics.

        Args:
            msg: sensor_msgs/Image message.
        """
        try:
            from ros2_interface.vision_nodes.image_converter import ImageConverter

            image = ImageConverter.ros_to_cv2(msg)
        except Exception as exc:
            logger.error("Image conversion failed: %s", exc)
            return

        # Store for service callbacks
        self._last_image = image

        try:
            result = self.pipeline.process_frame(image)
        except Exception as exc:
            logger.error("Pipeline processing failed: %s", exc)
            return

        stamp = getattr(getattr(msg, "header", None), "stamp", None)
        self._publish_results(result, stamp)

    def _publish_results(self, result: Any, stamp: Any) -> None:
        """Publish all pipeline outputs to their respective topics."""
        if not _ROS2_AVAILABLE:
            return

        # Detections
        det_dicts = [
            d.to_dict() if hasattr(d, "to_dict") else str(d)
            for d in result.detections
        ]
        det_msg = String()
        det_msg.data = json.dumps(det_dicts)
        self._det_pub.publish(det_msg)

        # Segmentation mask
        if result.segmentation is not None:
            try:
                from ros2_interface.vision_nodes.image_converter import ImageConverter

                seg_msg = ImageConverter.cv2_to_ros(
                    result.segmentation.astype(np.uint8),
                    encoding="mono8",
                    stamp=stamp,
                )
                self._seg_pub.publish(seg_msg)
            except Exception as exc:
                logger.warning("Segmentation publish failed: %s", exc)

        # Depth map
        if result.depth_map is not None:
            try:
                from ros2_interface.vision_nodes.image_converter import ImageConverter

                depth_msg = ImageConverter.depth_to_ros(
                    result.depth_map, stamp=stamp
                )
                self._depth_pub.publish(depth_msg)
            except Exception as exc:
                logger.warning("Depth publish failed: %s", exc)

        # Poses
        pose_dicts = [
            p.to_dict() if hasattr(p, "to_dict") else str(p)
            for p in result.poses
        ]
        pose_msg = String()
        pose_msg.data = json.dumps(pose_dicts)
        self._pose_pub.publish(pose_msg)

        # Scene description
        scene_msg = String()
        scene_msg.data = result.scene_description or ""
        self._scene_pub.publish(scene_msg)

    def find_object_callback(self, request: Any, response: Any) -> Any:
        """
        Service callback to find an object in the latest frame.

        Args:
            request: Service request with a ``query`` string field.
            response: Service response populated with JSON bbox data.

        Returns:
            Populated response object.
        """
        query = getattr(request, "query", "")
        try:
            # Re-use the last frame stored in result if available
            result_dict = {"found": False, "bbox": [], "confidence": 0.0}
            if hasattr(self, "_last_image") and self._last_image is not None:
                from vision.vision_pipeline import VisionPipeline

                obj = self.pipeline.find_object(self._last_image, query)
                result_dict = {
                    "found": obj.get("score", 0.0) > 0.0,
                    "bbox": obj.get("region") or [],
                    "confidence": float(obj.get("score", 0.0)),
                }
        except Exception as exc:
            logger.error("find_object_callback error: %s", exc)

        response.data = json.dumps(result_dict)
        return response

    def analyze_scene_callback(self, request: Any, response: Any) -> Any:
        """
        Service callback to perform full scene analysis.

        Args:
            request: Empty service request (trigger).
            response: Service response populated with JSON scene data.

        Returns:
            Populated response object.
        """
        try:
            result_dict: dict = {"description": "", "objects": [], "spatial_map": {}}
            if hasattr(self, "_last_image") and self._last_image is not None:
                scene = self.pipeline.analyze_scene(self._last_image)
                det_dicts = [
                    d.to_dict() if hasattr(d, "to_dict") else str(d)
                    for d in scene.get("detections", [])
                ]
                result_dict = {
                    "description": scene.get("description", ""),
                    "objects": det_dicts,
                    "spatial_map": {},
                }
        except Exception as exc:
            logger.error("analyze_scene_callback error: %s", exc)
            result_dict = {"description": "", "objects": [], "spatial_map": {}}

        response.data = json.dumps(result_dict)
        return response


def main(args: Optional[list] = None) -> None:
    """Entry point: initialise rclpy, spin the VisionNode, then shutdown."""
    if not _ROS2_AVAILABLE:
        logger.error(
            "rclpy is not installed. Install ROS2 and source the environment "
            "before running the vision node."
        )
        return

    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
