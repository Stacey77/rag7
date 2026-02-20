"""
Natural language control example for the rag7 AGI Robotics Framework.

Demonstrates the NLP pipeline: command parsing, intent classification,
dialog management, and NL-driven robot control.
"""

import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.robotics_agi import RoboticsAGI
from nlp.command_parser import CommandParser
from nlp.intent_classifier import IntentClassifier
from nlp.dialog_manager import DialogManager

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")


def main() -> None:
    """Run an NLP control demo."""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
    agi = RoboticsAGI(config_path=config_path)
    dialog = DialogManager(max_history=5)
    classifier = IntentClassifier()
    parser = CommandParser()

    print("\n=== rag7 AGI – NLP Control Demo ===\n")

    commands = [
        "What is the current system status?",
        "Navigate to the loading bay",
        "Pick up the package on conveyor belt A",
        "Emergency stop!",
        "Go to the charging dock",
    ]

    robot_state = agi.get_status()

    for cmd in commands:
        print(f"Operator: {cmd}")
        intent = classifier.classify(cmd)
        parsed = parser.parse(cmd)
        response = dialog.process(cmd, robot_state)

        result = agi.execute_command(cmd)
        robot_state = agi.get_status()

        print(f"  Intent:   {intent}  (confidence: {parsed.get('confidence', '?')})")
        print(f"  Robot:    {response}")
        print(f"  Success:  {result['success']}\n")

    print("Dialog history:")
    for turn in dialog.get_history():
        print(f"  [{turn['role']}]: {turn['content']}")


if __name__ == "__main__":
    main()
