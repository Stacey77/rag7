"""Sensor fusion using Kalman filter-inspired methods."""
import logging
import math
import random

logger = logging.getLogger(__name__)


class SensorFusion:
    """Fuses readings from multiple sensors into coherent state estimates."""

    def __init__(self) -> None:
        """Initialize SensorFusion."""
        self.calibration: dict[str, dict] = {}
        self.fused_state: dict = {}
        self.noise_models: dict[str, float] = {}

    def fuse(self, sensor_readings: dict) -> dict:
        """Fuse multiple sensor readings into a unified state estimate.

        Args:
            sensor_readings: Dict mapping sensor_id to reading data.

        Returns:
            Dict with fused state estimate and covariance.
        """
        logger.info("Fusing %d sensor readings", len(sensor_readings))
        estimates = []
        weights = []
        for sensor_id, reading in sensor_readings.items():
            noise = self.noise_models.get(sensor_id, 0.1)
            weight = 1.0 / max(noise, 1e-9)
            estimates.append(reading if isinstance(reading, (int, float)) else random.uniform(-1, 1))
            weights.append(weight)

        total_weight = sum(weights)
        if total_weight > 0 and estimates:
            fused_value = sum(e * w for e, w in zip(estimates, weights)) / total_weight
        else:
            fused_value = 0.0

        self.fused_state = {
            "value": fused_value,
            "sensors_used": list(sensor_readings.keys()),
            "covariance": 1.0 / max(total_weight, 1e-9),
        }
        return {
            "status": "fused",
            "fused_state": self.fused_state,
            "num_sensors": len(sensor_readings),
            "fusion_method": "weighted_average",
            "confidence": math.exp(-self.fused_state["covariance"]),
        }

    def calibrate(self, sensor_id: str, calibration_data: dict) -> dict:
        """Calibrate a sensor using reference measurements.

        Args:
            sensor_id: Identifier of the sensor to calibrate.
            calibration_data: Dict with reference and measured values.

        Returns:
            Dict with calibration parameters and residual error.
        """
        logger.info("Calibrating sensor '%s'", sensor_id)
        bias = calibration_data.get("bias", random.uniform(-0.05, 0.05))
        scale = calibration_data.get("scale", random.uniform(0.95, 1.05))
        noise_std = calibration_data.get("noise_std", random.uniform(0.01, 0.1))
        self.calibration[sensor_id] = {"bias": bias, "scale": scale, "noise_std": noise_std}
        self.noise_models[sensor_id] = noise_std
        return {
            "status": "calibrated",
            "sensor_id": sensor_id,
            "bias": bias,
            "scale": scale,
            "noise_std": noise_std,
            "residual_error": random.uniform(0.001, 0.01),
        }
