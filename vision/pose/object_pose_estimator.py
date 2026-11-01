"""6-DoF object pose estimator using PnP with template matching."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ObjectPose:
    """6-DoF pose of a detected object.

    Attributes:
        rotation: 3×3 rotation matrix.
        translation: 3-element translation vector in metres.
        object_class: Class label.
        confidence: Pose estimation confidence.
        reprojection_error: Mean reprojection error in pixels.
    """

    rotation: np.ndarray      # (3, 3)
    translation: np.ndarray   # (3,)
    object_class: str
    confidence: float
    reprojection_error: float = 0.0


class ObjectPoseEstimator:
    """Estimate 6-DoF object pose using feature matching and PnP.

    Uses ORB feature matching between a reference template and the query
    image to find 2D–3D correspondences, then solves the PnP problem with
    RANSAC via OpenCV.

    Example::

        estimator = ObjectPoseEstimator(intrinsics=K)
        template = cv2.imread("template.png")
        estimator.register_template("mug", template, points_3d)
        pose = estimator.estimate(image, "mug")
    """

    def __init__(
        self,
        intrinsics: Optional[np.ndarray] = None,
        dist_coeffs: Optional[np.ndarray] = None,
    ) -> None:
        """
        Args:
            intrinsics: 3×3 camera intrinsics matrix ``K``.
            dist_coeffs: Distortion coefficients (5 or 8 elements).
        """
        if intrinsics is None:
            # Default pinhole camera
            intrinsics = np.array(
                [[500.0, 0, 320.0],
                 [0, 500.0, 240.0],
                 [0, 0, 1.0]],
                dtype=np.float32,
            )
        self.intrinsics = intrinsics
        self.dist_coeffs = dist_coeffs if dist_coeffs is not None else np.zeros(5, dtype=np.float32)
        self._templates: dict = {}  # name -> (keypoints, descriptors, points_3d)
        self._orb = None

    def _get_orb(self):
        import cv2
        if self._orb is None:
            self._orb = cv2.ORB_create(nfeatures=1000)
        return self._orb

    def register_template(
        self,
        name: str,
        template_image: np.ndarray,
        points_3d: np.ndarray,
    ) -> None:
        """Register a reference object template.

        Args:
            name: Unique object name.
            template_image: BGR reference image.
            points_3d: Array of shape ``(N, 3)`` with 3-D model points
                       corresponding to template keypoints.
        """
        import cv2
        orb = self._get_orb()
        gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
        kps, descs = orb.detectAndCompute(gray, None)
        self._templates[name] = (kps, descs, points_3d)
        logger.info("Registered template '%s' with %d keypoints", name, len(kps))

    def estimate(
        self,
        image: np.ndarray,
        object_class: str,
    ) -> Optional[ObjectPose]:
        """Estimate the 6-DoF pose of *object_class* in *image*.

        Args:
            image: BGR query image.
            object_class: Name of a registered template.

        Returns:
            :class:`ObjectPose` or ``None`` if estimation failed.
        """
        if object_class not in self._templates:
            logger.warning("Template '%s' not registered", object_class)
            return None

        try:
            import cv2
            orb = self._get_orb()
            tpl_kps, tpl_descs, pts_3d = self._templates[object_class]

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            q_kps, q_descs = orb.detectAndCompute(gray, None)
            if q_descs is None or len(q_kps) < 4:
                return None

            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(tpl_descs, q_descs)
            matches = sorted(matches, key=lambda m: m.distance)

            if len(matches) < 4:
                return None

            n = min(len(matches), len(pts_3d))
            object_pts = pts_3d[:n].astype(np.float32)
            image_pts = np.float32([q_kps[m.trainIdx].pt for m in matches[:n]])

            success, rvec, tvec, inliers = cv2.solvePnPRansac(
                object_pts,
                image_pts,
                self.intrinsics,
                self.dist_coeffs,
                confidence=0.99,
                reprojectionError=8.0,
            )

            if not success or inliers is None:
                return None

            R, _ = cv2.Rodrigues(rvec)

            # Compute reprojection error
            proj_pts, _ = cv2.projectPoints(
                object_pts[inliers[:, 0]], rvec, tvec,
                self.intrinsics, self.dist_coeffs
            )
            rep_err = float(
                np.mean(
                    np.linalg.norm(proj_pts.squeeze() - image_pts[inliers[:, 0]], axis=1)
                )
            )
            conf = min(1.0, len(inliers) / len(matches))

            return ObjectPose(
                rotation=R.astype(np.float32),
                translation=tvec.squeeze().astype(np.float32),
                object_class=object_class,
                confidence=conf,
                reprojection_error=rep_err,
            )
        except Exception as exc:
            logger.error("ObjectPoseEstimator.estimate failed: %s", exc)
            return None
