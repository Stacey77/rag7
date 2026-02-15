"""
API Schemas
"""
try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Fallback to dict-based schemas if pydantic not available
    PYDANTIC_AVAILABLE = False
    BaseModel = dict
    def Field(*args, **kwargs):
        return kwargs.get('default', None)

from typing import Dict, Any, List, Optional
from datetime import datetime


class IntentRequest(BaseModel):
    """Request to process user intent"""
    user_input: str = Field(..., description="User's natural language input")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class IntentResponse(BaseModel):
    """Response from intent processing"""
    intent: Dict[str, Any]
    validation: Dict[str, Any]
    script: Optional[Dict[str, Any]] = None


class DeploymentRequest(BaseModel):
    """Request to deploy an application"""
    name: str = Field(..., description="Application name")
    image: str = Field(..., description="Container image")
    replicas: int = Field(default=3, ge=1, le=100, description="Number of replicas")
    environment: str = Field(default="production", description="Target environment")
    regions: Optional[List[str]] = Field(default=None, description="Target regions for multi-region deployment")


class DeploymentResponse(BaseModel):
    """Response from deployment"""
    status: str
    deployment_id: str
    endpoints: List[str]
    message: Optional[str] = None


class PolicyCheckRequest(BaseModel):
    """Request to check policy"""
    action: str = Field(..., description="Action to validate")
    context: Dict[str, Any] = Field(..., description="Action context")
    change_spec: Optional[Dict[str, Any]] = Field(default=None, description="Change specification for blast radius")


class PolicyCheckResponse(BaseModel):
    """Response from policy check"""
    allowed: bool
    final_decision: str
    policy_checks: List[Dict[str, Any]]
    blast_radius: Optional[Dict[str, Any]] = None
    approval_required: Optional[bool] = None


class ComplianceCheckRequest(BaseModel):
    """Request to check compliance"""
    resource: Dict[str, Any] = Field(..., description="Resource to check")
    resource_id: str = Field(..., description="Resource identifier")
    frameworks: List[str] = Field(..., description="Compliance frameworks to check against")


class ComplianceCheckResponse(BaseModel):
    """Response from compliance check"""
    compliant: bool
    frameworks: Dict[str, Any]
    violations: List[Dict[str, Any]]
    warnings: List[str]


class AgentStatusResponse(BaseModel):
    """Agent status response"""
    agent_id: str
    status: str
    queue_size: int


class PlatformStatusResponse(BaseModel):
    """Platform status response"""
    platform: str
    version: str
    agents: Dict[str, AgentStatusResponse]
    healthy: bool


class AuditLogRequest(BaseModel):
    """Request to get audit logs"""
    filters: Optional[Dict[str, Any]] = None
    limit: int = Field(default=100, ge=1, le=1000)


class AuditLogResponse(BaseModel):
    """Audit log response"""
    events: List[Dict[str, Any]]
    total: int
