"""Admin API endpoints for agent and system management."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import AgentType
from app.db.crud import AgentCRUD, ModelCRUD
from app.api.auth import require_any_role, User
from app.core import Role
from app.agents.learning import AgentLearningSystem

router = APIRouter(prefix="/admin", tags=["admin"])


class AgentCreate(BaseModel):
    """Agent creation request."""
    agent_type: str
    name: str
    version: str
    config: dict = {}
    max_load: int = 10


class AgentResponse(BaseModel):
    """Agent response model."""
    id: int
    agent_type: str
    name: str
    version: str
    is_active: bool
    current_load: int
    max_load: int
    
    class Config:
        from_attributes = True


class ModelResponse(BaseModel):
    """Model response model."""
    id: int
    name: str
    version: str
    agent_type: str
    is_active: bool
    metrics: dict = {}
    
    class Config:
        from_attributes = True


class TrainingRequest(BaseModel):
    """Training job request."""
    agent_type: str


@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    request: AgentCreate,
    current_user: User = Depends(require_any_role(Role.ADMIN, Role.AGENT_MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new agent (requires admin or agent_manager role).
    """
    try:
        agent_type = AgentType(request.agent_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {request.agent_type}"
        )
    
    agent = await AgentCRUD.create_agent(
        db,
        agent_type=agent_type,
        name=request.name,
        version=request.version,
        config=request.config,
        max_load=request.max_load
    )
    
    return AgentResponse(
        id=agent.id,
        agent_type=agent.agent_type.value,
        name=agent.name,
        version=agent.version,
        is_active=bool(agent.is_active),
        current_load=agent.current_load,
        max_load=agent.max_load
    )


@router.get("/agents", response_model=List[AgentResponse])
async def list_agents(
    agent_type: str = None,
    current_user: User = Depends(require_any_role(Role.ADMIN, Role.AGENT_MANAGER, Role.VIEWER)),
    db: AsyncSession = Depends(get_db)
):
    """
    List all agents, optionally filtered by type.
    """
    # This would need proper implementation with pagination
    # For now, return empty list
    return []


@router.get("/models", response_model=List[ModelResponse])
async def list_models(
    agent_type: str = None,
    current_user: User = Depends(require_any_role(Role.ADMIN, Role.AGENT_MANAGER, Role.VIEWER)),
    db: AsyncSession = Depends(get_db)
):
    """
    List all models in the model registry.
    """
    # This would need proper implementation with pagination
    return []


@router.post("/training/trigger")
async def trigger_training(
    request: TrainingRequest,
    current_user: User = Depends(require_any_role(Role.ADMIN, Role.AGENT_MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger a training job for an agent type.
    """
    try:
        agent_type = AgentType(request.agent_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type: {request.agent_type}"
        )
    
    learning_system = AgentLearningSystem(agent_type)
    training_job = await learning_system.trigger_training(db)
    
    return {
        "success": True,
        "training_job": training_job
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "agentic-platform-api"
    }


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(require_any_role(Role.ADMIN, Role.VIEWER)),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system statistics.
    """
    # Placeholder implementation
    return {
        "total_tasks": 0,
        "active_agents": 0,
        "models_trained": 0,
        "escalations_today": 0
    }
