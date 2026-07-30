"""Customer data: the company's living record of who it serves."""
import logging

logger = logging.getLogger(__name__)


class CustomerData:
    """In-memory store of customer/prospect records and segments."""

    def __init__(self) -> None:
        """Initialize CustomerData with an empty record set."""
        self.records: dict[str, dict] = {}

    def upsert_record(self, customer_id: str, fields: dict) -> dict:
        """Create or update a customer/prospect record.

        Args:
            customer_id: Unique identifier for the customer or lead.
            fields: Arbitrary attributes to merge into the record.

        Returns:
            Dict with the full stored record.
        """
        logger.info("Upserting customer record '%s'", customer_id)
        record = self.records.setdefault(customer_id, {"id": customer_id})
        record.update(fields)
        return {"status": "saved", "record": dict(record)}

    def segment(self, predicate: str, value: str) -> dict:
        """Return customers whose field matches a value.

        Args:
            predicate: Field name to filter on (e.g. "stage").
            value: Field value to match.

        Returns:
            Dict with the matching segment.
        """
        matches = [r for r in self.records.values() if r.get(predicate) == value]
        logger.debug("Segment %s=%s matched %d records", predicate, value, len(matches))
        return {"predicate": predicate, "value": value, "matches": matches}

    def snapshot(self) -> dict:
        """Return an aggregate view of the customer base.

        Returns:
            Dict with total record count and the records themselves.
        """
        return {"total": len(self.records), "records": list(self.records.values())}
