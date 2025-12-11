"""CRUD operations for database models."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Event, Task, Agent, Audit, Feedback, Model, TrainingJob


# Event operations

async def create_event(
    db: AsyncSession,
    event_type: str,
    entity_type: str,
    entity_id: str,
    data: dict,
    user_id: Optional[str] = None
) -> Event:
    """Create a new event in the event store."""
    event = Event(
        id=str(uuid.uuid4()),
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        data=data,
        user_id=user_id
    )
    db.add(event)
    await db.flush()
    return event


async def get_events(
    db: AsyncSession,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 100
) -> list[Event]:
    """Get events with optional filters."""
    query = select(Event).order_by(Event.created_at.desc()).limit(limit)
    
    if entity_type:
        query = query.where(Event.entity_type == entity_type)
    if entity_id:
        query = query.where(Event.entity_id == entity_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    result = await db.execute(query)
    return list(result.scalars().all())


# Task operations

async def create_task(
    db: AsyncSession,
    task_id: str,
    title: str,
    description: Optional[str] = None,
    task_type: str = "default",
    priority: str = "medium",
    payload: dict = None,
    assigned_agent_id: Optional[str] = None
) -> Task:
    """Create a new task."""
    task = Task(
        id=task_id,
        title=title,
        description=description,
        task_type=task_type,
        priority=priority,
        payload=payload or {},
        assigned_agent_id=assigned_agent_id,
        state="queued"
    )
    db.add(task)
    await db.flush()
    return task


async def get_task(db: AsyncSession, task_id: str) -> Optional[Task]:
    """Get a task by ID."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def get_tasks(
    db: AsyncSession,
    state: Optional[str] = None,
    agent_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> list[Task]:
    """Get tasks with optional filters."""
    query = select(Task).order_by(Task.created_at.desc()).limit(limit).offset(offset)
    
    if state:
        query = query.where(Task.state == state)
    if agent_id:
        query = query.where(Task.assigned_agent_id == agent_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_task_state(
    db: AsyncSession,
    task_id: str,
    state: str,
    increment_retry: bool = False
) -> Optional[Task]:
    """Update task state."""
    task = await get_task(db, task_id)
    if not task:
        return None
    
    task.state = state
    task.updated_at = datetime.now(timezone.utc)
    if increment_retry:
        task.retry_count += 1
    
    await db.flush()
    return task


# Agent operations

async def create_agent(
    db: AsyncSession,
    name: str,
    agent_type: str,
    capabilities: list = None,
    config: dict = None
) -> Agent:
    """Create a new agent."""
    agent = Agent(
        id=str(uuid.uuid4()),
        name=name,
        agent_type=agent_type,
        capabilities=capabilities or [],
        config=config or {},
        status="available"
    )
    db.add(agent)
    await db.flush()
    return agent


async def get_agent(db: AsyncSession, agent_id: str) -> Optional[Agent]:
    """Get an agent by ID."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    return result.scalar_one_or_none()


async def get_agents(
    db: AsyncSession,
    status: Optional[str] = None
) -> list[Agent]:
    """Get all agents with optional status filter."""
    query = select(Agent).order_by(Agent.name)
    
    if status:
        query = query.where(Agent.status == status)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_agent_status(
    db: AsyncSession,
    agent_id: str,
    status: str
) -> Optional[Agent]:
    """Update agent status."""
    agent = await get_agent(db, agent_id)
    if not agent:
        return None
    
    agent.status = status
    agent.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return agent


# Audit operations

async def create_audit(
    db: AsyncSession,
    action: str,
    entity_type: str,
    entity_id: str,
    user_id: str,
    details: dict = None
) -> Audit:
    """Create an audit record."""
    audit = Audit(
        id=str(uuid.uuid4()),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        details=details or {}
    )
    db.add(audit)
    await db.flush()
    return audit


async def get_audits(
    db: AsyncSession,
    entity_type: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 100
) -> list[Audit]:
    """Get audit records with optional filters."""
    query = select(Audit).order_by(Audit.created_at.desc()).limit(limit)
    
    if entity_type:
        query = query.where(Audit.entity_type == entity_type)
    if user_id:
        query = query.where(Audit.user_id == user_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


# Feedback operations

async def create_feedback(
    db: AsyncSession,
    task_id: str,
    agent_id: str,
    feedback_type: str,
    content: dict,
    source_user_id: Optional[str] = None
) -> Feedback:
    """Create feedback record."""
    feedback = Feedback(
        id=str(uuid.uuid4()),
        task_id=task_id,
        agent_id=agent_id,
        feedback_type=feedback_type,
        content=content,
        source_user_id=source_user_id
    )
    db.add(feedback)
    await db.flush()
    return feedback


async def get_feedback(
    db: AsyncSession,
    agent_id: Optional[str] = None,
    task_id: Optional[str] = None,
    limit: int = 100
) -> list[Feedback]:
    """Get feedback records."""
    query = select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)
    
    if agent_id:
        query = query.where(Feedback.agent_id == agent_id)
    if task_id:
        query = query.where(Feedback.task_id == task_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


# Model operations

async def create_model(
    db: AsyncSession,
    name: str,
    version: str,
    agent_id: str,
    training_job_id: Optional[str] = None,
    metrics: dict = None,
    artifact_path: Optional[str] = None,
    is_active: bool = False
) -> Model:
    """Create a model registry entry."""
    model = Model(
        id=str(uuid.uuid4()),
        name=name,
        version=version,
        agent_id=agent_id,
        training_job_id=training_job_id,
        metrics=metrics or {},
        artifact_path=artifact_path,
        is_active=is_active
    )
    db.add(model)
    await db.flush()
    return model


async def get_models(
    db: AsyncSession,
    agent_id: Optional[str] = None,
    active_only: bool = False
) -> list[Model]:
    """Get models from registry."""
    query = select(Model).order_by(Model.created_at.desc())
    
    if agent_id:
        query = query.where(Model.agent_id == agent_id)
    if active_only:
        query = query.where(Model.is_active == True)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def activate_model(
    db: AsyncSession,
    model_id: str
) -> Optional[Model]:
    """Activate a model (deactivates others with same name)."""
    model = await db.execute(select(Model).where(Model.id == model_id))
    model = model.scalar_one_or_none()
    
    if not model:
        return None
    
    # Deactivate other versions
    other_models = await db.execute(
        select(Model).where(
            Model.name == model.name,
            Model.id != model_id
        )
    )
    for m in other_models.scalars().all():
        m.is_active = False
    
    model.is_active = True
    await db.flush()
    return model


# Training job operations

async def create_training_job(
    db: AsyncSession,
    model_name: str,
    agent_id: str,
    config: dict = None,
    feedback_ids: list = None
) -> TrainingJob:
    """Create a training job."""
    job = TrainingJob(
        id=str(uuid.uuid4()),
        model_name=model_name,
        agent_id=agent_id,
        status="pending",
        config={
            **(config or {}),
            "feedback_ids": feedback_ids or []
        }
    )
    db.add(job)
    await db.flush()
    return job


async def get_training_jobs(
    db: AsyncSession,
    status: Optional[str] = None,
    agent_id: Optional[str] = None
) -> list[TrainingJob]:
    """Get training jobs."""
    query = select(TrainingJob).order_by(TrainingJob.created_at.desc())
    
    if status:
        query = query.where(TrainingJob.status == status)
    if agent_id:
        query = query.where(TrainingJob.agent_id == agent_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_training_job_status(
    db: AsyncSession,
    job_id: str,
    status: str,
    error_message: Optional[str] = None
) -> Optional[TrainingJob]:
    """Update training job status."""
    result = await db.execute(select(TrainingJob).where(TrainingJob.id == job_id))
    job = result.scalar_one_or_none()
    
    if not job:
        return None
    
    job.status = status
    
    if status == "running":
        job.started_at = datetime.now(timezone.utc)
    elif status in ["completed", "failed"]:
        job.completed_at = datetime.now(timezone.utc)
        if error_message:
            job.error_message = error_message
    
    await db.flush()
    return job


# System stats

async def get_system_stats(db: AsyncSession) -> dict:
    """Get system statistics."""
    # Task stats
    task_count = await db.execute(select(func.count(Task.id)))
    task_count = task_count.scalar() or 0
    
    escalated_count = await db.execute(
        select(func.count(Task.id)).where(Task.state == "escalated")
    )
    escalated_count = escalated_count.scalar() or 0
    
    # Agent stats
    agent_count = await db.execute(select(func.count(Agent.id)))
    agent_count = agent_count.scalar() or 0
    
    available_agents = await db.execute(
        select(func.count(Agent.id)).where(Agent.status == "available")
    )
    available_agents = available_agents.scalar() or 0
    
    # Model stats
    model_count = await db.execute(select(func.count(Model.id)))
    model_count = model_count.scalar() or 0
    
    active_models = await db.execute(
        select(func.count(Model.id)).where(Model.is_active == True)
    )
    active_models = active_models.scalar() or 0
    
    # Training job stats
    pending_jobs = await db.execute(
        select(func.count(TrainingJob.id)).where(TrainingJob.status == "pending")
    )
    pending_jobs = pending_jobs.scalar() or 0
    
    running_jobs = await db.execute(
        select(func.count(TrainingJob.id)).where(TrainingJob.status == "running")
    )
    running_jobs = running_jobs.scalar() or 0
    
    return {
        "tasks": {
            "total": task_count,
            "escalated": escalated_count
        },
        "agents": {
            "total": agent_count,
            "available": available_agents
        },
        "models": {
            "total": model_count,
            "active": active_models
        },
        "training_jobs": {
            "pending": pending_jobs,
            "running": running_jobs
        }
    }
