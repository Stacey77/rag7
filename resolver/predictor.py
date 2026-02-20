"""
ML-based conflict predictor for the Resolver Agent.

Uses a lightweight PyTorch neural network to predict conflict probabilities
from agent state feature vectors. Falls back gracefully when PyTorch is
unavailable so the rest of the system continues to operate.
"""

import logging
import time
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)

# Try importing PyTorch; fail gracefully if it is not installed
try:
    import torch
    import torch.nn as nn

    _TORCH_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TORCH_AVAILABLE = False
    logger.warning("PyTorch not available; ML conflict prediction will use heuristics only")


# ---------------------------------------------------------------------------
# Neural network model definition
# ---------------------------------------------------------------------------

if _TORCH_AVAILABLE:

    class _ConflictPredictorNet(nn.Module):
        """Simple feed-forward network for binary conflict prediction."""

        def __init__(self, input_dim: int = 20, hidden_dim: int = 64):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_dim, hidden_dim // 2),
                nn.ReLU(),
                nn.Linear(hidden_dim // 2, 1),
                nn.Sigmoid(),
            )

        def forward(self, x: "torch.Tensor") -> "torch.Tensor":  # noqa: F821
            return self.network(x)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class ConflictPredictor:
    """
    Predict conflicts before they happen.

    If PyTorch is available, a neural network model is trained on historical
    data.  Otherwise, a simple heuristic-based fallback is used.
    """

    INPUT_DIM = 20   # feature vector length per prediction call
    HIDDEN_DIM = 64

    def __init__(self):
        self._model: Optional[Any] = None
        self._trained = False
        self._history: List[Dict[str, Any]] = []

        if _TORCH_AVAILABLE:
            self._model = _ConflictPredictorNet(self.INPUT_DIM, self.HIDDEN_DIM)
            logger.info("ConflictPredictor: PyTorch model initialised")

    # ------------------------------------------------------------------ #
    # Training
    # ------------------------------------------------------------------ #

    def train_predictor(self, historical_conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Train the predictor on a list of historical conflict records."""
        if not _TORCH_AVAILABLE or not historical_conflicts:
            logger.warning("Training skipped: PyTorch unavailable or no data provided")
            return {"trained": False, "reason": "no_data_or_no_torch"}

        import torch  # pylint: disable=import-outside-toplevel
        import torch.nn as nn  # pylint: disable=import-outside-toplevel

        features, labels = self._extract_features(historical_conflicts)
        X = torch.tensor(features, dtype=torch.float32)
        y = torch.tensor(labels, dtype=torch.float32).unsqueeze(1)

        optimizer = torch.optim.Adam(self._model.parameters(), lr=1e-3)
        criterion = nn.BCELoss()

        epochs = 50
        for _ in range(epochs):
            self._model.train()
            optimizer.zero_grad()
            output = self._model(X)
            loss = criterion(output, y)
            loss.backward()
            optimizer.step()

        self._trained = True
        logger.info("ConflictPredictor: model trained on %d records", len(historical_conflicts))
        return {"trained": True, "samples": len(historical_conflicts), "epochs": epochs}

    # ------------------------------------------------------------------ #
    # Inference
    # ------------------------------------------------------------------ #

    def predict_conflict_probability(
        self, agent_states: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict the probability of a conflict given current agent states."""
        feature_vector = self._states_to_features(agent_states)

        if _TORCH_AVAILABLE and self._trained and self._model is not None:
            import torch  # pylint: disable=import-outside-toplevel

            self._model.eval()
            with torch.no_grad():
                x = torch.tensor(feature_vector, dtype=torch.float32).unsqueeze(0)
                probability = float(self._model(x).item())
        else:
            # Heuristic fallback: high error counts or resource contention raise probability
            probability = self._heuristic_probability(agent_states)

        result = {
            "probability": probability,
            "threshold": 0.5,
            "likely_conflict": probability >= 0.5,
            "timestamp": time.time(),
        }
        self._history.append(result)
        return result

    def predict_best_resolution(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """Use the model to suggest the best resolution (heuristic if no model)."""
        agents = conflict.get("agents", [])
        from resolver.arbitrator import AgentArbitrator  # pylint: disable=import-outside-toplevel
        priorities = AgentArbitrator.DEFAULT_PRIORITIES
        if not agents:
            return {"winning_agent": None, "action": "no_resolution"}
        winner = max(agents, key=lambda a: priorities.get(a, 0))
        return {
            "winning_agent": winner,
            "action": f"grant_to_{winner}",
            "confidence": 0.75,
        }

    def suggest_preventive_actions(
        self, agent_states: Dict[str, Any]
    ) -> List[str]:
        """Suggest actions to prevent predicted conflicts."""
        prediction = self.predict_conflict_probability(agent_states)
        actions: List[str] = []
        if prediction["likely_conflict"]:
            actions.append("pre_allocate_contested_resources")
            actions.append("notify_agents_of_potential_conflict")
            actions.append("increase_monitoring_frequency")
        return actions

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _states_to_features(self, agent_states: Dict[str, Any]) -> List[float]:
        """Convert agent states to a fixed-length feature vector."""
        features: List[float] = []
        ordered_agents = ["perception", "planning", "control", "communication", "coordination"]
        for agent_name in ordered_agents:
            state = agent_states.get(agent_name)
            if state is not None:
                features.extend([
                    float(getattr(state, "cpu_usage", 0.0)) / 100.0,
                    float(getattr(state, "memory_usage", 0.0)) / 100.0,
                    float(getattr(state, "error_count", 0)) / 100.0,
                    float(getattr(state, "response_time", 0.0)),
                ])
            else:
                features.extend([0.0, 0.0, 0.0, 0.0])
        # Pad / truncate to INPUT_DIM
        features = (features + [0.0] * self.INPUT_DIM)[: self.INPUT_DIM]
        return features

    def _extract_features(
        self, records: List[Dict[str, Any]]
    ):
        """Extract (feature_matrix, label_vector) from historical records."""
        features = []
        labels = []
        for record in records:
            # Feature: encode conflict severity and agent count
            severity = float(record.get("severity", 1))
            agent_count = float(len(record.get("agents", [])))
            vec = [severity / 5.0, agent_count / 6.0] + [0.0] * (self.INPUT_DIM - 2)
            features.append(vec[: self.INPUT_DIM])
            labels.append(1.0 if record.get("conflict_occurred", True) else 0.0)
        return features, labels

    def _heuristic_probability(self, agent_states: Dict[str, Any]) -> float:
        """Simple heuristic fallback for conflict probability estimation."""
        score = 0.0
        for state in agent_states.values():
            if getattr(state, "error_count", 0) > 5:
                score += 0.2
            resources = getattr(state, "metadata", {}).get("requested_resources", [])
            score += len(resources) * 0.05
        return min(score, 0.99)
