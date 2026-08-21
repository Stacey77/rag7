"""Demo entrypoint: run one full Ingenium think/connect/execute cycle."""
import json

from .samples import sample_brain


def main() -> None:
    """Populate a sample company edge and execute one objective end to end."""
    brain = sample_brain()
    report = brain.execute("Launch fall tune-up campaign")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
