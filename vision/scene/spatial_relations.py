"""Compute spatial relationships between pairs of bounding boxes."""

from __future__ import annotations

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class SpatialRelations:
    """Compute spatial relationships between pairs of bounding boxes.

    Supported relationships:

    - ``above`` / ``below``
    - ``left_of`` / ``right_of``
    - ``on`` (one object resting on top of another)
    - ``in`` (one object contained inside another)
    - ``next_to`` (objects are spatially adjacent)

    Example::

        sr = SpatialRelations()
        rels = sr.compute((10, 10, 50, 50), (60, 10, 100, 50))
        # {'above': 0, 'below': 0, 'left_of': 1.0, 'right_of': 0, ...}
    """

    def compute(
        self,
        bbox_a: Tuple[float, float, float, float],
        bbox_b: Tuple[float, float, float, float],
        proximity_threshold: float = 0.5,
    ) -> Dict[str, float]:
        """Compute directional and topological relations from A to B.

        Args:
            bbox_a: Subject bounding box ``(x1, y1, x2, y2)``.
            bbox_b: Reference bounding box ``(x1, y1, x2, y2)``.
            proximity_threshold: Fraction of average box dimension for
                                  ``"next_to"`` classification.

        Returns:
            Dict mapping relation name to a confidence in ``[0, 1]``.
        """
        ax1, ay1, ax2, ay2 = bbox_a
        bx1, by1, bx2, by2 = bbox_b

        # Centres
        acx = (ax1 + ax2) / 2
        acy = (ay1 + ay2) / 2
        bcx = (bx1 + bx2) / 2
        bcy = (by1 + by2) / 2

        a_w, a_h = ax2 - ax1, ay2 - ay1
        b_w, b_h = bx2 - bx1, by2 - by1
        avg_dim = (a_w + a_h + b_w + b_h) / 4 + 1e-8

        dx = acx - bcx
        dy = acy - bcy
        dist = (dx ** 2 + dy ** 2) ** 0.5

        # Directional relations
        above = max(0.0, float(bcy - acy) / avg_dim)  # A is above B (A.cy < B.cy)
        below = max(0.0, float(acy - bcy) / avg_dim)
        left_of = max(0.0, float(bcx - acx) / avg_dim)
        right_of = max(0.0, float(acx - bcx) / avg_dim)

        # Normalise to [0, 1]
        above = min(above, 1.0)
        below = min(below, 1.0)
        left_of = min(left_of, 1.0)
        right_of = min(right_of, 1.0)

        # "next_to": close but not overlapping
        iou = self._iou(bbox_a, bbox_b)
        next_to = float(dist < avg_dim * proximity_threshold and iou < 0.2)

        # "in": A is inside B
        a_inside_b = float(
            ax1 >= bx1 and ay1 >= by1 and ax2 <= bx2 and ay2 <= by2
        )

        # "on": A is sitting on top of B (A is above B and vertically adjacent)
        vertical_gap = abs(ay2 - by1)
        on = float(
            above > 0.1
            and vertical_gap < avg_dim * 0.3
            and ax1 < bx2 and ax2 > bx1  # horizontal overlap
        )

        return {
            "above": above,
            "below": below,
            "left_of": left_of,
            "right_of": right_of,
            "next_to": next_to,
            "in": a_inside_b,
            "on": on,
        }

    @staticmethod
    def _iou(
        box_a: Tuple[float, float, float, float],
        box_b: Tuple[float, float, float, float],
    ) -> float:
        """Compute IoU between two bounding boxes."""
        ax1, ay1, ax2, ay2 = box_a
        bx1, by1, bx2, by2 = box_b
        ix1, iy1 = max(ax1, bx1), max(ay1, by1)
        ix2, iy2 = min(ax2, bx2), min(ay2, by2)
        iw = max(0.0, ix2 - ix1)
        ih = max(0.0, iy2 - iy1)
        inter = iw * ih
        a_area = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
        b_area = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
        union = a_area + b_area - inter
        return inter / union if union > 0 else 0.0
