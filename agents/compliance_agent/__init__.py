"""
Compliance Agent - Main Implementation
"""
from typing import Dict, Any, Optional
from agents.core.base_agent import BaseAgent, Message
from .compliance_checker import ComplianceChecker
from .audit_logger import AuditLogger
from .markers import ComplianceMarkers


class ComplianceAgent(BaseAgent):
    """Compliance Agent - Monitors and ensures compliance"""
    
    def __init__(self, agent_id: str = "compliance_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config)
        self.checker = None
        self.audit_logger = None
        self.markers = None
        
    async def initialize(self) -> bool:
        """Initialize the compliance agent"""
        try:
            self.checker = ComplianceChecker()
            self.audit_logger = AuditLogger()
            self.markers = ComplianceMarkers()
            
            self.logger.info("Compliance Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Compliance Agent: {str(e)}")
            return False
    
    async def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming compliance-related messages"""
        
        message_type = message.message_type
        payload = message.payload
        
        if message_type == "check_compliance":
            result = await self.checker.check_compliance(
                payload.get("resource", {}),
                payload.get("frameworks", [])
            )
            
            # Log compliance check
            await self.audit_logger.log_compliance_check(
                payload.get("resource_id", "unknown"),
                result
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="compliance_result",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "log_event":
            event = await self.audit_logger.log_event(
                event_type=payload.get("event_type", ""),
                actor=payload.get("actor", ""),
                resource=payload.get("resource", ""),
                action=payload.get("action", ""),
                details=payload.get("details"),
                status=payload.get("status", "success")
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="event_logged",
                payload=event,
                correlation_id=message.correlation_id
            )
        
        elif message_type == "get_audit_trail":
            trail = await self.audit_logger.get_audit_trail(
                filters=payload.get("filters"),
                limit=payload.get("limit", 100)
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="audit_trail",
                payload={"events": trail},
                correlation_id=message.correlation_id
            )
        
        elif message_type == "add_compliance_marker":
            self.markers.add_marker(
                payload.get("resource_id", ""),
                payload.get("marker", ""),
                payload.get("metadata")
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="marker_added",
                payload={"status": "success"},
                correlation_id=message.correlation_id
            )
        
        elif message_type == "validate_change":
            result = await self.checker.validate_change(
                payload.get("change_spec", {}),
                payload.get("requirements", [])
            )
            
            return Message(
                sender=self.agent_id,
                receiver=message.sender,
                message_type="change_validated",
                payload=result,
                correlation_id=message.correlation_id
            )
        
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
            return None
