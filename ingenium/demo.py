"""Demo entrypoint: run one full Ingenium think/connect/execute cycle."""
import json

from ingenium import Ingenium


def main() -> None:
    """Populate a sample company edge and execute one objective end to end."""
    brain = Ingenium()
    ci = brain.company_intelligence
    ci.strategy.set_positioning("AI ops partner for local service businesses")
    ci.strategy.add_priority("book more jobs", rank=1)
    ci.customer_data.upsert_record("cust-1", {"email": "lead@example.com", "stage": "new"})
    ci.goals.set_goal("Q3 new clients", target=10, current=3)
    ci.knowledge.add("offers", "Fall tune-up special: $99")
    ci.brand.set_voice("direct, confident, no fluff", ["clear", "bold"])

    report = brain.execute("Launch fall tune-up campaign")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
