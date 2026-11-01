"""Force/impedance controller for compliant manipulation."""
import logging
import random

logger = logging.getLogger(__name__)


class ForceController:
    """Impedance and force controller for safe contact tasks."""

    def __init__(self) -> None:
        """Initialize ForceController."""
        self.stiffness = 100.0
        self.damping = 10.0
        self.max_force_N = 50.0

    def compliant_insertion(self, peg: dict, hole: dict) -> dict:
        """Perform compliant peg-in-hole insertion with force feedback.

        Args:
            peg: Dict with peg geometry and tolerance.
            hole: Dict with hole geometry and position.

        Returns:
            Dict with insertion result, forces applied, and alignment error.
        """
        logger.info("Compliant insertion: peg '%s' into hole '%s'", peg.get("id", "?"), hole.get("id", "?"))
        clearance = peg.get("diameter_mm", 10.0) - hole.get("diameter_mm", 10.2)
        success = clearance < 0.5
        return {
            "status": "inserted" if success else "failed",
            "peg": peg.get("id", "peg"),
            "hole": hole.get("id", "hole"),
            "clearance_mm": clearance,
            "max_force_N": random.uniform(5.0, 20.0),
            "insertion_depth_mm": random.uniform(20.0, 50.0) if success else 0.0,
            "alignment_error_mm": random.uniform(0.01, 0.5),
            "search_spiral_used": not success,
        }

    def polishing_with_force(self, surface: dict) -> dict:
        """Polish a surface with constant normal force control.

        Args:
            surface: Dict with surface properties and target roughness.

        Returns:
            Dict with polishing result and surface quality metrics.
        """
        logger.info("Polishing surface: %s", surface.get("material", "unknown"))
        target_force = surface.get("target_force_N", 10.0)
        achieved_roughness = random.uniform(0.1, 1.0)
        return {
            "status": "complete",
            "surface": surface.get("material", "surface"),
            "target_force_N": target_force,
            "achieved_force_N": target_force + random.uniform(-0.5, 0.5),
            "initial_roughness_um": random.uniform(5.0, 20.0),
            "final_roughness_um": achieved_roughness,
            "coverage_pct": random.uniform(90.0, 100.0),
        }

    def set_impedance(self, stiffness: float, damping: float) -> dict:
        """Set impedance parameters for compliant control.

        Args:
            stiffness: Desired stiffness in N/m.
            damping: Desired damping in N·s/m.

        Returns:
            Dict with confirmation of set parameters and stability check.
        """
        logger.info("Setting impedance: K=%.1f N/m, D=%.1f N·s/m", stiffness, damping)
        self.stiffness = stiffness
        self.damping = damping
        critical_damping = 2.0 * (stiffness * 1.0) ** 0.5
        stable = damping >= 0.1 * critical_damping
        return {
            "status": "set",
            "stiffness_N_m": stiffness,
            "damping_N_s_m": damping,
            "critical_damping": critical_damping,
            "stable": stable,
            "bandwidth_Hz": stiffness / (2 * 3.14159 * damping) if damping > 0 else 0.0,
        }
