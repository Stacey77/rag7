"""A shared sample company edge used by the demo, web GUI, and CLI."""
from .core.brain import Ingenium


def sample_brain() -> Ingenium:
    """Construct an Ingenium pre-populated with a sample company edge.

    Returns:
        An Ingenium instance ready to execute objectives against out of the box.
    """
    brain = Ingenium()
    ci = brain.company_intelligence
    ci.strategy.set_positioning("AI ops partner for local service businesses")
    ci.strategy.add_priority("book more jobs", rank=1)
    ci.customer_data.upsert_record("cust-1", {"email": "lead@example.com", "stage": "new"})
    ci.goals.set_goal("Q3 new clients", target=10, current=3)
    ci.knowledge.add("offers", "Fall tune-up special: $99")
    ci.brand.set_voice("direct, confident, no fluff", ["clear", "bold"])
    return brain
