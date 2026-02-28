"""
Audit Logger
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class AuditLogger:
    """Maintains audit trail of all platform activities"""
    
    def __init__(self):
        self.logger = logging.getLogger("audit_logger")
        self.audit_log: List[Dict[str, Any]] = []
    
    async def log_event(
        self,
        event_type: str,
        actor: str,
        resource: str,
        action: str,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ) -> Dict[str, Any]:
        """Log an audit event"""
        
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "resource": resource,
            "action": action,
            "status": status,
            "details": details or {},
            "event_id": f"evt-{len(self.audit_log) + 1}"
        }
        
        self.audit_log.append(event)
        
        # Keep only last 10000 events in memory
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-10000:]
        
        self.logger.info(
            f"Audit: {actor} {action} {resource} - {status}"
        )
        
        return event
    
    async def log_policy_decision(
        self,
        policy: str,
        decision: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a policy decision"""
        
        return await self.log_event(
            event_type="policy_decision",
            actor="policy_agent",
            resource=policy,
            action="evaluate",
            details={
                "decision": decision,
                "context": context
            }
        )
    
    async def log_deployment(
        self,
        deployment_spec: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a deployment event"""
        
        return await self.log_event(
            event_type="deployment",
            actor=deployment_spec.get("actor", "system"),
            resource=deployment_spec.get("name", "unknown"),
            action="deploy",
            details={
                "spec": deployment_spec,
                "result": result
            },
            status=result.get("status", "unknown")
        )
    
    async def log_compliance_check(
        self,
        resource: str,
        compliance_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Log a compliance check"""
        
        return await self.log_event(
            event_type="compliance_check",
            actor="compliance_agent",
            resource=resource,
            action="check_compliance",
            details=compliance_result,
            status="compliant" if compliance_result.get("compliant") else "non_compliant"
        )
    
    async def get_audit_trail(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit trail with optional filters"""
        
        filtered_log = self.audit_log
        
        if filters:
            if "actor" in filters:
                filtered_log = [
                    e for e in filtered_log
                    if e["actor"] == filters["actor"]
                ]
            
            if "resource" in filters:
                filtered_log = [
                    e for e in filtered_log
                    if e["resource"] == filters["resource"]
                ]
            
            if "event_type" in filters:
                filtered_log = [
                    e for e in filtered_log
                    if e["event_type"] == filters["event_type"]
                ]
        
        return filtered_log[-limit:]
    
    async def export_audit_log(
        self,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> str:
        """Export audit log as JSON"""
        
        filtered_log = self.audit_log
        
        if start_time:
            filtered_log = [
                e for e in filtered_log
                if e["timestamp"] >= start_time
            ]
        
        if end_time:
            filtered_log = [
                e for e in filtered_log
                if e["timestamp"] <= end_time
            ]
        
        return json.dumps(filtered_log, indent=2)
