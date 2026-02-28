"""Decisions API for task management and agent orchestration."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_active_user, require_role, Role, User
from app.db.session import get_db
from app.db import crud
from app.agents.communication import TaskState


router = APIRouter()


class TaskCreate(BaseModel):
    """Task creation request."""
    title: str
    description: Optional[str] = None
    task_type: str = "default"
    priority: str = "medium"
    payload: dict = {}
    assigned_agent_id: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response model."""
    id: str
    title: str
    description: Optional[str]
    task_type: str
    priority: str
    state: str
    payload: dict
    assigned_agent_id: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: datetime


class TaskStateUpdate(BaseModel):
    """Task state update request."""
    state: TaskState
    metadata: Optional[dict] = None


class DecisionOverride(BaseModel):
    """Human decision override request."""
    reason: str
    new_decision: str
    metadata: Optional[dict] = None


@router.post("/task", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """
    Create a new task and publish to agent orchestration.
    
    This endpoint:
    1. Persists the task to the database
    2. Creates an initial task event
    3. Publishes the task to Redis for agent assignment
    4. Returns the created task
    """
    task_id = str(uuid.uuid4())
    
    # Create task in database
    db_task = await crud.create_task(
        db=db,
        task_id=task_id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority,
        payload=task.payload,
        assigned_agent_id=task.assigned_agent_id
    )
    
    # Create initial event
    await crud.create_event(
        db=db,
        event_type="task_created",
        entity_type="task",
        entity_id=task_id,
        data={
            "title": task.title,
            "task_type": task.task_type,
            "priority": task.priority
        },
        user_id=current_user.id
    )
    
    # Schedule background task for Redis publication
    # In a full implementation, this would use the AgentCommunicationSystem
    
    return TaskResponse(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        task_type=db_task.task_type,
        priority=db_task.priority,
        state=db_task.state,
        payload=db_task.payload,
        assigned_agent_id=db_task.assigned_agent_id,
        retry_count=db_task.retry_count,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task by ID."""
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority,
        state=task.state,
        payload=task.payload,
        assigned_agent_id=task.assigned_agent_id,
        retry_count=task.retry_count,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.get("/tasks")
async def list_tasks(
    state: Optional[TaskState] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List tasks with optional state filter."""
    tasks = await crud.get_tasks(
        db=db,
        state=state.value if state else None,
        limit=limit,
        offset=offset
    )
    
    return {
        "tasks": [
            TaskResponse(
                id=t.id,
                title=t.title,
                description=t.description,
                task_type=t.task_type,
                priority=t.priority,
                state=t.state,
                payload=t.payload,
                assigned_agent_id=t.assigned_agent_id,
                retry_count=t.retry_count,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in tasks
        ],
        "limit": limit,
        "offset": offset
    }


@router.patch("/task/{task_id}/state")
async def update_task_state(
    task_id: str,
    state_update: TaskStateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.ADMIN))
):
    """Update task state and create state change event."""
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    old_state = task.state
    
    # Update task state
    updated_task = await crud.update_task_state(
        db=db,
        task_id=task_id,
        state=state_update.state.value
    )
    
    # Create state change event
    await crud.create_event(
        db=db,
        event_type="task_state_changed",
        entity_type="task",
        entity_id=task_id,
        data={
            "old_state": old_state,
            "new_state": state_update.state.value,
            "metadata": state_update.metadata
        },
        user_id=current_user.id
    )
    
    return {"status": "updated", "new_state": state_update.state.value}


@router.post("/task/{task_id}/override")
async def override_decision(
    task_id: str,
    override: DecisionOverride,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.REVIEWER, Role.ADMIN))
):
    """
    Override an agent decision (human in the loop).
    
    Only reviewers and admins can override decisions.
    """
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create override event
    await crud.create_event(
        db=db,
        event_type="decision_override",
        entity_type="task",
        entity_id=task_id,
        data={
            "reason": override.reason,
            "new_decision": override.new_decision,
            "metadata": override.metadata,
            "overridden_by": current_user.id
        },
        user_id=current_user.id
    )
    
    # Create audit record
    await crud.create_audit(
        db=db,
        action="decision_override",
        entity_type="task",
        entity_id=task_id,
        user_id=current_user.id,
        details={
            "reason": override.reason,
            "new_decision": override.new_decision
        }
    )
    
    return {
        "status": "overridden",
        "task_id": task_id,
        "new_decision": override.new_decision
    }


@router.post("/task/{task_id}/escalate")
async def escalate_task(
    task_id: str,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.AGENT_MANAGER, Role.REVIEWER, Role.ADMIN))
):
    """
    Escalate a task to higher priority or human review.
    """
    task = await crud.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Update task state to escalated
    await crud.update_task_state(db, task_id, TaskState.ESCALATED.value)
    
    # Create escalation event
    await crud.create_event(
        db=db,
        event_type="task_escalated",
        entity_type="task",
        entity_id=task_id,
        data={
            "reason": reason,
            "escalated_by": current_user.id,
            "previous_state": task.state
        },
        user_id=current_user.id
    )
    
    return {
        "status": "escalated",
        "task_id": task_id,
        "reason": reason
    }


@router.get("/events")
async def get_events(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get events with optional filters."""
    events = await crud.get_events(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit
    )
    
    return {
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "entity_type": e.entity_type,
                "entity_id": e.entity_id,
                "data": e.data,
                "user_id": e.user_id,
                "created_at": e.created_at
            }
            for e in events
        ]
    }


@router.get("/escalations")
async def get_escalations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(Role.REVIEWER, Role.ADMIN))
):
    """Get all escalated tasks for review."""
    tasks = await crud.get_tasks(db, state=TaskState.ESCALATED.value)
    
    return {
        "escalations": [
            TaskResponse(
                id=t.id,
                title=t.title,
                description=t.description,
                task_type=t.task_type,
                priority=t.priority,
                state=t.state,
                payload=t.payload,
                assigned_agent_id=t.assigned_agent_id,
                retry_count=t.retry_count,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in tasks
        ]
    }
