"""Agent Decision System for task processing and decision making."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import redis.asyncio as redis

from app.agents.communication import TaskState, AgentCommunicationSystem


class DecisionType(str, Enum):
    """Types of agent decisions."""
    TASK_ACCEPT = "task_accept"
    TASK_REJECT = "task_reject"
    TASK_DELEGATE = "task_delegate"
    TASK_COMPLETE = "task_complete"
    TASK_FAIL = "task_fail"
    HUMAN_OVERRIDE = "human_override"
    AUTO_ESCALATE = "auto_escalate"


class ConfidenceLevel(str, Enum):
    """Confidence levels for decisions."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class AgentDecision:
    """Represents a decision made by an agent."""
    
    def __init__(
        self,
        decision_id: str,
        task_id: str,
        agent_id: str,
        decision_type: DecisionType,
        confidence: ConfidenceLevel,
        rationale: str,
        metadata: Optional[dict] = None,
        timestamp: Optional[datetime] = None
    ):
        self.decision_id = decision_id
        self.task_id = task_id
        self.agent_id = agent_id
        self.decision_type = decision_type
        self.confidence = confidence
        self.rationale = rationale
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now(timezone.utc)
    
    def to_dict(self) -> dict:
        return {
            "decision_id": self.decision_id,
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "decision_type": self.decision_type.value,
            "confidence": self.confidence.value,
            "rationale": self.rationale,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class AgentDecisionSystem:
    """
    Decision system for autonomous agents.
    
    Features:
    - Process incoming tasks and make decisions
    - Track decision history
    - Support human override and escalation
    - Integrate with confidence thresholds
    """
    
    CONFIDENCE_THRESHOLD = ConfidenceLevel.MEDIUM
    
    def __init__(
        self,
        agent_id: str,
        communication_system: AgentCommunicationSystem
    ):
        self.agent_id = agent_id
        self.comm_system = communication_system
        self.decision_history: list[AgentDecision] = []
    
    async def process_task(
        self,
        task_id: str,
        payload: dict,
        correlation_id: str
    ) -> AgentDecision:
        """
        Process an incoming task and make a decision.
        
        This is a placeholder implementation that should be overridden
        with actual task processing logic.
        """
        # Evaluate task and determine confidence
        confidence = await self._evaluate_confidence(payload)
        
        # Make decision based on confidence
        if confidence in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM]:
            decision_type = DecisionType.TASK_ACCEPT
            rationale = "Task accepted based on confidence evaluation"
        else:
            decision_type = DecisionType.AUTO_ESCALATE
            rationale = "Low confidence - escalating for review"
        
        decision = AgentDecision(
            decision_id=str(uuid.uuid4()),
            task_id=task_id,
            agent_id=self.agent_id,
            decision_type=decision_type,
            confidence=confidence,
            rationale=rationale,
            metadata={"correlation_id": correlation_id}
        )
        
        self.decision_history.append(decision)
        
        # Send ack if accepting
        if decision_type == DecisionType.TASK_ACCEPT:
            await self.comm_system.send_ack(
                correlation_id=correlation_id,
                task_id=task_id,
                agent_id=self.agent_id,
                status="accepted",
                metadata=decision.to_dict()
            )
        
        return decision
    
    async def _evaluate_confidence(self, payload: dict) -> ConfidenceLevel:
        """
        Evaluate confidence level for processing a task.
        
        This is a placeholder - real implementation would use ML models.
        """
        # Simple heuristic for demo purposes
        if payload.get("priority") == "high":
            return ConfidenceLevel.MEDIUM
        elif payload.get("type") in ["simple", "routine"]:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.LOW
    
    async def complete_task(
        self,
        task_id: str,
        result: Any,
        success: bool = True
    ) -> AgentDecision:
        """Mark a task as completed."""
        decision = AgentDecision(
            decision_id=str(uuid.uuid4()),
            task_id=task_id,
            agent_id=self.agent_id,
            decision_type=DecisionType.TASK_COMPLETE if success else DecisionType.TASK_FAIL,
            confidence=ConfidenceLevel.HIGH,
            rationale="Task processing completed",
            metadata={"result": result, "success": success}
        )
        
        self.decision_history.append(decision)
        return decision
    
    async def request_human_override(
        self,
        task_id: str,
        reason: str,
        options: Optional[list[dict]] = None
    ) -> AgentDecision:
        """Request human override for a decision."""
        decision = AgentDecision(
            decision_id=str(uuid.uuid4()),
            task_id=task_id,
            agent_id=self.agent_id,
            decision_type=DecisionType.HUMAN_OVERRIDE,
            confidence=ConfidenceLevel.UNCERTAIN,
            rationale=reason,
            metadata={"options": options or [], "requires_human": True}
        )
        
        self.decision_history.append(decision)
        return decision
    
    def get_decision_history(
        self,
        task_id: Optional[str] = None,
        limit: int = 100
    ) -> list[AgentDecision]:
        """Get decision history, optionally filtered by task."""
        history = self.decision_history
        if task_id:
            history = [d for d in history if d.task_id == task_id]
        return history[-limit:]
