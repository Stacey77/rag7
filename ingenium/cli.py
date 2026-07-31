"""Command-line interface for Ingenium.

Examples:
    python3 -m ingenium run "Launch fall tune-up campaign" --demo
    python3 -m ingenium run "Follow-up" --state state.json
    python3 -m ingenium show --state state.json
    python3 -m ingenium serve --port 8000
    python3 -m ingenium demo
"""
import argparse
import json
import sys
from pathlib import Path

from .core.brain import Ingenium
from .samples import sample_brain


def _load_brain(state_path: str | None, demo: bool) -> Ingenium:
    """Build the brain a command should act on.

    Args:
        state_path: Optional path to a saved state file; loaded if it exists.
        demo: If True, seed the shared sample edge (only on a fresh brain).

    Returns:
        An Ingenium instance, restored from state and/or seeded as requested.
    """
    if state_path and Path(state_path).is_file():
        brain = Ingenium.load(state_path)
        if demo:
            print("note: --demo ignored because --state file already exists", file=sys.stderr)
        return brain
    return sample_brain() if demo else Ingenium()


def _summarize(report: dict) -> str:
    """Render a one-glance human summary of an execute() report."""
    p = report["pipeline"]
    lines = [
        f"objective:      {report['objective']}",
        f"reached:        {len(p['outreach']['sent'])} customer(s)",
        f"published:      {p['create']['asset']['slug']}",
        f"follow-ups:     {len(p['follow_up']['scheduled'])} scheduled",
        f"recommendation: {p['optimize']['recommendation']}",
    ]
    return "\n".join(lines)


def _cmd_run(args: argparse.Namespace) -> int:
    brain = _load_brain(args.state, args.demo)
    report = brain.execute(args.objective)
    if args.state:
        brain.save(args.state)
    print(json.dumps(report, indent=2) if args.json else _summarize(report))
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    if not args.state or not Path(args.state).is_file():
        print(f"no state file at {args.state!r}", file=sys.stderr)
        return 1
    brain = Ingenium.load(args.state)
    if args.json:
        print(json.dumps(brain.state(), indent=2))
        return 0
    print("company edge:")
    print(json.dumps(brain.company_intelligence.snapshot(), indent=2))
    print(f"\nrun history: {len(brain.history)} run(s)")
    for i, r in enumerate(brain.history, 1):
        rec = r["pipeline"]["optimize"]["recommendation"]
        print(f"  {i}. {r['objective']} -> {rec}")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    from .web.server import run as serve  # local import: only needed for this command
    serve(host=args.host, port=args.port)
    return 0


def _cmd_demo(args: argparse.Namespace) -> int:
    from .demo import main as demo_main
    demo_main()
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser for the Ingenium CLI."""
    parser = argparse.ArgumentParser(prog="ingenium", description="Run the Ingenium loop from the command line.")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="execute an objective through the full pipeline")
    run.add_argument("objective", help="the objective to execute, e.g. 'Launch fall tune-up campaign'")
    run.add_argument("--state", metavar="PATH", help="load state from PATH if it exists, and save back to it after")
    run.add_argument("--demo", action="store_true", help="seed the sample company edge (fresh brain only)")
    run.add_argument("--json", action="store_true", help="print the full JSON report instead of a summary")
    run.set_defaults(func=_cmd_run)

    show = sub.add_parser("show", help="print the company edge and run history from a state file")
    show.add_argument("--state", metavar="PATH", required=True, help="path to a saved state file")
    show.add_argument("--json", action="store_true", help="print the raw state JSON")
    show.set_defaults(func=_cmd_show)

    serve = sub.add_parser("serve", help="start the web dashboard")
    serve.add_argument("--host", default="0.0.0.0", help="interface to bind (default: 0.0.0.0)")
    serve.add_argument("--port", type=int, default=8000, help="port to listen on (default: 8000)")
    serve.set_defaults(func=_cmd_serve)

    demo = sub.add_parser("demo", help="run one sample cycle and print the JSON report")
    demo.set_defaults(func=_cmd_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the Ingenium CLI.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Process exit code.
    """
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
