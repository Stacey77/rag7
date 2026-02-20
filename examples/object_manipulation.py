"""
Object manipulation example for the rag7 AGI Robotics Framework.

Demonstrates how to use the RoboticsAGI system to pick up and place
an object using task-level commands.
"""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.robotics_agi import RoboticsAGI
from agents.control_agent import ControlAgent

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


def main() -> None:
    """Run an object manipulation demo."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    agi = RoboticsAGI(config_path=config_path)

    print("\n=== rag7 AGI – Object Manipulation Demo ===\n")

    # Step 1: Navigate near the object
    nav_task = agi.create_task("navigate", location={"x": 2.0, "y": 1.5})
    nav_result = agi.execute_task(nav_task)
    print(f"Navigation: {nav_result}")

    # Step 2: Grasp the object
    grasp_task = agi.create_task("grasp", target_object="red_cube")
    grasp_result = agi.execute_task(grasp_task)
    print(f"Grasp: {grasp_result}")

    # Step 3: Navigate to placement location
    place_nav = agi.create_task("navigate", location={"x": 5.0, "y": 5.0})
    agi.execute_task(place_nav)

    # Step 4: Demonstrate planning for a complex task
    cmd = agi.execute_command("pick up the blue box and place it on the shelf")
    print(f"\nComplex command intent: {cmd['intent']}")
    print(f"Response: {cmd['response']}")


if __name__ == "__main__":
    main()
