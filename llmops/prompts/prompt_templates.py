"""Reusable prompt templates for trading platform LLM tasks."""

from __future__ import annotations

from dataclasses import dataclass, field
from string import Template
from typing import Any

from loguru import logger


@dataclass
class PromptTemplate:
    """A named, parameterised prompt template.

    Attributes:
        name: Unique template identifier.
        template: Template string using ``$variable`` or ``${variable}`` syntax.
        required_vars: Variable names that must be provided at render time.
        description: Human-readable description of the template's purpose.
        version: Semantic version string.
    """

    name: str
    template: str
    required_vars: list[str] = field(default_factory=list)
    description: str = ""
    version: str = "1.0.0"

    def render(self, **kwargs: Any) -> str:
        """Render the template with the provided variables.

        Args:
            **kwargs: Variable values to substitute.

        Returns:
            Fully rendered prompt string.

        Raises:
            ValueError: If any required variable is missing.
            KeyError: If the template references an undefined variable.
        """
        missing = [v for v in self.required_vars if v not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables for template '{self.name}': {missing}")
        try:
            return Template(self.template).substitute(**kwargs)
        except KeyError as exc:
            raise KeyError(
                f"Template '{self.name}' references undefined variable: {exc}"
            ) from exc


# ---------------------------------------------------------------------------
# Built-in trading platform templates
# ---------------------------------------------------------------------------

_MARKET_ANALYSIS_TEMPLATE = PromptTemplate(
    name="market_analysis",
    template=(
        "You are an expert quantitative analyst. Analyse the following market data "
        "and provide a structured assessment.\n\n"
        "Symbol: $symbol\n"
        "Timeframe: $timeframe\n"
        "Current Price: $current_price\n"
        "24h Change: $price_change_pct%\n"
        "Volume: $volume\n"
        "Recent News: $news_summary\n\n"
        "Provide:\n"
        "1. Trend direction (bullish/bearish/neutral)\n"
        "2. Key support and resistance levels\n"
        "3. Momentum indicators summary\n"
        "4. Short-term outlook (24–72 hours)\n"
        "5. Confidence level (0–100)"
    ),
    required_vars=[
        "symbol",
        "timeframe",
        "current_price",
        "price_change_pct",
        "volume",
        "news_summary",
    ],
    description="Comprehensive market analysis for a single instrument.",
    version="1.0.0",
)

_TRADE_DECISION_TEMPLATE = PromptTemplate(
    name="trade_decision",
    template=(
        "You are a disciplined algorithmic trading system. Based on the following "
        "context, recommend a trade decision.\n\n"
        "Portfolio State:\n$portfolio_summary\n\n"
        "Market Signal:\n$market_signal\n\n"
        "Risk Parameters:\n"
        "  Max Position Size: $max_position_size\n"
        "  Max Drawdown: $max_drawdown_pct%\n"
        "  Risk/Reward Ratio: $risk_reward_ratio\n\n"
        "Respond with:\n"
        "ACTION: [BUY|SELL|HOLD]\n"
        "SIZE: [position size as % of portfolio]\n"
        "ENTRY: [entry price or MARKET]\n"
        "STOP_LOSS: [stop-loss price]\n"
        "TAKE_PROFIT: [take-profit price]\n"
        "RATIONALE: [one-sentence justification]"
    ),
    required_vars=[
        "portfolio_summary",
        "market_signal",
        "max_position_size",
        "max_drawdown_pct",
        "risk_reward_ratio",
    ],
    description="Structured trade entry/exit decision prompt.",
    version="1.0.0",
)

_RISK_ASSESSMENT_TEMPLATE = PromptTemplate(
    name="risk_assessment",
    template=(
        "You are a risk management officer. Evaluate the risk of the proposed trade.\n\n"
        "Proposed Trade:\n$trade_details\n\n"
        "Current Portfolio Exposure:\n$portfolio_exposure\n\n"
        "Market Conditions:\n$market_conditions\n\n"
        "Regulatory Constraints:\n$regulatory_context\n\n"
        "Provide a risk assessment including:\n"
        "RISK_SCORE: [0–100, higher = riskier]\n"
        "APPROVED: [YES|NO|CONDITIONAL]\n"
        "CONCERNS: [list of risk factors]\n"
        "MITIGATIONS: [list of recommended mitigations]\n"
        "POSITION_LIMIT: [maximum recommended position size]"
    ),
    required_vars=[
        "trade_details",
        "portfolio_exposure",
        "market_conditions",
        "regulatory_context",
    ],
    description="Risk assessment for proposed trades against portfolio and regulations.",
    version="1.0.0",
)

_EARNINGS_SUMMARY_TEMPLATE = PromptTemplate(
    name="earnings_summary",
    template=(
        "Summarise the following earnings report for $company ($ticker) for $period.\n\n"
        "Raw Report:\n$report_text\n\n"
        "Focus on: EPS vs estimate, revenue vs estimate, guidance, and market-moving"
        " surprises. Keep to 3 concise bullet points."
    ),
    required_vars=["company", "ticker", "period", "report_text"],
    description="Concise earnings report summary for trader consumption.",
    version="1.0.0",
)

_PORTFOLIO_REBALANCE_TEMPLATE = PromptTemplate(
    name="portfolio_rebalance",
    template=(
        "You are a portfolio manager. Review the current allocation and suggest "
        "rebalancing actions.\n\n"
        "Target Allocation:\n$target_allocation\n\n"
        "Current Allocation:\n$current_allocation\n\n"
        "Available Capital: $available_capital\n"
        "Transaction Cost Model: $cost_model\n\n"
        "List the minimum set of trades to reach the target allocation, "
        "considering transaction costs."
    ),
    required_vars=[
        "target_allocation",
        "current_allocation",
        "available_capital",
        "cost_model",
    ],
    description="Portfolio rebalancing instruction generator.",
    version="1.0.0",
)


class PromptTemplates:
    """Library of reusable prompt templates for the trading platform.

    Ships with built-in templates for market analysis, trade decisions,
    risk assessment, earnings summaries, and portfolio rebalancing.
    Custom templates can be registered at runtime.

    Attributes:
        _templates: All registered templates keyed by name.
    """

    def __init__(self) -> None:
        """Initialise with the built-in template set."""
        self._templates: dict[str, PromptTemplate] = {}
        for tpl in [
            _MARKET_ANALYSIS_TEMPLATE,
            _TRADE_DECISION_TEMPLATE,
            _RISK_ASSESSMENT_TEMPLATE,
            _EARNINGS_SUMMARY_TEMPLATE,
            _PORTFOLIO_REBALANCE_TEMPLATE,
        ]:
            self._templates[tpl.name] = tpl
        logger.info("PromptTemplates initialised with {} built-in templates", len(self._templates))

    def register(self, template: PromptTemplate, *, overwrite: bool = False) -> None:
        """Register a custom template.

        Args:
            template: Template to register.
            overwrite: Allow replacing an existing template with the same name.

        Raises:
            ValueError: If ``template.name`` already exists and
                ``overwrite=False``.
        """
        if template.name in self._templates and not overwrite:
            raise ValueError(
                f"Template '{template.name}' already exists. "
                "Pass overwrite=True to replace it."
            )
        self._templates[template.name] = template
        logger.info("Template '{}' registered (v{})", template.name, template.version)

    def get(self, name: str) -> PromptTemplate:
        """Retrieve a template by name.

        Args:
            name: Template identifier.

        Returns:
            The requested :class:`PromptTemplate`.

        Raises:
            KeyError: If no template with ``name`` is found.
        """
        if name not in self._templates:
            raise KeyError(
                f"Template '{name}' not found. "
                f"Available: {sorted(self._templates)}"
            )
        return self._templates[name]

    def render(self, name: str, **kwargs: Any) -> str:
        """Retrieve and immediately render a named template.

        Args:
            name: Template identifier.
            **kwargs: Variable substitutions.

        Returns:
            Rendered prompt string.

        Raises:
            KeyError: If template not found.
            ValueError: If required variables are missing.
        """
        return self.get(name).render(**kwargs)

    def list_templates(self) -> list[str]:
        """Return a sorted list of registered template names.

        Returns:
            Sorted list of template name strings.
        """
        return sorted(self._templates)
