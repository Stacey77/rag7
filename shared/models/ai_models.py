"""Pydantic models for AI/AGI components of the trading platform.

Provides:

* :class:`SignalDirection` – directional signal enum.
* :class:`SignalStrength` – confidence-band enum.
* :class:`TradingSignal` – raw signal emitted by a strategy or model.
* :class:`ModelPrediction` – structured output from an ML model.
* :class:`RiskAssessment` – risk evaluation for a proposed action.
* :class:`AGIDecision` – final decision produced by the AGI orchestrator.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SignalDirection(str, Enum):
    """Directional bias of a trading signal."""

    LONG = "LONG"
    SHORT = "SHORT"
    NEUTRAL = "NEUTRAL"
    EXIT_LONG = "EXIT_LONG"
    EXIT_SHORT = "EXIT_SHORT"


class SignalStrength(str, Enum):
    """Qualitative confidence band for a signal."""

    VERY_WEAK = "VERY_WEAK"
    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    VERY_STRONG = "VERY_STRONG"

    @classmethod
    def from_confidence(cls, confidence: float) -> "SignalStrength":
        """Map a [0, 1] confidence score to a :class:`SignalStrength`.

        Args:
            confidence: Normalised confidence value in [0, 1].

        Returns:
            Corresponding :class:`SignalStrength` bucket.

        Raises:
            ValueError: If *confidence* is outside [0, 1].
        """
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be in [0, 1], got {confidence}")
        if confidence < 0.2:
            return cls.VERY_WEAK
        if confidence < 0.4:
            return cls.WEAK
        if confidence < 0.6:
            return cls.MODERATE
        if confidence < 0.8:
            return cls.STRONG
        return cls.VERY_STRONG


class DecisionAction(str, Enum):
    """Action the AGI orchestrator has decided to take."""

    OPEN_LONG = "OPEN_LONG"
    OPEN_SHORT = "OPEN_SHORT"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"
    REDUCE_LONG = "REDUCE_LONG"
    REDUCE_SHORT = "REDUCE_SHORT"
    HOLD = "HOLD"
    HALT = "HALT"   # Emergency halt – close all positions.


# ---------------------------------------------------------------------------
# Shared config
# ---------------------------------------------------------------------------


class _BaseAIModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=False,
        json_encoders={Decimal: str, datetime: lambda v: v.isoformat()},
    )


# ---------------------------------------------------------------------------
# TradingSignal
# ---------------------------------------------------------------------------


class TradingSignal(_BaseAIModel):
    """Raw trading signal emitted by a strategy or sub-model.

    Args:
        signal_id: Unique signal identifier.
        symbol: Target instrument symbol.
        direction: Directional bias of the signal.
        confidence: Normalised confidence score in [0, 1].
        strength: Qualitative confidence band derived from *confidence*.
        price_target: Optional model price target.
        stop_loss: Optional suggested stop-loss level.
        take_profit: Optional suggested take-profit level.
        horizon_seconds: Forecast horizon in seconds.
        model_id: Identifier of the model or strategy that emitted the signal.
        features: Key model inputs used to generate the signal.
        timestamp: Signal generation timestamp (UTC-aware).
        expires_at: Optional expiry timestamp after which the signal is stale.
    """

    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = Field(..., min_length=1)
    direction: SignalDirection
    confidence: float = Field(..., ge=0.0, le=1.0)
    strength: SignalStrength | None = None
    price_target: Decimal | None = Field(None, gt=Decimal("0"))
    stop_loss: Decimal | None = Field(None, gt=Decimal("0"))
    take_profit: Decimal | None = Field(None, gt=Decimal("0"))
    horizon_seconds: int = Field(3600, ge=1)
    model_id: str = Field("unknown")
    features: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    expires_at: datetime | None = None

    @model_validator(mode="after")
    def _derive_strength(self) -> "TradingSignal":
        """Auto-populate *strength* from *confidence* if not provided."""
        if self.strength is None:
            object.__setattr__(
                self,
                "strength",
                SignalStrength.from_confidence(self.confidence),
            )
        return self

    @property
    def is_expired(self) -> bool:
        """``True`` when the signal has passed its expiry time."""
        if self.expires_at is None:
            return False
        return datetime.now(tz=timezone.utc) > self.expires_at

    @property
    def risk_reward_ratio(self) -> Decimal | None:
        """Risk/reward ratio when both stop-loss and take-profit are set.

        Calculated relative to *price_target* if present, otherwise returns
        *None* when insufficient data is available.
        """
        if self.price_target and self.stop_loss and self.take_profit:
            risk = abs(self.price_target - self.stop_loss)
            reward = abs(self.take_profit - self.price_target)
            if risk == Decimal("0"):
                return None
            return reward / risk
        return None


# ---------------------------------------------------------------------------
# ModelPrediction
# ---------------------------------------------------------------------------


class ModelPrediction(_BaseAIModel):
    """Structured output from a single ML model inference call.

    Args:
        prediction_id: Unique prediction identifier.
        model_id: Model name and optional version (e.g. ``"lstm-v3"``).
        model_version: Semantic version string of the model.
        symbol: Target instrument symbol.
        predicted_return: Expected return over *horizon_seconds* (fraction).
        predicted_volatility: Expected volatility (annualised fraction).
        confidence: Model confidence in [0, 1].
        raw_output: Full model output dict for traceability.
        feature_importance: Map of feature name → importance score.
        latency_ms: Model inference latency in milliseconds.
        timestamp: Inference timestamp (UTC-aware).
        horizon_seconds: Prediction horizon in seconds.
    """

    prediction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_id: str = Field(..., min_length=1)
    model_version: str = Field("0.0.0")
    symbol: str = Field(..., min_length=1)
    predicted_return: float = Field(
        ..., description="Expected fractional return over the horizon."
    )
    predicted_volatility: float = Field(
        0.0, ge=0.0, description="Expected annualised volatility."
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    raw_output: dict[str, Any] = Field(default_factory=dict)
    feature_importance: dict[str, float] = Field(default_factory=dict)
    latency_ms: float = Field(0.0, ge=0.0)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    horizon_seconds: int = Field(3600, ge=1)

    @field_validator("feature_importance")
    @classmethod
    def _validate_importance_values(
        cls, v: dict[str, float]
    ) -> dict[str, float]:
        """Ensure all importance scores are non-negative."""
        for name, score in v.items():
            if score < 0:
                raise ValueError(
                    f"Feature importance for {name!r} must be >= 0, got {score}"
                )
        return v

    @property
    def direction(self) -> SignalDirection:
        """Implied directional signal from the predicted return."""
        if self.predicted_return > 0:
            return SignalDirection.LONG
        if self.predicted_return < 0:
            return SignalDirection.SHORT
        return SignalDirection.NEUTRAL


# ---------------------------------------------------------------------------
# RiskAssessment
# ---------------------------------------------------------------------------


class RiskAssessment(_BaseAIModel):
    """Risk evaluation for a proposed trade or portfolio state.

    Args:
        assessment_id: Unique assessment identifier.
        symbol: Instrument being assessed.
        proposed_quantity: Trade size being evaluated.
        proposed_notional_usd: Estimated USD notional value.
        current_drawdown_pct: Portfolio drawdown at time of assessment.
        position_concentration_pct: Concentration of the symbol in the portfolio.
        var_1d_pct: 1-day Value-at-Risk as a percentage of portfolio equity.
        sharpe_estimate: Estimated Sharpe ratio for the proposed trade.
        is_approved: Whether the risk gate approved the trade.
        rejection_reasons: Human-readable reasons when *is_approved* is False.
        risk_score: Composite risk score in [0, 1] (higher = riskier).
        timestamp: Assessment timestamp (UTC-aware).
    """

    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = Field(..., min_length=1)
    proposed_quantity: Decimal = Field(..., gt=Decimal("0"))
    proposed_notional_usd: Decimal = Field(..., ge=Decimal("0"))
    current_drawdown_pct: float = Field(0.0, ge=0.0, le=100.0)
    position_concentration_pct: float = Field(0.0, ge=0.0, le=100.0)
    var_1d_pct: float = Field(0.0, ge=0.0)
    sharpe_estimate: float | None = None
    is_approved: bool = True
    rejection_reasons: list[str] = Field(default_factory=list)
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    @model_validator(mode="after")
    def _sync_approval(self) -> "RiskAssessment":
        """Mark as rejected when rejection reasons are present."""
        if self.rejection_reasons and self.is_approved:
            object.__setattr__(self, "is_approved", False)
        return self


# ---------------------------------------------------------------------------
# AGIDecision
# ---------------------------------------------------------------------------


class AGIDecision(_BaseAIModel):
    """Final decision produced by the AGI orchestration layer.

    Aggregates signals, model predictions, and risk assessment into a single
    actionable decision that can be forwarded to the execution engine.

    Args:
        decision_id: Unique decision identifier.
        symbol: Instrument the decision applies to.
        action: The action the AGI has decided to take.
        confidence: Aggregate decision confidence in [0, 1].
        suggested_quantity: Suggested order quantity (None for HOLD/HALT).
        suggested_price: Optional limit-price recommendation.
        signals: Input signals that contributed to this decision.
        predictions: Model predictions considered by the AGI.
        risk_assessment: Risk gate evaluation for this decision.
        reasoning: Human-readable explanation of the decision.
        metadata: Arbitrary extra fields for traceability.
        timestamp: Decision timestamp (UTC-aware).
        executed: Whether the decision has been forwarded to execution.
        execution_order_id: Order ID assigned by the execution engine.
    """

    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = Field(..., min_length=1)
    action: DecisionAction
    confidence: float = Field(..., ge=0.0, le=1.0)
    suggested_quantity: Decimal | None = Field(None, gt=Decimal("0"))
    suggested_price: Decimal | None = Field(None, gt=Decimal("0"))
    signals: list[TradingSignal] = Field(default_factory=list)
    predictions: list[ModelPrediction] = Field(default_factory=list)
    risk_assessment: RiskAssessment | None = None
    reasoning: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    executed: bool = False
    execution_order_id: str | None = None

    @property
    def is_actionable(self) -> bool:
        """``True`` when the decision requires order submission.

        An actionable decision has a non-HOLD/HALT action, a suggested
        quantity, and an approved risk assessment.
        """
        if self.action in {DecisionAction.HOLD, DecisionAction.HALT}:
            return False
        if self.suggested_quantity is None:
            return False
        if self.risk_assessment and not self.risk_assessment.is_approved:
            return False
        return True

    @property
    def average_signal_confidence(self) -> float:
        """Mean confidence across all contributing signals."""
        if not self.signals:
            return 0.0
        return sum(s.confidence for s in self.signals) / len(self.signals)

    def mark_executed(self, order_id: str) -> "AGIDecision":
        """Return a copy of this decision marked as executed.

        Args:
            order_id: The order ID returned by the execution engine.

        Returns:
            Updated :class:`AGIDecision` (immutable copy).
        """
        return self.model_copy(
            update={"executed": True, "execution_order_id": order_id}
        )
