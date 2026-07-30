"""Company Intelligence hemisphere: strategy, customer data, goals, knowledge, brand."""
import logging

from .brand import Brand
from .customer_data import CustomerData
from .goals import Goals
from .knowledge import Knowledge
from .strategy import Strategy

logger = logging.getLogger(__name__)


class CompanyIntelligence:
    """Aggregates the five company-edge modules into one queryable hemisphere."""

    def __init__(self) -> None:
        """Initialize each company-edge module."""
        self.strategy = Strategy()
        self.customer_data = CustomerData()
        self.goals = Goals()
        self.knowledge = Knowledge()
        self.brand = Brand()

    def snapshot(self) -> dict:
        """Build the company edge: a single context object the agent side can act on.

        Returns:
            Dict with a key per module (strategy, customer_data, goals,
            knowledge, brand) holding that module's current state.
        """
        logger.info("Building company edge snapshot")
        return {
            "strategy": self.strategy.snapshot(),
            "customer_data": self.customer_data.snapshot(),
            "goals": self.goals.snapshot(),
            "knowledge": self.knowledge.snapshot(),
            "brand": self.brand.snapshot(),
        }
