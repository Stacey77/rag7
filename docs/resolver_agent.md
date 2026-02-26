# Resolver Agent

## Overview

The **Resolver Agent** is the 6th intelligent agent in the Agentic AGI robotics system. It acts as the **System Mediator and Health Guardian**, monitoring all other agents, resolving conflicts, handling errors gracefully, and ensuring the system continues operating even when problems arise.

## Architecture

```
ResolverAgent
├── ConflictDetector      ← detects disagreements between agents
├── ConflictResolver      ← applies resolution strategies
├── ErrorRecoverySystem   ← handles errors and automatic recovery
├── AgentArbitrator       ← allocates resources and arbitrates control
├── HealthMonitor         ← tracks metrics and raises alerts
├── DeadlockDetector      ← finds and breaks deadlocks
└── FallbackPlanner       ← executes fallback strategies
```

## Responsibilities

| Responsibility        | Module                    |
|-----------------------|---------------------------|
| Conflict resolution   | `resolver/conflict_resolution.py` |
| Error recovery        | `resolver/error_recovery.py`      |
| Agent arbitration     | `resolver/arbitrator.py`          |
| Health monitoring     | `resolver/health_monitor.py`      |
| Deadlock detection    | `resolver/deadlock_detector.py`   |
| Fallback planning     | `resolver/fallback_planner.py`    |
| ML conflict prediction| `resolver/predictor.py`           |

## Quick Start

```python
from agents.resolver_agent import ResolverAgent
from agents.base_agent import BaseAgent

# Create the resolver
resolver = ResolverAgent()

# Connect to other agents
resolver.integrate_with_agents([perception, planning, control,
                                 communication, coordination])

# Start monitoring (non-blocking background thread)
resolver.start_monitoring()

# Manually resolve a conflict
conflict = {
    "type": "control",
    "agents": ["planning", "control"],
    "description": "Path disagreement",
}
resolution = resolver.resolve_conflict(conflict)

# Check system health
health = resolver.generate_health_report()

# Handle an error
error = {"type": "sensor_failure", "sensor": "camera", "severity": 2}
result = resolver.recover_from_error(error)
```

## Agent Priorities

| Agent         | Priority |
|---------------|----------|
| resolver      | 6 (highest) |
| perception    | 5 |
| planning      | 4 |
| control       | 3 |
| communication | 2 |
| coordination  | 1 (lowest) |

## Configuration

See [`config/resolver_config.yaml`](../config/resolver_config.yaml) for all configuration options.

## API Reference

### `ResolverAgent`

| Method | Description |
|--------|-------------|
| `integrate_with_agents(agents)` | Connect resolver to a list of agents |
| `start_monitoring()` | Start background monitoring loop |
| `monitor_agents()` | Run one monitoring cycle, return status dict |
| `detect_conflicts()` | Return list of active conflicts |
| `resolve_conflict(conflict)` | Resolve a conflict dict |
| `recover_from_error(error)` | Handle an error and attempt recovery |
| `arbitrate_resources(requests)` | Decide resource allocation |
| `detect_deadlock()` | Check for deadlocks (returns dict or None) |
| `break_deadlock(deadlock)` | Break a detected deadlock |
| `assess_system_health()` | Return overall system health |
| `generate_health_report()` | Return detailed health report |
| `execute_fallback(failure)` | Execute fallback strategy |
| `launch_dashboard(port=8080)` | Start the web health dashboard |

## ROS2 Integration

See [`ros2_interface/resolver_node.py`](../ros2_interface/resolver_node.py) for the ROS2 node implementation.

Launch with:
```bash
ros2 launch rag7 resolver.launch.py
```

## Testing

```bash
python -m pytest tests/ -v
```

All 87+ tests should pass.
