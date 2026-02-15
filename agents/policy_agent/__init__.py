"""
Policy Agent - Main Implementation
"""
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent, Message
from .policy_engine import LocalPolicyEngine
from .blast_radius import BlastRadiusPredictor
from .enforcement import PolicyEnforcement


class PolicyAgent(BaseAgent):
    """Policy Agent - Enforces governance policies across all automation"""
    
    def __init__(self, agent_id: str = "policy_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.enforcement = None
        
    async def initialize(self) -> bool:
        """Initialize the policy agent"""
        try:
            use_opa = self.config.get("use_opa", False)
            opa_url = self.config.get("opa_url", "http://localhost:8181")
            
            self.enforcement = PolicyEnforcement(use_opa, opa_url)
            
            # Load default policies if using local engine
            if not use_opa:
                await self._load_default_policies()
            
            self.logger.info("Policy Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Policy Agent: {str(e)}")
            return False
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming policy-related messages"""
        
        message_type = message.message_type
        payload = message.payload
        
        if message_type == "enforce_policy":
            result = await self.enforcement.enforce_policies(
                payload.get("action"),
                payload.get("context", {})
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="policy_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "predict_blast_radius":
            result = await self.enforcement.blast_predictor.predict_impact(
                payload.get("change_spec", {})
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="blast_radius_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "validate_script":
            result = await self.enforcement.validate_before_execution(
                payload.get("script", ""),
                payload.get("context", {})
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="validation_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "simulate_policy":
            result = await self.enforcement.simulate_policy(
                payload.get("action"),
                payload.get("context", {})
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="simulation_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
            return None
    
    async def _load_default_policies(self):
        """Load default policies for local engine"""
        if isinstance(self.enforcement.policy_engine, LocalPolicyEngine):
            # Load default deployment policy
            self.enforcement.policy_engine.load_policy(
                "deployment/validate",
                {
                    "require_approval": {
                        "type": "require",
                        "field": "approver",
                        "message": "Deployment requires approval"
                    },
                    "valid_environment": {
                        "type": "allow",
                        "message": "Environment is valid"
                    }
                }
            )
            
            # Load default script policy
            self.enforcement.policy_engine.load_policy(
                "script/validate",
                {
                    "safe_commands": {
                        "type": "allow",
                        "message": "Script commands are safe"
                    }
                }
            )
