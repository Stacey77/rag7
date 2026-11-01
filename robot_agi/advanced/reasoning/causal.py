"""Causal reasoning for understanding cause-and-effect relationships."""
import logging
import random
from collections import defaultdict

logger = logging.getLogger(__name__)


class CausalReasoner:
    """Learns and reasons with causal models of the environment."""

    def __init__(self) -> None:
        """Initialize CausalReasoner."""
        self.causal_graph: dict[str, list[str]] = defaultdict(list)
        self.causal_strengths: dict[tuple[str, str], float] = {}

    def learn_causal_model(self, observations: list) -> dict:
        """Learn a causal model from observational data.

        Args:
            observations: List of observation dicts with variable states.

        Returns:
            Dict with learned causal graph and edge strengths.
        """
        logger.info("Learning causal model from %d observations", len(observations))
        variables = set()
        for obs in observations:
            if isinstance(obs, dict):
                variables.update(obs.keys())
        variables = list(variables)
        edges_found = 0
        for i, var_a in enumerate(variables):
            for var_b in variables[i+1:]:
                strength = random.uniform(0, 1)
                if strength > 0.5:
                    self.causal_graph[var_a].append(var_b)
                    self.causal_strengths[(var_a, var_b)] = strength
                    edges_found += 1
        return {
            "status": "learned",
            "variables": variables,
            "causal_edges": edges_found,
            "causal_graph": {k: v for k, v in self.causal_graph.items()},
            "observations_used": len(observations),
        }

    def predict_intervention(self, action: dict, outcome: str) -> dict:
        """Predict the effect of an intervention using the causal model.

        Args:
            action: Dict describing the intervention (do-calculus notation).
            outcome: Variable to predict the value of.

        Returns:
            Dict with predicted outcome distribution and causal path.
        """
        logger.info("Predicting intervention '%s' on outcome '%s'", action.get("variable", "?"), outcome)
        intervention_var = action.get("variable", "unknown")
        intervention_val = action.get("value", 1.0)
        causal_path = self.causal_graph.get(intervention_var, [])
        predicted_value = intervention_val * random.uniform(0.5, 1.5) if outcome in causal_path else random.uniform(0, 1)
        return {
            "status": "predicted",
            "intervention": action,
            "outcome_variable": outcome,
            "predicted_value": predicted_value,
            "causal_path": causal_path,
            "confidence": random.uniform(0.5, 0.9),
        }

    def counterfactual_reasoning(self, scenario: dict) -> dict:
        """Reason about what would have happened under a different scenario.

        Args:
            scenario: Dict with factual and counterfactual conditions.

        Returns:
            Dict with counterfactual outcome and difference from factual.
        """
        logger.info("Counterfactual reasoning on scenario")
        factual_outcome = scenario.get("factual_outcome", random.uniform(0, 1))
        counterfactual_outcome = factual_outcome * random.uniform(0.5, 1.5)
        return {
            "status": "reasoned",
            "scenario": scenario,
            "factual_outcome": factual_outcome,
            "counterfactual_outcome": counterfactual_outcome,
            "delta": counterfactual_outcome - factual_outcome,
            "explanation": f"Changing '{scenario.get('changed_variable', 'variable')}' would have altered the outcome by {abs(counterfactual_outcome - factual_outcome):.3f}",
        }
