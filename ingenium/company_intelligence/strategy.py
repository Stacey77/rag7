"""Strategy: the company's positioning, priorities, and competitive edge."""
import logging

logger = logging.getLogger(__name__)


class Strategy:
    """Holds strategic priorities and the company's stated competitive edge."""

    def __init__(self) -> None:
        """Initialize Strategy with no priorities set."""
        self.priorities: list[dict] = []
        self.positioning: str = ""

    def set_positioning(self, statement: str) -> dict:
        """Set the company's market positioning statement.

        Args:
            statement: One-line description of how the company is positioned.

        Returns:
            Dict confirming the stored positioning.
        """
        logger.info("Setting positioning statement")
        self.positioning = statement
        return {"status": "set", "positioning": self.positioning}

    def add_priority(self, name: str, rank: int) -> dict:
        """Add or update a strategic priority.

        Args:
            name: Priority label (e.g. "expand into enterprise").
            rank: Lower numbers are higher priority.

        Returns:
            Dict with the current ordered priority list.
        """
        logger.info("Adding strategic priority '%s' at rank %d", name, rank)
        self.priorities = [p for p in self.priorities if p["name"] != name]
        self.priorities.append({"name": name, "rank": rank})
        self.priorities.sort(key=lambda p: p["rank"])
        return {"status": "updated", "priorities": list(self.priorities)}

    def snapshot(self) -> dict:
        """Return the current strategic context.

        Returns:
            Dict with positioning and ranked priorities.
        """
        return {"positioning": self.positioning, "priorities": list(self.priorities)}
