"""Base class every Ingenium integration adapter implements."""
import logging

logger = logging.getLogger(__name__)


class Integration:
    """Common lifecycle for an external system that Ingenium plugs into."""

    name = "integration"

    def __init__(self) -> None:
        """Initialize the integration in a disconnected state."""
        self.connected = False

    def connect(self) -> dict:
        """Mark the integration as connected.

        Real adapters override this to authenticate against a live API;
        this base implementation just flips the connected flag so the
        rest of the brain can be developed and tested without live
        credentials.

        Returns:
            Dict with the integration name and connection status.
        """
        logger.info("Connecting integration '%s'", self.name)
        self.connected = True
        return {"integration": self.name, "connected": self.connected}

    def require_connection(self) -> None:
        """Raise if an action is attempted before connect() was called.

        Raises:
            RuntimeError: If the integration has not been connected.
        """
        if not self.connected:
            raise RuntimeError(f"Integration '{self.name}' is not connected yet")
