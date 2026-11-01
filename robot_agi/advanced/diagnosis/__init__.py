"""Diagnosis and self-repair module for robotics AGI."""
from .self_diagnostics import SelfDiagnostics
from .self_repair import SelfRepair
from .anomaly_detection import AnomalyDetector
from .predictive_maintenance import PredictiveMaintenance

__all__ = ["SelfDiagnostics", "SelfRepair", "AnomalyDetector", "PredictiveMaintenance"]
