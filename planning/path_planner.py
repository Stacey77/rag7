"""
Path planner module for the RAG7 planning system.

Implements A* search on a 2-D occupancy grid to compute
collision-free paths between two poses.
"""

import heapq
import logging
from typing import Dict, List, Optional, Set, Tuple


class PathPlanner:
    """Grid-based path planner using the A* algorithm.

    Operates on a discrete occupancy grid.  Obstacle cells are treated
    as impassable; all other cells have unit traversal cost.

    Args:
        grid_resolution: Physical size of each grid cell in metres.
    """

    def __init__(self, grid_resolution: float = 0.1) -> None:
        """Initialize the path planner."""
        self._logger = logging.getLogger("rag7.planning.path")
        self._resolution = grid_resolution

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
        obstacles: Optional[List[Tuple[float, float]]] = None,
    ) -> List[Tuple[float, float]]:
        """Compute a collision-free path from start to goal using A*.

        Args:
            start: (x, y) start position in world coordinates.
            goal: (x, y) goal position in world coordinates.
            obstacles: Optional list of (x, y) obstacle positions in
                world coordinates.

        Returns:
            List of (x, y) waypoint tuples from start to goal, or an
            empty list if no path is found.
        """
        obstacles = obstacles or []
        obstacle_set: Set[Tuple[int, int]] = {
            self._to_grid(ox, oy) for ox, oy in obstacles
        }
        start_cell = self._to_grid(*start)
        goal_cell = self._to_grid(*goal)

        path_cells = self._astar(start_cell, goal_cell, obstacle_set)

        if path_cells is None:
            self._logger.warning("No path found from %s to %s.", start, goal)
            return []

        return [self._to_world(r, c) for r, c in path_cells]

    # ------------------------------------------------------------------
    # Private A* implementation
    # ------------------------------------------------------------------

    def _astar(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        obstacles: Set[Tuple[int, int]],
    ) -> Optional[List[Tuple[int, int]]]:
        """Run A* search on the grid.

        Args:
            start: Grid (row, col) start cell.
            goal: Grid (row, col) goal cell.
            obstacles: Set of impassable grid cells.

        Returns:
            List of grid cells forming the path, or None if unreachable.
        """
        open_heap: List[Tuple[float, Tuple[int, int]]] = []
        heapq.heappush(open_heap, (0.0, start))
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        g_score: Dict[Tuple[int, int], float] = {start: 0.0}

        while open_heap:
            _, current = heapq.heappop(open_heap)

            if current == goal:
                return self._reconstruct(came_from, goal)

            for neighbour in self._neighbours(current):
                if neighbour in obstacles:
                    continue
                tentative_g = g_score[current] + 1.0
                if tentative_g < g_score.get(neighbour, float("inf")):
                    came_from[neighbour] = current
                    g_score[neighbour] = tentative_g
                    f = tentative_g + self._heuristic(neighbour, goal)
                    heapq.heappush(open_heap, (f, neighbour))

        return None  # No path found

    @staticmethod
    def _heuristic(
        a: Tuple[int, int], b: Tuple[int, int]
    ) -> float:
        """Manhattan distance heuristic for A*.

        Args:
            a: First grid cell (row, col).
            b: Second grid cell (row, col).

        Returns:
            Manhattan distance between a and b.
        """
        return float(abs(a[0] - b[0]) + abs(a[1] - b[1]))

    @staticmethod
    def _neighbours(cell: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Return 4-connected grid neighbours of a cell.

        Args:
            cell: (row, col) grid cell.

        Returns:
            List of adjacent grid cells.
        """
        r, c = cell
        return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]

    @staticmethod
    def _reconstruct(
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]],
        goal: Tuple[int, int],
    ) -> List[Tuple[int, int]]:
        """Reconstruct the path from the came_from map.

        Args:
            came_from: Mapping from cell to its predecessor.
            goal: Goal cell.

        Returns:
            Ordered list of cells from start to goal.
        """
        path = []
        current: Optional[Tuple[int, int]] = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def _to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid cell indices.

        Args:
            x: World X coordinate.
            y: World Y coordinate.

        Returns:
            (row, col) grid cell.
        """
        return (int(round(y / self._resolution)), int(round(x / self._resolution)))

    def _to_world(self, row: int, col: int) -> Tuple[float, float]:
        """Convert grid cell indices to world coordinates.

        Args:
            row: Grid row index.
            col: Grid column index.

        Returns:
            (x, y) world coordinates.
        """
        return (col * self._resolution, row * self._resolution)
