"""
Resolver package for the Agentic AGI robotics system.

Provides conflict resolution, error recovery, agent arbitration,
health monitoring, deadlock detection, fallback planning, and
ML-based conflict prediction.
"""

from resolver.arbitrator import AgentArbitrator
from resolver.conflict_resolution import ConflictDetector, ConflictPredictor, ConflictResolver
from resolver.deadlock_detector import DeadlockDetector
from resolver.error_recovery import ErrorRecoverySystem, ErrorSeverity
from resolver.fallback_planner import FallbackPlanner
from resolver.health_monitor import HealthMonitor
from resolver.predictor import ConflictPredictor as MLConflictPredictor

__all__ = [
    "ConflictDetector",
    "ConflictResolver",
    "ConflictPredictor",
    "MLConflictPredictor",
    "ErrorRecoverySystem",
    "ErrorSeverity",
    "AgentArbitrator",
    "HealthMonitor",
    "DeadlockDetector",
    "FallbackPlanner",
]
