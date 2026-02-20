"""
Simple navigation example for the rag7 AGI Robotics Framework.

Demonstrates how to use the RoboticsAGI system to navigate a robot
to a target location using a natural language command.
"""

import logging
import os
import sys

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.robotics_agi import RoboticsAGI

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


def main() -> None:
    """Run a simple navigation demo."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    agi = RoboticsAGI(config_path=config_path)

    print("\n=== rag7 AGI – Simple Navigation Demo ===\n")
    print("System status:", agi.get_status()["system"])

    # Navigate via task API
    task = agi.create_task("navigate", location={"x": 5.0, "y": 3.0})
    result = agi.execute_task(task)
    print(f"Task result: {result}")

    # Navigate via natural language command
    cmd_result = agi.execute_command("go to the charging station")
    print(f"NL command result: intent={cmd_result['intent']}, success={cmd_result['success']}")
    print(f"Robot response: {cmd_result['response']}")


if __name__ == "__main__":
    main()
