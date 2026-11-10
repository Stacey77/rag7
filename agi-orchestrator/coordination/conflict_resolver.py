"""Conflict Resolver – inter-system conflict detection and resolution.

When multiple sub-systems issue contradictory directives (e.g. one agent
wants to buy while another wants to sell the same asset), the resolver
detects the conflict, applies an arbitration policy, and returns a
resolved directive.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="agi-orchestrator")


class ConflictType(Enum):
    """Classification of detected conflicts."""

    DIRECTIONAL = auto()    # Opposing buy/sell signals.
    RESOURCE = auto()       # Over-subscription of a shared resource.
    PRIORITY = auto()       # Competing goals at the same priority level.
    TEMPORAL = auto()       # Time-window overlaps in scheduled actions.
    UNKNOWN = auto()


@dataclass
class Conflict:
    """A detected inter-system conflict.

    Attributes:
        conflict_id: Unique identifier, auto-generated.
        conflict_type: Classification of the conflict.
        parties: List of agent/system IDs involved.
        directives: The contradictory directives that caused the conflict.
        severity: Numeric severity in ``[0.0, 1.0]``.
        resolved: Whether a resolution has been applied.
        resolution: The chosen resolution directive (populated by :meth:`resolve`).
    """

    conflict_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conflict_type: ConflictType = ConflictType.UNKNOWN
    parties: list[str] = field(default_factory=list)
    directives: list[dict[str, Any]] = field(default_factory=list)
    severity: float = 0.5
    resolved: bool = False
    resolution: dict[str, Any] = field(default_factory=dict)


class ConflictResolver:
    """Detects, resolves, and arbitrates inter-system conflicts.

    Attributes:
        _conflicts: History of all detected conflicts keyed by ``conflict_id``.
        _arbitration_policy: Strategy used when automatic resolution fails.
    """

    def __init__(self, arbitration_policy: str = "priority") -> None:
        """Initialise the resolver with an arbitration policy.

        Args:
            arbitration_policy: Strategy for tie-breaking. Supported values:
                ``"priority"`` (higher-priority directive wins) and
                ``"conservative"`` (least-aggressive directive wins).
        """
        if arbitration_policy not in {"priority", "conservative"}:
            raise ValueError(
                f"Unknown arbitration_policy '{arbitration_policy}'. "
                "Choose 'priority' or 'conservative'."
            )
        self._conflicts: dict[str, Conflict] = {}
        self._arbitration_policy = arbitration_policy
        log.info("ConflictResolver initialised", policy=arbitration_policy)

    def detect_conflict(self, directives: list[dict[str, Any]]) -> Conflict | None:
        """Analyse a set of directives and return a :class:`Conflict` if found.

        A directional conflict is detected when two directives target the same
        asset with opposing actions (``"buy"`` vs ``"sell"``).

        Args:
            directives: List of directive dicts, each containing at minimum
                ``action`` and optionally ``asset`` and ``agent_id`` keys.

        Returns:
            A new :class:`Conflict` if one is found, otherwise *None*.
        """
        if len(directives) < 2:
            return None

        # Build action map per asset.
        asset_actions: dict[str, list[dict[str, Any]]] = {}
        for d in directives:
            asset = d.get("asset", "global")
            asset_actions.setdefault(asset, []).append(d)

        for asset, asset_directives in asset_actions.items():
            actions = {d.get("action", "").lower() for d in asset_directives}
            if "buy" in actions and "sell" in actions:
                parties = [d.get("agent_id", "unknown") for d in asset_directives]
                conflict = Conflict(
                    conflict_type=ConflictType.DIRECTIONAL,
                    parties=parties,
                    directives=asset_directives,
                    severity=0.8,
                )
                self._conflicts[conflict.conflict_id] = conflict
                log.warning(
                    "Conflict detected",
                    conflict_id=conflict.conflict_id,
                    conflict_type=conflict.conflict_type.name,
                    asset=asset,
                    parties=parties,
                )
                return conflict

        return None

    def resolve(self, conflict: Conflict) -> dict[str, Any]:
        """Apply automatic resolution logic to a detected conflict.

        Args:
            conflict: The :class:`Conflict` to resolve.

        Returns:
            The chosen resolution directive dict.
        """
        if conflict.resolved:
            log.debug("Conflict already resolved", conflict_id=conflict.conflict_id)
            return conflict.resolution

        resolution = self.arbitrate(conflict)
        conflict.resolution = resolution
        conflict.resolved = True
        log.info(
            "Conflict resolved",
            conflict_id=conflict.conflict_id,
            resolution_action=resolution.get("action"),
        )
        return resolution

    def arbitrate(self, conflict: Conflict) -> dict[str, Any]:
        """Apply the configured arbitration policy to select a winning directive.

        Args:
            conflict: The :class:`Conflict` being arbitrated.

        Returns:
            The winning directive dict according to the policy.
        """
        if not conflict.directives:
            return {"action": "hold", "reason": "no directives to arbitrate"}

        if self._arbitration_policy == "priority":
            # Directive with the highest ``priority`` value wins.
            winner = max(
                conflict.directives,
                key=lambda d: float(d.get("priority", 0.0)),
            )
        else:  # conservative
            # Directive with the least-aggressive action wins (hold > buy > sell).
            aggression = {"hold": 0, "buy": 1, "sell": 1, "short": 2}
            winner = min(
                conflict.directives,
                key=lambda d: aggression.get(d.get("action", "hold").lower(), 99),
            )

        log.info(
            "Arbitration complete",
            policy=self._arbitration_policy,
            winning_action=winner.get("action"),
        )
        return dict(winner)
