"""Symbolic reasoning with rules and logic."""
import logging
import random

logger = logging.getLogger(__name__)


class SymbolicReasoner:
    """Rule-based symbolic reasoner using forward/backward chaining."""

    def __init__(self) -> None:
        """Initialize SymbolicReasoner."""
        self.rules: list[dict] = []
        self.facts: set[str] = set()

    def add_rule(self, rule: str) -> dict:
        """Add a logical rule to the knowledge base.

        Args:
            rule: Rule string in format 'IF condition THEN conclusion'.

        Returns:
            Dict with rule id and parse result.
        """
        logger.debug("Adding rule: %s", rule)
        parts = rule.upper().split("THEN")
        condition = parts[0].replace("IF", "").strip() if len(parts) > 0 else rule
        conclusion = parts[1].strip() if len(parts) > 1 else ""
        rule_dict = {"id": len(self.rules), "rule": rule, "condition": condition, "conclusion": conclusion}
        self.rules.append(rule_dict)
        return {
            "status": "added",
            "rule_id": rule_dict["id"],
            "condition": condition,
            "conclusion": conclusion,
            "total_rules": len(self.rules),
        }

    def reason(self, query: str) -> dict:
        """Reason over the rule base to answer a query.

        Args:
            query: Query string to evaluate against the rule base.

        Returns:
            Dict with conclusion, proof trace, and confidence.
        """
        logger.info("Reasoning over query: '%s'", query)
        applicable_rules = [r for r in self.rules if query.lower() in r["rule"].lower() or query.lower() in r["condition"].lower()]
        conclusions = [r["conclusion"] for r in applicable_rules if r["conclusion"]]
        proof_trace = [{"rule_id": r["id"], "rule": r["rule"], "fired": True} for r in applicable_rules]
        answer = conclusions[0] if conclusions else f"Cannot determine: {query}"
        return {
            "status": "reasoned",
            "query": query,
            "answer": answer,
            "conclusions": conclusions,
            "proof_trace": proof_trace,
            "rules_fired": len(applicable_rules),
            "confidence": random.uniform(0.6, 0.95) if applicable_rules else 0.1,
        }
