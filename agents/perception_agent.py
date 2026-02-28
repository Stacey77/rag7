"""
Perception agent module for the RAG7 AGI Robotics Framework.

Handles processing of multi-modal sensor data including RGB-D camera,
2-D LiDAR, and IMU readings.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np

from agents.base_agent import BaseAgent

try:
    import torch  # noqa: F401

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class PerceptionAgent(BaseAgent):
    """Agent responsible for processing raw sensor observations.

    Processes camera images, LiDAR scans, and IMU data into structured
    perception outputs that higher-level agents can consume.

    Args:
        config: Configuration dictionary (see config/agent_config.yaml).
        device: Compute device for neural network inference ('cpu' or 'cuda').
    """

    def __init__(
        self,
        config: Dict[str, Any],
        device: str = "cpu",
    ) -> None:
        """Initialize the perception agent."""
        super().__init__(
            name="perception_agent",
            config=config,
            logger=logging.getLogger("rag7.perception"),
        )
        self._device = device
        self._model = None
        self._confidence_threshold = config.get("confidence_threshold", 0.7)
        model_path = config.get("model_path")
        if model_path and TORCH_AVAILABLE:
            self._try_load_model(model_path)

    # ------------------------------------------------------------------
    # Abstract method implementations
    # ------------------------------------------------------------------

    def perceive(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Process a multi-modal sensor observation.

        Args:
            observation: Dictionary that may contain:
                - ``image``: numpy array (H x W x C) from RGB-D camera.
                - ``lidar``: list or array of range measurements.
                - ``imu``: dict with ``acceleration`` and ``angular_velocity``.

        Returns:
            Dictionary with keys:
                - ``detections``: list of detected objects.
                - ``position``: estimated robot position (if available).
                - ``orientation``: estimated robot orientation.
                - ``nearest_obstacle``: closest obstacle distance in metres.
        """
        result: Dict[str, Any] = {
            "detections": [],
            "position": self._state.get("position", {"x": 0.0, "y": 0.0, "z": 0.0}),
            "orientation": {"roll": 0.0, "pitch": 0.0, "yaw": 0.0},
            "nearest_obstacle": float("inf"),
        }

        if "image" in observation and observation["image"] is not None:
            result["detections"] = self._process_image(observation["image"])

        if "lidar" in observation and observation["lidar"] is not None:
            result["nearest_obstacle"] = self._process_lidar(observation["lidar"])

        if "imu" in observation and observation["imu"] is not None:
            result["orientation"] = self._process_imu(observation["imu"])

        self.update_state("last_perception", result)
        self.add_to_memory(result)
        return result

    def reason(self, context: Any) -> Dict[str, Any]:
        """Analyse recent perception data and describe the current scene.

        Args:
            context: Optional additional context (currently unused).

        Returns:
            Dictionary with ``scene_description``, ``num_objects``,
            ``obstacle_detected``, and ``safe_to_proceed`` fields.
        """
        last = self._state.get("last_perception", {})
        detections = last.get("detections", [])
        nearest = last.get("nearest_obstacle", float("inf"))
        obstacle_detected = nearest < self._config.get("collision_threshold", 0.3)

        scene: Dict[str, Any] = {
            "scene_description": f"Detected {len(detections)} object(s).",
            "num_objects": len(detections),
            "obstacle_detected": obstacle_detected,
            "safe_to_proceed": not obstacle_detected,
        }
        self._logger.debug("Scene analysis: %s", scene)
        return scene

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Update internal model parameters based on an action directive.

        Args:
            action: Dictionary specifying the action, e.g.
                ``{"type": "update_threshold", "value": 0.8}``.

        Returns:
            Acknowledgement dictionary with ``status`` key.
        """
        action_type = action.get("type", "")
        if action_type == "update_threshold":
            self._confidence_threshold = float(action.get("value", self._confidence_threshold))
            self._logger.info("Confidence threshold updated to %.2f", self._confidence_threshold)
        else:
            self._logger.warning("Unknown action type for PerceptionAgent: %s", action_type)
        return {"status": "ok", "action": action_type}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _process_image(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Run object detection on a single image frame.

        Uses a loaded PyTorch model when available; otherwise returns
        mock detections for testing and fallback purposes.

        Args:
            image: RGB image as a numpy array of shape (H, W, C).

        Returns:
            List of detection dictionaries, each with ``label``,
            ``confidence``, and ``bbox`` keys.
        """
        if self._model is not None and TORCH_AVAILABLE:
            try:
                import torch

                tensor = self._preprocess(image)
                with torch.no_grad():
                    outputs = self._model(tensor)
                return self._parse_model_output(outputs)
            except Exception as exc:  # noqa: BLE001
                self._logger.warning("Model inference failed: %s", exc)

        # Fallback: mock detections based on image statistics
        mock_detections = [
            {
                "label": "unknown_object",
                "confidence": 0.75,
                "bbox": [10, 10, 50, 50],
            }
        ]
        return mock_detections

    def _process_lidar(self, data: Any) -> float:
        """Determine the nearest obstacle distance from a LiDAR scan.

        Args:
            data: Array-like of range measurements in metres.

        Returns:
            Minimum valid range reading (nearest obstacle distance).
        """
        try:
            ranges = np.asarray(data, dtype=float)
            valid = ranges[np.isfinite(ranges) & (ranges > 0)]
            return float(np.min(valid)) if len(valid) > 0 else float("inf")
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("LiDAR processing failed: %s", exc)
            return float("inf")

    def _process_imu(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Extract orientation estimates from IMU data.

        Args:
            data: Dictionary with optional ``roll``, ``pitch``, ``yaw`` keys
                or ``angular_velocity`` sub-dict.

        Returns:
            Orientation dictionary with ``roll``, ``pitch``, ``yaw`` in radians.
        """
        orientation = {
            "roll": float(data.get("roll", 0.0)),
            "pitch": float(data.get("pitch", 0.0)),
            "yaw": float(data.get("yaw", 0.0)),
        }
        return orientation

    def _preprocess(self, image: np.ndarray) -> Any:
        """Preprocess a numpy image for model inference.

        Args:
            image: Raw numpy image array.

        Returns:
            Preprocessed torch Tensor on the configured device.
        """
        import torch

        if image.dtype != np.float32:
            image = image.astype(np.float32) / 255.0
        tensor = torch.from_numpy(image).permute(2, 0, 1).unsqueeze(0)
        return tensor.to(self._device)

    def _parse_model_output(self, outputs: Any) -> List[Dict[str, Any]]:
        """Convert raw model output to detection dictionaries.

        Args:
            outputs: Raw model output tensors.

        Returns:
            List of detection dictionaries.
        """
        # Placeholder – real implementation would parse model-specific format
        return []

    def _try_load_model(self, path: str) -> None:
        """Attempt to load a detection model from disk.

        Args:
            path: Filesystem path to the serialised model file.
        """
        try:
            import torch

            self._model = torch.load(path, map_location=self._device)
            self._model.eval()
            self._logger.info("Detection model loaded from '%s'.", path)
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Could not load model from '%s': %s", path, exc)
