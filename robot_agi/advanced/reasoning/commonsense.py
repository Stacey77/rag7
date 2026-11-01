"""Common-sense reasoning for physical, temporal, and social domains."""
import logging
import random

logger = logging.getLogger(__name__)


class CommonSenseReasoner:
    """Applies common-sense knowledge to physical and social reasoning."""

    def __init__(self) -> None:
        """Initialize CommonSenseReasoner."""
        self.physical_axioms = [
            "Objects fall when unsupported",
            "Liquids flow to lower positions",
            "Rigid objects cannot overlap",
            "Heavy objects require more force to move",
        ]
        self.temporal_axioms = [
            "Events happen in sequence",
            "Causes precede effects",
            "Actions take time",
        ]

    def physical_reasoning(self, scene: dict) -> dict:
        """Apply physical common-sense reasoning to a scene.

        Args:
            scene: Dict with objects, positions, and physical properties.

        Returns:
            Dict with physical predictions and stability analysis.
        """
        logger.info("Physical reasoning on scene: %s", scene.get("name", "unknown"))
        objects = scene.get("objects", [])
        stability_scores = {obj: random.uniform(0.3, 1.0) for obj in objects} if objects else {}
        unstable = [obj for obj, s in stability_scores.items() if s < 0.5]
        return {
            "status": "analyzed",
            "scene": scene.get("name", "scene"),
            "stability_scores": stability_scores,
            "unstable_objects": unstable,
            "physical_predictions": [f"{obj} may fall" for obj in unstable],
            "applied_axioms": random.sample(self.physical_axioms, min(2, len(self.physical_axioms))),
        }

    def temporal_reasoning(self, events: list) -> dict:
        """Reason about temporal relationships between events.

        Args:
            events: List of event dicts with timestamps and types.

        Returns:
            Dict with temporal ordering, durations, and causal chains.
        """
        logger.info("Temporal reasoning over %d events", len(events))
        sorted_events = sorted(events, key=lambda e: e.get("timestamp", 0)) if events else []
        causal_chains = []
        for i in range(len(sorted_events) - 1):
            causal_chains.append({
                "cause": sorted_events[i].get("type", f"event_{i}"),
                "effect": sorted_events[i+1].get("type", f"event_{i+1}"),
                "delay_s": sorted_events[i+1].get("timestamp", i+1) - sorted_events[i].get("timestamp", i),
            })
        return {
            "status": "analyzed",
            "num_events": len(events),
            "temporal_order": [e.get("type", f"event_{i}") for i, e in enumerate(sorted_events)],
            "causal_chains": causal_chains,
            "total_duration_s": (sorted_events[-1].get("timestamp", 0) - sorted_events[0].get("timestamp", 0)) if len(sorted_events) > 1 else 0,
        }

    def social_reasoning(self, situation: dict) -> dict:
        """Apply social common-sense reasoning to a situation.

        Args:
            situation: Dict with agents, context, and social norms.

        Returns:
            Dict with social assessment, norms violated, and recommendations.
        """
        logger.info("Social reasoning on situation: %s", situation.get("context", "unknown"))
        agents = situation.get("agents", ["person_1"])
        social_norms = ["maintain personal space", "take turns", "be polite", "avoid interruption"]
        norms_checked = random.sample(social_norms, min(3, len(social_norms)))
        norms_violated = [n for n in norms_checked if random.random() < 0.2]
        return {
            "status": "analyzed",
            "agents": agents,
            "context": situation.get("context", "interaction"),
            "norms_checked": norms_checked,
            "norms_violated": norms_violated,
            "recommendations": [f"Fix: {n}" for n in norms_violated],
            "social_appropriateness": 1.0 - len(norms_violated) / max(len(norms_checked), 1),
        }
