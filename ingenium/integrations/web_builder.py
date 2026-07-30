"""Web builder integration: publishing pages/landing sites."""
import logging

from .base import Integration

logger = logging.getLogger(__name__)


class WebBuilder(Integration):
    """Adapter for a website/landing-page builder."""

    name = "web_builder"

    def __init__(self) -> None:
        """Initialize the web builder adapter with an empty page registry."""
        super().__init__()
        self.pages: dict[str, dict] = {}

    def publish_page(self, slug: str, content: dict) -> dict:
        """Publish or update a page.

        Args:
            slug: URL-safe identifier for the page.
            content: Page content/config (title, sections, etc.).

        Returns:
            Dict describing the published page.
        """
        self.require_connection()
        self.pages[slug] = {"slug": slug, "content": content, "status": "published"}
        logger.info("Published page '%s'", slug)
        return dict(self.pages[slug])

    def list_pages(self) -> dict:
        """List every published page.

        Returns:
            Dict with all page slugs and their status.
        """
        self.require_connection()
        return {slug: page["status"] for slug, page in self.pages.items()}
