"""Collective intelligence for stigmergic coordination."""
import logging
import random

logger = logging.getLogger(__name__)


class CollectiveIntelligence:
    """Implements stigmergy and quorum sensing for swarm intelligence."""

    def __init__(self) -> None:
        """Initialize CollectiveIntelligence."""
        self.pheromone_trails: dict[str, float] = {}
        self.evaporation_rate = 0.05
        self.quorum_threshold = 0.5

    def stigmergic_coordination(self, environment_markers: dict) -> dict:
        """Coordinate using indirect stigmergic communication via markers.

        Args:
            environment_markers: Dict with positions and pheromone levels.

        Returns:
            Dict with updated pheromone trails and recommended actions.
        """
        logger.info("Stigmergic coordination with %d markers", len(environment_markers))
        for marker_id, strength in environment_markers.items():
            current = self.pheromone_trails.get(marker_id, 0.0)
            self.pheromone_trails[marker_id] = current * (1 - self.evaporation_rate) + float(strength)

        best_trail = max(self.pheromone_trails, key=lambda k: self.pheromone_trails[k]) if self.pheromone_trails else None
        return {
            "status": "coordinated",
            "active_trails": len(self.pheromone_trails),
            "strongest_trail": best_trail,
            "recommended_direction": best_trail,
            "total_pheromone": sum(self.pheromone_trails.values()),
            "evaporation_rate": self.evaporation_rate,
        }

    def quorum_decision(self, robot_votes: list) -> dict:
        """Make a collective decision when quorum is reached.

        Args:
            robot_votes: List of vote dicts from individual robots.

        Returns:
            Dict with decision outcome and vote tallies.
        """
        logger.info("Quorum decision from %d votes", len(robot_votes))
        vote_counts: dict[str, int] = {}
        for vote in robot_votes:
            choice = str(vote.get("choice", "abstain"))
            vote_counts[choice] = vote_counts.get(choice, 0) + 1

        total_votes = len(robot_votes)
        quorum_reached = total_votes > 0
        if vote_counts and quorum_reached:
            winning_choice = max(vote_counts, key=lambda k: vote_counts[k])
            quorum_fraction = vote_counts[winning_choice] / total_votes
            quorum_reached = quorum_fraction >= self.quorum_threshold
        else:
            winning_choice = "no_decision"
            quorum_fraction = 0.0

        return {
            "status": "decided" if quorum_reached else "no_quorum",
            "decision": winning_choice if quorum_reached else None,
            "vote_counts": vote_counts,
            "quorum_fraction": quorum_fraction,
            "quorum_threshold": self.quorum_threshold,
            "total_votes": total_votes,
        }
