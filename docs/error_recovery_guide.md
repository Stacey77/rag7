# Error Recovery Guide

## Overview

The error recovery system automatically detects, classifies, and recovers from errors across all robot systems.

## Error Severity Levels

| Level    | Value | Meaning |
|----------|-------|---------|
| INFO     | 0     | Minor issue; log only |
| WARNING  | 1     | Potential problem; monitor |
| ERROR    | 2     | Significant issue; needs recovery |
| CRITICAL | 3     | System-threatening; immediate action |
| FATAL    | 4     | System shutdown required |

## Supported Error Types

| Type                   | Trigger                        | Recovery Action |
|------------------------|-------------------------------|-----------------|
| `sensor_failure`       | Camera/LIDAR offline          | Switch to backup sensor |
| `agent_crash`          | Agent stops responding (30s)  | Restart agent |
| `planning_failure`     | No valid plan found           | Try alternative planner |
| `execution_failure`    | Robot cannot reach goal       | Re-plan trajectory |
| `communication_failure`| Connection lost               | Use cached data / fail-safe |
| `hardware_failure`     | Motor error / battery low     | Emergency stop / limp mode |

## Usage

```python
from resolver.error_recovery import ErrorRecoverySystem, ErrorSeverity, ErrorType

system = ErrorRecoverySystem()

# Recover from an error
error = {
    "type": ErrorType.SENSOR_FAILURE,
    "sensor": "camera",
    "severity": ErrorSeverity.ERROR,
}
result = system.execute_recovery(error)
# result["recovery_action"] → "switched_to_backup_sensor:camera"
# result["recovery_success"] → True
```

## Escalation

After `MAX_RECOVERY_ATTEMPTS` (default: 3) failed attempts for the same error, the system escalates:

```python
result["escalation_required"] = True  # Human intervention needed
```

## Integration with Resolver Agent

```python
resolver = ResolverAgent()
resolver.recover_from_error({
    "type": "agent_crash",
    "agent": "planning",
    "severity": 3,
})
```

## Error Log

```python
print(system.error_log)  # List of all ErrorRecord dicts
```

## Detection

The system can auto-detect errors by scanning agent states:

```python
errors = system.detect_errors(agent_states)
# Returns list of error dicts for agents with:
# - No heartbeat for >30 seconds (agent_crash)
# - Error count >10 (unknown)
```
