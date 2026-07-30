"""Finance integration: revenue and cost metrics."""
import logging

from .base import Integration

logger = logging.getLogger(__name__)


class Finance(Integration):
    """Adapter for a finance/accounting system."""

    name = "finance"

    def __init__(self) -> None:
        """Initialize the finance adapter with no metrics recorded."""
        super().__init__()
        self.metrics: dict[str, float] = {}

    def record_metric(self, name: str, value: float) -> dict:
        """Record or update a financial metric.

        Args:
            name: Metric label (e.g. "mrr", "cac").
            value: Numeric value of the metric.

        Returns:
            Dict with all current metrics.
        """
        self.require_connection()
        self.metrics[name] = value
        logger.info("Recorded finance metric '%s' = %s", name, value)
        return dict(self.metrics)

    def get_snapshot(self) -> dict:
        """Return every recorded metric.

        Returns:
            Dict of metric name to value.
        """
        self.require_connection()
        return dict(self.metrics)
