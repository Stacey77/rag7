"""Demo/CLI: design a robot from a brief and emit URDF + a viewer JSON.

Usage:
    python3 -m robot_agi.design_demo "6-DOF humanoid service robot arm"
    python3 -m robot_agi.design_demo "5-DOF exoskeleton leg" --out ./out
"""
import argparse
import json
import sys
from pathlib import Path

from .design import design_robot, to_urdf


def main(argv: list[str] | None = None) -> int:
    """Run the design pipeline and print/export the results."""
    parser = argparse.ArgumentParser(prog="robot_agi.design_demo")
    parser.add_argument("goal", nargs="?", default="6-DOF humanoid service robot arm",
                        help="what to design, e.g. '6-DOF service robot arm'")
    parser.add_argument("--out", metavar="DIR", help="write design.json + robot.urdf into DIR")
    args = parser.parse_args(argv)

    result = design_robot(args.goal)
    design = result["design"]

    print(f"Brief:   {result['brief']}")
    print(f"Design:  {design.name} — {design.dof()} DOF, "
          f"{design.total_mass_kg()} kg, {design.reach_m()} m reach")
    print("Agents:")
    for name, report in result["reports"].items():
        print(f"  {name:11s} {report}")
    print(f"A2A messages exchanged: {len(result['conversation'])}")

    if args.out:
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "robot.urdf").write_text(to_urdf(design), encoding="utf-8")
        (out / "design.json").write_text(json.dumps(design.to_dict(), indent=2), encoding="utf-8")
        print(f"\nWrote {out/'robot.urdf'} and {out/'design.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
