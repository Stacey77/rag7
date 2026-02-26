"""
Tests for the error recovery system.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from resolver.error_recovery import ErrorRecoverySystem, ErrorSeverity, ErrorType, ErrorRecord
from agents.base_agent import AgentState


class TestErrorSeverity(unittest.TestCase):
    def test_ordering(self):
        self.assertLess(ErrorSeverity.INFO, ErrorSeverity.WARNING)
        self.assertLess(ErrorSeverity.WARNING, ErrorSeverity.ERROR)
        self.assertLess(ErrorSeverity.ERROR, ErrorSeverity.CRITICAL)
        self.assertLess(ErrorSeverity.CRITICAL, ErrorSeverity.FATAL)


class TestErrorRecoverySystem(unittest.TestCase):
    def setUp(self):
        self.system = ErrorRecoverySystem()

    def test_classify_sensor_failure(self):
        error = {
            "type": ErrorType.SENSOR_FAILURE,
            "severity": ErrorSeverity.ERROR,
            "sensor": "camera",
            "description": "Camera offline",
        }
        record = self.system.classify_error(error)
        self.assertIsInstance(record, ErrorRecord)
        self.assertEqual(record.error_type, ErrorType.SENSOR_FAILURE)
        self.assertEqual(record.severity, ErrorSeverity.ERROR)

    def test_classify_default_severity(self):
        record = self.system.classify_error({"type": "sensor_failure"})
        self.assertEqual(record.severity, ErrorSeverity.ERROR)

    def test_execute_recovery_sensor(self):
        error = {"type": ErrorType.SENSOR_FAILURE, "sensor": "lidar"}
        result = self.system.execute_recovery(error)
        self.assertIn("recovery_action", result)
        self.assertIn("lidar", result["recovery_action"])
        self.assertTrue(result["recovery_success"])

    def test_execute_recovery_agent_crash(self):
        error = {"type": ErrorType.AGENT_CRASH, "agent": "planning"}
        result = self.system.execute_recovery(error)
        self.assertIn("planning", result["recovery_action"])

    def test_execute_recovery_planning_failure(self):
        error = {"type": ErrorType.PLANNING_FAILURE}
        result = self.system.execute_recovery(error)
        self.assertTrue(result["recovery_success"])

    def test_execute_recovery_execution_failure(self):
        error = {"type": ErrorType.EXECUTION_FAILURE}
        result = self.system.execute_recovery(error)
        self.assertIn("replan", result["recovery_action"])

    def test_execute_recovery_communication_failure(self):
        error = {"type": ErrorType.COMMUNICATION_FAILURE}
        result = self.system.execute_recovery(error)
        self.assertIn("cached", result["recovery_action"])

    def test_execute_recovery_hardware_failure(self):
        error = {"type": ErrorType.HARDWARE_FAILURE}
        result = self.system.execute_recovery(error)
        self.assertIn("emergency", result["recovery_action"])

    def test_execute_recovery_unknown_type(self):
        error = {"type": "totally_unknown"}
        result = self.system.execute_recovery(error)
        self.assertTrue(result["recovery_success"])

    def test_max_recovery_attempts(self):
        error = {"type": ErrorType.AGENT_CRASH, "agent": "perception"}
        for _ in range(ErrorRecoverySystem.MAX_RECOVERY_ATTEMPTS):
            self.system.execute_recovery(error)
        # One more should trigger escalation
        result = self.system.execute_recovery(error)
        self.assertFalse(result["recovery_success"])
        self.assertTrue(result.get("escalation_required"))

    def test_error_log_grows(self):
        self.system.execute_recovery({"type": ErrorType.SENSOR_FAILURE})
        self.system.execute_recovery({"type": ErrorType.PLANNING_FAILURE})
        self.assertEqual(len(self.system.error_log), 2)

    def test_detect_errors_heartbeat_timeout(self):
        import time
        state = AgentState(name="planning")
        state.last_heartbeat = time.time() - 60  # 60 seconds ago
        errors = self.system.detect_errors({"planning": state})
        self.assertTrue(any(e["type"] == ErrorType.AGENT_CRASH for e in errors))

    def test_detect_errors_high_error_count(self):
        state = AgentState(name="control")
        state.error_count = 15
        errors = self.system.detect_errors({"control": state})
        self.assertTrue(len(errors) > 0)


if __name__ == "__main__":
    unittest.main()
