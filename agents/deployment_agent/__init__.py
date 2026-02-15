"""
Deployment Agent - Main Implementation
"""
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent, Message
from .kubernetes import KubernetesDeployer
from .multi_region import MultiRegionManager
from .failover import FailoverManager


class DeploymentAgent(BaseAgent):
    """CD Agent - Handles deployment orchestration"""
    
    def __init__(self, agent_id: str = "deployment_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.k8s_deployer = None
        self.multi_region = None
        self.failover = None
        
    async def initialize(self) -> bool:
        """Initialize the deployment agent"""
        try:
            self.k8s_deployer = KubernetesDeployer(self.config.get("kubernetes", {}))
            self.multi_region = MultiRegionManager()
            self.failover = FailoverManager()
            
            self.logger.info("Deployment Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Deployment Agent: {str(e)}")
            return False
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming deployment-related messages"""
        
        message_type = message.message_type
        payload = message.payload
        
        if message_type == "deploy":
            result = await self.k8s_deployer.deploy(payload.get("spec", {}))
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="deployment_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "deploy_multi_region":
            result = await self.multi_region.deploy_to_regions(
                payload.get("spec", {}),
                payload.get("regions", [])
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="multi_region_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "scale":
            result = await self.k8s_deployer.scale(
                payload.get("deployment_name", ""),
                payload.get("replicas", 3)
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="scale_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "rollback":
            result = await self.k8s_deployer.rollback(
                payload.get("deployment_name", ""),
                payload.get("revision")
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="rollback_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "configure_failover":
            result = await self.failover.configure_failover(
                payload.get("service", ""),
                payload.get("primary_region", ""),
                payload.get("failover_regions", []),
                payload.get("health_check_interval", 30)
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="failover_configured",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "trigger_failover":
            result = await self.failover.trigger_failover(
                payload.get("service", ""),
                payload.get("target_region")
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="failover_triggered",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "get_deployment_status":
            result = await self.k8s_deployer.get_status(
                payload.get("deployment_name", "")
            )
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="deployment_status",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
            return None
