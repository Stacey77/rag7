"""
Inference Agent - AI-driven decision making
"""
from typing import Dict, Any, Optional, List
from agents.core.base_agent import BaseAgent, Message
import logging

logger = logging.getLogger(__name__)


class InferenceAgent(BaseAgent):
    """Inference Agent - AI-driven decision making and recommendations"""
    
    def __init__(self, agent_id: str = "inference_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.model_config = None
        
    async def initialize(self) -> bool:
        """Initialize the inference agent"""
        try:
            self.model_config = self.config.get("model", {
                "type": "rule_based",  # Default to rule-based
                "temperature": 0.7
            })
            
            self.logger.info("Inference Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Inference Agent: {str(e)}")
            return False
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming inference requests"""
        
        message_type = message.message_type
        payload = message.payload
        
        if message_type == "recommend_action":
            recommendation = await self.recommend_action(
                payload.get("context", {}),
                payload.get("options", [])
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="action_recommendation",
                payload=recommendation,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "predict_outcome":
            prediction = await self.predict_outcome(
                payload.get("action", {}),
                payload.get("context", {})
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="outcome_prediction",
                payload=prediction,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "analyze_intent":
            analysis = await self.analyze_intent(
                payload.get("intent", {}),
                payload.get("historical_data", [])
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="intent_analysis",
                payload=analysis,
                correlation_id=message.correlation_id
            )
        
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
            return None
    
    async def recommend_action(
        self,
        context: Dict[str, Any],
        options: List[str]
    ) -> Dict[str, Any]:
        """Recommend best action based on context"""
        
        self.logger.info("Generating action recommendation")
        
        # Simple rule-based recommendation
        scores = {}
        for option in options:
            scores[option] = self._score_option(option, context)
        
        best_option = max(scores, key=scores.get) if scores else None
        
        return {
            "recommended_action": best_option,
            "scores": scores,
            "confidence": scores.get(best_option, 0.0) if best_option else 0.0,
            "reasoning": f"Based on context analysis, {best_option} has highest score"
        }
    
    def _score_option(self, option: str, context: Dict[str, Any]) -> float:
        """Score an option based on context"""
        
        score = 0.5  # Base score
        
        # Increase score for safer options
        if "rollback" in option.lower():
            score += 0.3
        elif "scale down" in option.lower():
            score += 0.2
        elif "deploy" in option.lower():
            score += 0.1
        
        # Adjust based on context
        if context.get("risk_level") == "high":
            if "rollback" in option.lower():
                score += 0.2
        
        return min(score, 1.0)
    
    async def predict_outcome(
        self,
        action: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict outcome of an action"""
        
        self.logger.info("Predicting action outcome")
        
        action_type = action.get("type", "unknown")
        
        # Simple outcome prediction
        outcomes = {
            "success_probability": 0.8,
            "estimated_duration_minutes": 5,
            "potential_issues": [],
            "rollback_required": False
        }
        
        # Adjust based on action type
        if action_type == "deploy":
            outcomes["success_probability"] = 0.85
            outcomes["estimated_duration_minutes"] = 10
        elif action_type == "rollback":
            outcomes["success_probability"] = 0.95
            outcomes["estimated_duration_minutes"] = 3
        elif action_type == "scale":
            outcomes["success_probability"] = 0.9
            outcomes["estimated_duration_minutes"] = 2
        
        # Add potential issues based on context
        if context.get("peak_hours", False):
            outcomes["potential_issues"].append("Deployment during peak hours")
            outcomes["success_probability"] -= 0.1
        
        return outcomes
    
    async def analyze_intent(
        self,
        intent: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze intent and provide insights"""
        
        self.logger.info("Analyzing intent")
        
        intent_type = intent.get("intent_type", "unknown")
        
        analysis = {
            "intent_type": intent_type,
            "complexity": "medium",
            "risk_level": "medium",
            "similar_past_actions": 0,
            "success_rate": 0.0,
            "recommendations": []
        }
        
        # Analyze historical data
        similar_actions = [
            h for h in historical_data
            if h.get("type") == intent_type
        ]
        
        analysis["similar_past_actions"] = len(similar_actions)
        
        if similar_actions:
            successes = sum(
                1 for a in similar_actions
                if a.get("status") == "success"
            )
            analysis["success_rate"] = successes / len(similar_actions)
        
        # Generate recommendations
        if analysis["success_rate"] < 0.5:
            analysis["recommendations"].append(
                "Low historical success rate - review and test thoroughly"
            )
        
        if intent_type == "deploy":
            analysis["recommendations"].append(
                "Consider blue-green deployment strategy"
            )
        
        return analysis
