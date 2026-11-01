"""Integration hub: the connective tissue between both hemispheres and the outside world."""
import logging

from ..integrations import CRM, Analytics, Calendar, Email, Finance, Integration, WebBuilder

logger = logging.getLogger(__name__)


class IntegrationHub:
    """Owns one instance of each external adapter and connects them on demand."""

    def __init__(self) -> None:
        """Register the six integrations that Ingenium plugs into."""
        self.adapters: dict[str, Integration] = {
            "crm": CRM(),
            "web_builder": WebBuilder(),
            "email": Email(),
            "finance": Finance(),
            "analytics": Analytics(),
            "calendar": Calendar(),
        }

    def connect_all(self) -> dict:
        """Connect every registered integration.

        Returns:
            Dict mapping integration name to its connection status.
        """
        logger.info("Connecting all integrations")
        return {name: adapter.connect() for name, adapter in self.adapters.items()}

    def get(self, name: str) -> Integration:
        """Fetch a connected adapter by name.

        Args:
            name: One of crm, web_builder, email, finance, analytics, calendar.

        Returns:
            The requested Integration instance.

        Raises:
            KeyError: If no integration is registered under that name.
        """
        if name not in self.adapters:
            raise KeyError(f"Unknown integration: {name}")
        return self.adapters[name]

    def status(self) -> dict:
        """Report which integrations are currently connected.

        Returns:
            Dict mapping integration name to a bool connected flag.
        """
        return {name: adapter.connected for name, adapter in self.adapters.items()}
