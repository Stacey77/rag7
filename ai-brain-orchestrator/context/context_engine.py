"""Context Engine – builds, enriches, and compresses situational context.

The context engine assembles a structured context object from raw data feeds,
enriches it with derived features, and compresses it to a configurable token
budget for downstream consumption by LLM or rule-based components.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from shared.common.logger import get_logger

log = get_logger(__name__, service="ai-brain-orchestrator")


@dataclass
class Context:
    """A structured context snapshot.

    Attributes:
        raw: Original input data dict.
        enriched: Raw data extended with derived features.
        compressed: Reduced representation within the token budget.
        token_count: Estimated token count of the compressed context.
        metadata: Arbitrary supporting data.
    """

    raw: dict[str, Any] = field(default_factory=dict)
    enriched: dict[str, Any] = field(default_factory=dict)
    compressed: dict[str, Any] = field(default_factory=dict)
    token_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ContextEngine:
    """Builds, enriches, and compresses situational context for AI models.

    Attributes:
        _token_budget: Maximum context size (notional token count).
        _enrichers: Registered enrichment callables.
    """

    def __init__(self, token_budget: int = 4096) -> None:
        """Initialise the context engine.

        Args:
            token_budget: Maximum number of tokens for the compressed context.
                Defaults to 4096.
        """
        self._token_budget = token_budget
        self._enrichers: list[Any] = []
        log.info("ContextEngine initialised", token_budget=token_budget)

    def build_context(self, data: dict[str, Any]) -> Context:
        """Construct a raw :class:`Context` from input data.

        Args:
            data: Raw input dict (e.g. market snapshot, agent state).

        Returns:
            A :class:`Context` with ``raw`` populated and ``enriched`` /
            ``compressed`` set to copies of the raw data.

        Raises:
            TypeError: If *data* is not a dict.
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data).__name__}")

        ctx = Context(raw=copy.deepcopy(data))
        ctx.enriched = copy.deepcopy(data)
        ctx.compressed = copy.deepcopy(data)
        ctx.token_count = self._estimate_tokens(ctx.compressed)
        log.debug("Context built", keys=list(data.keys()), token_count=ctx.token_count)
        return ctx

    def enrich(self, ctx: Context, extra: dict[str, Any]) -> Context:
        """Merge *extra* derived features into the context's enriched layer.

        Args:
            ctx: The :class:`Context` to enrich in-place.
            extra: Key-value pairs to add to the enriched representation.

        Returns:
            The mutated :class:`Context` (same object, mutated in-place).
        """
        ctx.enriched.update(extra)
        ctx.token_count = self._estimate_tokens(ctx.enriched)
        log.debug("Context enriched", added_keys=list(extra.keys()))
        return ctx

    def compress(self, ctx: Context, priority_keys: list[str] | None = None) -> Context:
        """Reduce the context to fit within the configured token budget.

        Keys listed in *priority_keys* are retained first; remaining keys are
        added in insertion order until the budget is exhausted.

        Args:
            ctx: The :class:`Context` to compress in-place.
            priority_keys: Keys that must be retained even if the budget is
                tight.

        Returns:
            The mutated :class:`Context` with ``compressed`` updated.
        """
        source = ctx.enriched
        ordered_keys = list(priority_keys or []) + [
            k for k in source if k not in (priority_keys or [])
        ]

        compressed: dict[str, Any] = {}
        used_tokens = 0
        for key in ordered_keys:
            if key not in source:
                continue
            entry_tokens = self._estimate_tokens({key: source[key]})
            if used_tokens + entry_tokens > self._token_budget:
                log.debug("Token budget reached", key=key, used=used_tokens)
                break
            compressed[key] = source[key]
            used_tokens += entry_tokens

        ctx.compressed = compressed
        ctx.token_count = used_tokens
        log.debug("Context compressed", keys_kept=len(compressed), tokens=used_tokens)
        return ctx

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_tokens(data: dict[str, Any]) -> int:
        """Rough token estimate: ~4 characters per token.

        Args:
            data: Dict whose string representation is measured.

        Returns:
            Estimated integer token count.
        """
        return max(1, len(str(data)) // 4)
