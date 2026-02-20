"""Feature matcher between image pairs."""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class FeatureMatcher:
    """Match features between two images using OpenCV matchers.

    Supports brute-force (BFMatcher) and FLANN-based matching.

    Example::

        matcher = FeatureMatcher(method="bf")
        matches = matcher.match(descs_a, descs_b)
        H, mask = matcher.find_homography(kps_a, kps_b, matches)
    """

    def __init__(
        self,
        method: str = "bf",
        cross_check: bool = True,
        ratio_threshold: float = 0.75,
    ) -> None:
        """
        Args:
            method: ``"bf"`` for BFMatcher or ``"flann"`` for FLANN.
            cross_check: Enable cross-check filtering (BFMatcher only).
            ratio_threshold: Lowe's ratio test threshold (FLANN only).
        """
        self.method = method
        self.cross_check = cross_check
        self.ratio_threshold = ratio_threshold
        self._matcher = None

    def _build_matcher(self, descriptor_type: str = "binary"):
        """Create the underlying OpenCV matcher."""
        import cv2

        if self.method == "flann":
            if descriptor_type == "binary":
                index_params = {"algorithm": 6, "table_number": 12, "key_size": 20, "multi_probe_level": 2}
            else:
                index_params = {"algorithm": 1, "trees": 5}
            search_params = {"checks": 50}
            self._matcher = cv2.FlannBasedMatcher(index_params, search_params)
        else:
            norm = cv2.NORM_HAMMING if descriptor_type == "binary" else cv2.NORM_L2
            self._matcher = cv2.BFMatcher(norm, crossCheck=self.cross_check)

    def match(
        self,
        descs_a: np.ndarray,
        descs_b: np.ndarray,
    ) -> list:
        """Match descriptors and return filtered matches.

        Args:
            descs_a: Descriptors from image A of shape ``(N, D)``.
            descs_b: Descriptors from image B of shape ``(M, D)``.

        Returns:
            List of ``cv2.DMatch`` sorted by ascending distance.
        """
        if descs_a is None or descs_b is None:
            return []
        if len(descs_a) < 2 or len(descs_b) < 2:
            return []

        try:
            import cv2

            dtype_str = "binary" if descs_a.dtype == np.uint8 else "float"
            if self._matcher is None:
                self._build_matcher(dtype_str)

            if self.method == "flann" and descs_a.dtype == np.uint8:
                # FLANN LSH requires float
                descs_a = descs_a.astype(np.float32)
                descs_b = descs_b.astype(np.float32)

            if self.method == "flann" or not self.cross_check:
                knn = self._matcher.knnMatch(descs_a, descs_b, k=2)
                good = []
                for pair in knn:
                    if len(pair) == 2:
                        m, n = pair
                        if m.distance < self.ratio_threshold * n.distance:
                            good.append(m)
                return sorted(good, key=lambda m: m.distance)
            else:
                matches = self._matcher.match(descs_a, descs_b)
                return sorted(matches, key=lambda m: m.distance)
        except Exception as exc:
            logger.error("FeatureMatcher.match failed: %s", exc)
            return []

    def find_homography(
        self,
        kps_a: list,
        kps_b: list,
        matches: list,
        method: str = "ransac",
    ) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Estimate homography from matched keypoints.

        Args:
            kps_a: Keypoints from image A.
            kps_b: Keypoints from image B.
            matches: List of ``cv2.DMatch``.
            method: ``"ransac"`` or ``"lmeds"``.

        Returns:
            Tuple of ``(H, mask)`` where ``H`` is the 3×3 homography matrix
            and ``mask`` is the inlier mask.  Returns ``(None, None)`` on
            failure.
        """
        if len(matches) < 4:
            return None, None

        try:
            import cv2

            src = np.float32([kps_a[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst = np.float32([kps_b[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
            cv_method = cv2.RANSAC if method == "ransac" else cv2.LMEDS
            H, mask = cv2.findHomography(src, dst, cv_method, 5.0)
            return H, mask
        except Exception as exc:
            logger.error("FeatureMatcher.find_homography failed: %s", exc)
            return None, None
