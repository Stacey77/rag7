"""
Error Recovery Demo

Demonstrates the Resolver Agent's error detection and automatic
recovery capabilities for various error types.
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from resolver.error_recovery import ErrorRecoverySystem, ErrorSeverity, ErrorType


def demo_error_classification():
    print("\n=== Error Classification ===")
    system = ErrorRecoverySystem()
    errors = [
        {"type": ErrorType.SENSOR_FAILURE, "sensor": "camera", "severity": ErrorSeverity.ERROR},
        {"type": ErrorType.AGENT_CRASH, "agent": "planning", "severity": ErrorSeverity.CRITICAL},
        {"type": ErrorType.PLANNING_FAILURE, "severity": ErrorSeverity.ERROR},
        {"type": ErrorType.HARDWARE_FAILURE, "component": "motor", "severity": ErrorSeverity.CRITICAL},
    ]
    for error in errors:
        record = system.classify_error(error)
        print(f"  {record.error_type:30s} → severity: {record.severity.name}")


def demo_automatic_recovery():
    print("\n=== Automatic Error Recovery ===")
    system = ErrorRecoverySystem()
    scenarios = [
        {
            "name": "Camera failure during navigation",
            "error": {"type": ErrorType.SENSOR_FAILURE, "sensor": "camera",
                      "severity": ErrorSeverity.ERROR},
        },
        {
            "name": "Planning agent becomes unresponsive",
            "error": {"type": ErrorType.AGENT_CRASH, "agent": "planning",
                      "severity": ErrorSeverity.CRITICAL},
        },
        {
            "name": "Robot cannot reach goal",
            "error": {"type": ErrorType.EXECUTION_FAILURE,
                      "severity": ErrorSeverity.ERROR},
        },
        {
            "name": "Communication link lost",
            "error": {"type": ErrorType.COMMUNICATION_FAILURE,
                      "severity": ErrorSeverity.WARNING},
        },
        {
            "name": "Motor controller error",
            "error": {"type": ErrorType.HARDWARE_FAILURE, "component": "motor",
                      "severity": ErrorSeverity.CRITICAL},
        },
    ]

    for scenario in scenarios:
        print(f"\n  Scenario: {scenario['name']}")
        result = system.execute_recovery(scenario["error"])
        print(f"    Action:  {result['recovery_action']}")
        print(f"    Success: {result['recovery_success']}")


def demo_escalation():
    print("\n=== Recovery Escalation (max attempts exceeded) ===")
    system = ErrorRecoverySystem()
    error = {"type": ErrorType.SENSOR_FAILURE, "sensor": "lidar"}

    for attempt in range(ErrorRecoverySystem.MAX_RECOVERY_ATTEMPTS + 1):
        result = system.execute_recovery(error)
        if result.get("escalation_required"):
            print(f"  Attempt {attempt + 1}: ESCALATED – human intervention required")
        else:
            print(f"  Attempt {attempt + 1}: Recovery action → {result['recovery_action']}")


if __name__ == "__main__":
    demo_error_classification()
    demo_automatic_recovery()
    demo_escalation()
    print("\nDemo completed successfully!")
