"""Admin API endpoints for system management."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_active_user, require_role, Role, User
from app.db.session import get_db
from app.db import crud


router = APIRouter()


class AgentCreate(BaseModel):
    """Agent creation request."""
    name: str
    agent_type: str
    capabilities: list[str] = []
    config: dict = {}


class AgentResponse(BaseModel):
    """Agent response model."""
    id: str
    name: str
    agent_type: str
    status: str
    capabilities: list[str]
    config: dict


class ModelCreate(BaseModel):
    """Model registration request."""
    name: str
    version: str
    agent_id: str
    training_job_id: Optional[str] = None
    metrics: dict = {}
    artifact_path: Optional[str] = None
    is_active: bool = False


class ModelResponse(BaseModel):
    """Model response model."""
    id: str
    name: str
    version: str
    agent_id: str
    metrics: dict
    artifact_path: Optional[str]
    is_active: bool


class TrainingJobCreate(BaseModel):
    """Training job creation request."""
    model_name: str
    agent_id: str
    config: dict = {}
    feedback_ids: list[str] = []


# Agent Management

@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    agent: AgentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN))
):
    """Create a new agent (admin only)."""
    db_agent = await crud.create_agent(
        db=db,
        name=agent.name,
        agent_type=agent.agent_type,
        capabilities=agent.capabilities,
        config=agent.config
    )
    
    return AgentResponse(
        id=db_agent.id,
        name=db_agent.name,
        agent_type=db_agent.agent_type,
        status=db_agent.status,
        capabilities=db_agent.capabilities,
        config=db_agent.config
    )


@router.get("/agents")
async def list_agents(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """List all agents."""
    agents = await crud.get_agents(db, status=status)
    
    return {
        "agents": [
            AgentResponse(
                id=a.id,
                name=a.name,
                agent_type=a.agent_type,
                status=a.status,
                capabilities=a.capabilities,
                config=a.config
            )
            for a in agents
        ]
    }


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """Get agent by ID."""
    agent = await crud.get_agent(db, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return AgentResponse(
        id=agent.id,
        name=agent.name,
        agent_type=agent.agent_type,
        status=agent.status,
        capabilities=agent.capabilities,
        config=agent.config
    )


@router.patch("/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    new_status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN))
):
    """Update agent status."""
    agent = await crud.update_agent_status(db, agent_id, new_status)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return {"status": "updated", "new_status": new_status}


# Model Registry

@router.post("/models", response_model=ModelResponse)
async def register_model(
    model: ModelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """Register a trained model in the registry."""
    db_model = await crud.create_model(
        db=db,
        name=model.name,
        version=model.version,
        agent_id=model.agent_id,
        training_job_id=model.training_job_id,
        metrics=model.metrics,
        artifact_path=model.artifact_path,
        is_active=model.is_active
    )
    
    return ModelResponse(
        id=db_model.id,
        name=db_model.name,
        version=db_model.version,
        agent_id=db_model.agent_id,
        metrics=db_model.metrics,
        artifact_path=db_model.artifact_path,
        is_active=db_model.is_active
    )


@router.get("/models")
async def list_models(
    agent_id: Optional[str] = None,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List models from the registry."""
    models = await crud.get_models(
        db=db,
        agent_id=agent_id,
        active_only=active_only
    )
    
    return {
        "models": [
            ModelResponse(
                id=m.id,
                name=m.name,
                version=m.version,
                agent_id=m.agent_id,
                metrics=m.metrics,
                artifact_path=m.artifact_path,
                is_active=m.is_active
            )
            for m in models
        ]
    }


@router.post("/models/{model_id}/activate")
async def activate_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """Activate a model version (deactivates other versions of same model)."""
    model = await crud.activate_model(db, model_id)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return {"status": "activated", "model_id": model_id}


# Training Jobs

@router.post("/training-jobs")
async def create_training_job(
    job: TrainingJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """Create and enqueue a training job."""
    # In a full implementation, this would enqueue a Celery task
    db_job = await crud.create_training_job(
        db=db,
        model_name=job.model_name,
        agent_id=job.agent_id,
        config=job.config,
        feedback_ids=job.feedback_ids
    )
    
    # TODO: Enqueue Celery task
    # from app.tasks.training import run_training_job
    # run_training_job.delay(db_job.id)
    
    return {
        "job_id": db_job.id,
        "status": db_job.status,
        "message": "Training job created and queued"
    }


@router.get("/training-jobs")
async def list_training_jobs(
    status: Optional[str] = None,
    agent_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """List training jobs."""
    jobs = await crud.get_training_jobs(
        db=db,
        status=status,
        agent_id=agent_id
    )
    
    return {
        "jobs": [
            {
                "id": j.id,
                "model_name": j.model_name,
                "agent_id": j.agent_id,
                "status": j.status,
                "config": j.config,
                "created_at": j.created_at,
                "started_at": j.started_at,
                "completed_at": j.completed_at
            }
            for j in jobs
        ]
    }


# Audit Log

@router.get("/audits")
async def get_audit_log(
    entity_type: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.ADMIN))
):
    """Get audit log (admin only)."""
    audits = await crud.get_audits(
        db=db,
        entity_type=entity_type,
        user_id=user_id,
        limit=limit
    )
    
    return {
        "audits": [
            {
                "id": a.id,
                "action": a.action,
                "entity_type": a.entity_type,
                "entity_id": a.entity_id,
                "user_id": a.user_id,
                "details": a.details,
                "created_at": a.created_at
            }
            for a in audits
        ]
    }


# System Stats

@router.get("/stats")
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """Get system statistics."""
    stats = await crud.get_system_stats(db)
    return stats
