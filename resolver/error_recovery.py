"""
Error recovery system for the Resolver Agent.

Classifies errors by severity and type, then executes the appropriate
recovery strategy automatically.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


class ErrorSeverity(IntEnum):
    """Error severity levels, ordered from least to most severe."""
    INFO = 0      # Minor issue; log only
    WARNING = 1   # Potential problem; monitor
    ERROR = 2     # Significant issue; needs recovery
    CRITICAL = 3  # System-threatening; immediate action required
    FATAL = 4     # System shutdown required


class ErrorType:
    """Constants for recognised error types."""
    SENSOR_FAILURE = "sensor_failure"
    AGENT_CRASH = "agent_crash"
    PLANNING_FAILURE = "planning_failure"
    EXECUTION_FAILURE = "execution_failure"
    COMMUNICATION_FAILURE = "communication_failure"
    HARDWARE_FAILURE = "hardware_failure"
    UNKNOWN = "unknown"


@dataclass
class ErrorRecord:
    """Record of a detected error and its recovery attempt."""
    error_type: str
    severity: ErrorSeverity
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    recovery_attempted: bool = False
    recovery_success: Optional[bool] = None
    recovery_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "severity": self.severity.name,
            "description": self.description,
            "details": self.details,
            "timestamp": self.timestamp,
            "recovery_attempted": self.recovery_attempted,
            "recovery_success": self.recovery_success,
            "recovery_action": self.recovery_action,
        }


class ErrorRecoverySystem:
    """
    Detect, classify, and recover from errors across all robot systems.

    Supported error types:
    - Sensor failures  (camera down, lidar malfunction)
    - Agent crashes    (agent stops responding)
    - Planning failures (no valid plan found)
    - Execution failures (robot cannot reach goal)
    - Communication failures (lost connection)
    - Hardware failures (motor error, battery low)
    """

    MAX_RECOVERY_ATTEMPTS = 3

    def __init__(self):
        self._error_log: List[ErrorRecord] = []
        self._recovery_attempts: Dict[str, int] = {}
        self._recovery_handlers: Dict[str, Callable[[Dict[str, Any]], str]] = {
            ErrorType.SENSOR_FAILURE: self._recover_sensor_failure,
            ErrorType.AGENT_CRASH: self._recover_agent_crash,
            ErrorType.PLANNING_FAILURE: self._recover_planning_failure,
            ErrorType.EXECUTION_FAILURE: self._recover_execution_failure,
            ErrorType.COMMUNICATION_FAILURE: self._recover_communication_failure,
            ErrorType.HARDWARE_FAILURE: self._recover_hardware_failure,
        }

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def detect_errors(self, agent_states: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scan agent states and return a list of detected error dicts."""
        errors: List[Dict[str, Any]] = []
        now = time.time()

        for agent_name, state in agent_states.items():
            heartbeat = getattr(state, "last_heartbeat", now)
            if now - heartbeat > 30:  # No heartbeat for 30 s → agent crash
                errors.append({
                    "type": ErrorType.AGENT_CRASH,
                    "severity": ErrorSeverity.CRITICAL,
                    "agent": agent_name,
                    "description": f"Agent '{agent_name}' has not sent a heartbeat in 30s",
                })

            error_count = getattr(state, "error_count", 0)
            if error_count > 10:
                errors.append({
                    "type": ErrorType.UNKNOWN,
                    "severity": ErrorSeverity.WARNING,
                    "agent": agent_name,
                    "description": f"Agent '{agent_name}' has high error count: {error_count}",
                })
        return errors

    def classify_error(self, error: Dict[str, Any]) -> ErrorRecord:
        """Classify an error dict and return a structured ErrorRecord."""
        error_type = error.get("type", ErrorType.UNKNOWN)
        raw_severity = error.get("severity", ErrorSeverity.ERROR)
        if isinstance(raw_severity, int):
            severity = ErrorSeverity(raw_severity)
        elif isinstance(raw_severity, ErrorSeverity):
            severity = raw_severity
        else:
            severity = ErrorSeverity.ERROR

        return ErrorRecord(
            error_type=error_type,
            severity=severity,
            description=error.get("description", "No description provided"),
            details={k: v for k, v in error.items()
                     if k not in {"type", "severity", "description"}},
        )

    def execute_recovery(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the appropriate recovery strategy for an error."""
        record = self.classify_error(error)
        error_key = f"{record.error_type}:{record.details.get('agent', 'system')}"

        attempts = self._recovery_attempts.get(error_key, 0)
        if attempts >= self.MAX_RECOVERY_ATTEMPTS:
            record.recovery_attempted = True
            record.recovery_success = False
            record.recovery_action = "max_recovery_attempts_exceeded"
            self._error_log.append(record)
            logger.error("Max recovery attempts exceeded for: %s", error_key)
            return {**record.to_dict(), "escalation_required": True}

        self._recovery_attempts[error_key] = attempts + 1
        handler = self._recovery_handlers.get(record.error_type, self._recover_unknown)
        recovery_action = handler(error)

        record.recovery_attempted = True
        record.recovery_success = True
        record.recovery_action = recovery_action
        self._error_log.append(record)

        logger.info("Recovery executed for %s: %s", error_key, recovery_action)
        return record.to_dict()

    @property
    def error_log(self) -> List[Dict[str, Any]]:
        """Return the full error log as a list of dicts."""
        return [r.to_dict() for r in self._error_log]

    # ------------------------------------------------------------------ #
    # Recovery strategies
    # ------------------------------------------------------------------ #

    def _recover_sensor_failure(self, error: Dict[str, Any]) -> str:
        """Switch to backup sensors or degrade gracefully."""
        sensor = error.get("sensor", "unknown")
        logger.warning("Sensor failure detected: %s. Switching to backup sensor.", sensor)
        return f"switched_to_backup_sensor:{sensor}"

    def _recover_agent_crash(self, error: Dict[str, Any]) -> str:
        """Restart the crashed agent or redistribute its tasks."""
        agent = error.get("agent", "unknown")
        logger.warning("Agent crash detected: %s. Attempting restart.", agent)
        return f"restart_agent:{agent}"

    def _recover_planning_failure(self, error: Dict[str, Any]) -> str:
        """Try an alternative planning method."""
        logger.warning("Planning failure detected. Switching to alternative planner.")
        return "alternative_planning_method"

    def _recover_execution_failure(self, error: Dict[str, Any]) -> str:
        """Re-plan or find an alternative path."""
        logger.warning("Execution failure detected. Triggering re-planning.")
        return "replan_trajectory"

    def _recover_communication_failure(self, error: Dict[str, Any]) -> str:
        """Use cached data or enter fail-safe mode."""
        logger.warning("Communication failure detected. Using cached data.")
        return "use_cached_data_failsafe"

    def _recover_hardware_failure(self, error: Dict[str, Any]) -> str:
        """Execute emergency stop or enter limp mode."""
        logger.warning("Hardware failure detected. Executing emergency stop.")
        return "emergency_stop_limp_mode"

    def _recover_unknown(self, error: Dict[str, Any]) -> str:
        """Generic recovery for unknown error types."""
        logger.warning("Unknown error type. Applying generic recovery.")
        return "generic_recovery"
