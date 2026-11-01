"""Domain randomization for sim-to-real transfer."""
import logging
import random

logger = logging.getLogger(__name__)


class DomainRandomizer:
    """Randomizes simulation parameters to improve sim-to-real transfer."""

    def __init__(self) -> None:
        """Initialize DomainRandomizer."""
        self.randomization_ranges = {
            "gravity": (-11.0, -8.0),
            "friction": (0.3, 1.0),
            "mass_scale": (0.7, 1.3),
            "joint_damping": (0.01, 0.5),
        }

    def randomize_physics(self, sim_params: dict) -> dict:
        """Randomize physical simulation parameters.

        Args:
            sim_params: Dict with current simulation parameters.

        Returns:
            Dict with randomized physics parameters.
        """
        logger.info("Randomizing physics parameters")
        randomized = {}
        for param, (low, high) in self.randomization_ranges.items():
            base = sim_params.get(param, (low + high) / 2)
            noise = random.uniform(-0.1, 0.1) * (high - low)
            randomized[param] = max(low, min(high, float(base) + noise))
        randomized.update({k: v for k, v in sim_params.items() if k not in randomized})
        return {
            "status": "randomized",
            "randomized_params": randomized,
            "parameters_changed": len(self.randomization_ranges),
        }

    def randomize_visuals(self, scene: dict) -> dict:
        """Randomize visual appearance of the simulation scene.

        Args:
            scene: Dict with scene objects and their visual properties.

        Returns:
            Dict with randomized visual parameters.
        """
        logger.info("Randomizing visual parameters")
        objects = scene.get("objects", ["object_1"])
        visual_params = {}
        for obj in objects:
            visual_params[obj] = {
                "color": [random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1)],
                "texture": random.choice(["smooth", "rough", "metallic", "matte"]),
                "reflectance": random.uniform(0.0, 1.0),
                "lighting_scale": random.uniform(0.5, 2.0),
            }
        return {
            "status": "randomized",
            "visual_params": visual_params,
            "objects_modified": len(objects),
            "lighting_variation": random.uniform(0.5, 2.0),
        }

    def randomize_sensors(self, sensor_readings: dict) -> dict:
        """Add realistic noise to sensor readings for domain randomization.

        Args:
            sensor_readings: Dict with clean sensor readings.

        Returns:
            Dict with noise-augmented sensor readings.
        """
        logger.info("Randomizing sensor noise for %d sensors", len(sensor_readings))
        noisy_readings = {}
        for sensor_id, reading in sensor_readings.items():
            noise_std = random.uniform(0.01, 0.1)
            if isinstance(reading, (int, float)):
                noisy_readings[sensor_id] = float(reading) + random.gauss(0, noise_std)
            elif isinstance(reading, list):
                noisy_readings[sensor_id] = [v + random.gauss(0, noise_std) for v in reading]
            else:
                noisy_readings[sensor_id] = reading
        return {
            "status": "randomized",
            "noisy_readings": noisy_readings,
            "noise_model": "gaussian",
            "sensors_modified": len(sensor_readings),
        }
