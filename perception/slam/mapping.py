"""
SLAM mapping module for the rag7 perception system.

Provides an occupancy-grid-based mapping and localisation system
suitable for 2-D LiDAR data.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class SLAMMapper:
    """Occupancy-grid SLAM mapper for 2-D LiDAR data.

    Maintains an occupancy grid map of the environment and provides
    simple scan-matching localisation.

    Args:
        map_resolution: Grid cell size in metres per cell.
        map_size: Number of cells along each axis (creates a square map).
    """

    # Cell value constants
    UNKNOWN = 0.5
    FREE = 0.0
    OCCUPIED = 1.0

    def __init__(
        self,
        map_resolution: float = 0.05,
        map_size: int = 100,
    ) -> None:
        """Initialize the SLAM mapper with an unknown occupancy grid."""
        self._logger = logging.getLogger("rag7.perception.slam")
        self._resolution = map_resolution
        self._size = map_size
        self._map = np.full((map_size, map_size), self.UNKNOWN, dtype=np.float32)
        self._pose: Dict[str, float] = {"x": 0.0, "y": 0.0, "theta": 0.0}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self, lidar_scan: Any, pose: Dict[str, float]) -> None:
        """Integrate a LiDAR scan into the occupancy grid map.

        Uses a simplified ray-casting model to mark free and occupied
        cells along each scan ray.

        Args:
            lidar_scan: Array-like of range measurements in metres.
                Values of ``inf`` or ``nan`` are ignored.
            pose: Robot pose dictionary with ``x``, ``y``, and ``theta``
                keys (theta in radians).
        """
        self._pose = dict(pose)
        ranges = np.asarray(lidar_scan, dtype=float)
        robot_cell = self._world_to_cell(pose["x"], pose["y"])
        num_rays = len(ranges)

        for i, r in enumerate(ranges):
            if not np.isfinite(r) or r <= 0:
                continue
            angle = pose.get("theta", 0.0) + (2 * np.pi * i / num_rays)
            end_x = pose["x"] + r * np.cos(angle)
            end_y = pose["y"] + r * np.sin(angle)
            end_cell = self._world_to_cell(end_x, end_y)
            self._ray_cast(robot_cell, end_cell)

        self._logger.debug("Map updated at pose (%.2f, %.2f).", pose["x"], pose["y"])

    def get_map(self) -> np.ndarray:
        """Return the current occupancy grid map.

        Returns:
            2-D numpy array of shape (map_size, map_size) with cell
            values in [0, 1] where 0 = free, 1 = occupied, 0.5 = unknown.
        """
        return self._map.copy()

    def localize(self, scan: Any) -> Dict[str, float]:
        """Estimate the robot pose from a LiDAR scan.

        This is a simplified placeholder that returns the last known
        pose.  A production implementation would use ICP or particle
        filters.

        Args:
            scan: LiDAR range measurements.

        Returns:
            Estimated pose dictionary with ``x``, ``y``, ``theta``,
            and ``confidence`` keys.
        """
        return {
            "x": self._pose["x"],
            "y": self._pose["y"],
            "theta": self._pose.get("theta", 0.0),
            "confidence": 0.8,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _world_to_cell(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid cell indices.

        Args:
            x: World X coordinate in metres.
            y: World Y coordinate in metres.

        Returns:
            (row, col) cell indices clamped to the grid bounds.
        """
        col = int(x / self._resolution) + self._size // 2
        row = int(y / self._resolution) + self._size // 2
        row = max(0, min(self._size - 1, row))
        col = max(0, min(self._size - 1, col))
        return row, col

    def _ray_cast(
        self, start: Tuple[int, int], end: Tuple[int, int]
    ) -> None:
        """Mark cells along a ray using Bresenham's line algorithm.

        Cells between start and end are marked free; the end cell is
        marked occupied.

        Args:
            start: (row, col) of the robot cell.
            end: (row, col) of the obstacle cell.
        """
        r0, c0 = start
        r1, c1 = end
        dr = abs(r1 - r0)
        dc = abs(c1 - c0)
        sr = 1 if r1 > r0 else -1
        sc = 1 if c1 > c0 else -1
        err = dr - dc
        r, c = r0, c0

        while True:
            if 0 <= r < self._size and 0 <= c < self._size:
                if (r, c) == (r1, c1):
                    self._map[r, c] = min(1.0, self._map[r, c] + 0.2)
                    break
                else:
                    self._map[r, c] = max(0.0, self._map[r, c] - 0.1)
            else:
                break

            e2 = 2 * err
            if e2 > -dc:
                err -= dc
                r += sr
            if e2 < dr:
                err += dr
                c += sc
