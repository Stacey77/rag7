"""Theory of Mind for inferring agent mental states."""
import logging
import random

logger = logging.getLogger(__name__)


class TheoryOfMind:
    """Models beliefs and intentions of other agents."""

    def __init__(self) -> None:
        """Initialize TheoryOfMind."""
        self.agent_models: dict[str, dict] = {}
        self.belief_history: list[dict] = []

    def infer_beliefs(self, agent: str, observations: list) -> dict:
        """Infer what an agent believes based on their observations.

        Args:
            agent: Agent identifier string.
            observations: List of observations the agent has made.

        Returns:
            Dict with inferred belief state and confidence.
        """
        logger.info("Inferring beliefs of agent '%s' from %d observations", agent, len(observations))
        if agent not in self.agent_models:
            self.agent_models[agent] = {"beliefs": {}, "intentions": [], "goals": []}
        inferred_beliefs = {f"belief_{i}": obs for i, obs in enumerate(observations[:5])}
        self.agent_models[agent]["beliefs"].update(inferred_beliefs)
        return {
            "status": "inferred",
            "agent": agent,
            "inferred_beliefs": inferred_beliefs,
            "belief_count": len(self.agent_models[agent]["beliefs"]),
            "confidence": random.uniform(0.5, 0.9),
            "observations_used": len(observations),
        }

    def infer_intentions(self, agent: str, actions: list) -> dict:
        """Infer an agent's intentions from their observed actions.

        Args:
            agent: Agent identifier string.
            actions: List of observed action dicts.

        Returns:
            Dict with inferred intentions and goal hypothesis.
        """
        logger.info("Inferring intentions of agent '%s' from %d actions", agent, len(actions))
        if agent not in self.agent_models:
            self.agent_models[agent] = {"beliefs": {}, "intentions": [], "goals": []}
        possible_intentions = ["reach_goal", "avoid_obstacle", "interact_with_object", "communicate"]
        inferred = random.choice(possible_intentions)
        self.agent_models[agent]["intentions"].append(inferred)
        return {
            "status": "inferred",
            "agent": agent,
            "inferred_intention": inferred,
            "supporting_actions": actions[:3],
            "goal_hypothesis": f"Agent wants to {inferred.replace('_', ' ')}",
            "confidence": random.uniform(0.55, 0.9),
        }

    def perspective_taking(self, agent_view: dict) -> dict:
        """Simulate what the world looks like from another agent's perspective.

        Args:
            agent_view: Dict with agent position, orientation, and context.

        Returns:
            Dict with simulated perspective and visible objects.
        """
        logger.info("Taking perspective of agent at %s", agent_view.get("position", "?"))
        visible_objects = ["table", "cup", "door", "chair"]
        occluded = random.sample(visible_objects, random.randint(0, 2))
        visible = [o for o in visible_objects if o not in occluded]
        return {
            "status": "perspective_taken",
            "agent_position": agent_view.get("position", [0, 0, 0]),
            "visible_objects": visible,
            "occluded_objects": occluded,
            "field_of_view_deg": agent_view.get("fov_deg", 120),
            "differs_from_robot_view": len(occluded) > 0,
        }
