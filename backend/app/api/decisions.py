"""Decision and task management API endpoints."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import TaskState, AgentType
from app.db.crud import TaskCRUD, EventCRUD, AuditCRUD
from app.api.auth import get_current_user, require_any_role, User
from app.core import Role
from app.agents.delegation import DelegationAgent
from app.agents.decision import DecisionAgent, DecisionOverride

router = APIRouter(prefix="/decisions", tags=["decisions"])


class TaskCreate(BaseModel):
    """Task creation request."""
    task_type: str
    input_data: dict
    priority: int = 0
    max_retries: int = 3
    agent_type: str = "decision"


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: int
    task_type: str
    state: str
    priority: int
    assigned_agent_id: Optional[int]
    retry_count: int
    created_at: str
    
    class Config:
        from_attributes = True


class DecisionOverrideRequest(BaseModel):
    """Decision override request."""
    task_id: int
    override_decision: dict
    reason: str


class EscalateRequest(BaseModel):
    """Task escalation request."""
    task_id: int
    reason: str


@router.post("/task", response_model=TaskResponse)
async def create_task(
    request: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task and initiate the ack/retry flow.
    """
    # Create task in database
    task = await TaskCRUD.create_task(
        db,
        task_type=request.task_type,
        input_data=request.input_data,
        priority=request.priority,
        max_retries=request.max_retries
    )
    
    # Log event
    await EventCRUD.create_event(
        db,
        event_type="task_created",
        event_data={
            "task_id": task.id,
            "task_type": request.task_type,
            "priority": request.priority
        },
        task_id=task.id,
        user_id=current_user.user_id
    )
    
    # Audit log
    await AuditCRUD.create_audit(
        db,
        action="task_created",
        user_id=current_user.user_id,
        user_role=current_user.roles[0] if current_user.roles else "viewer",
        task_id=task.id,
        details={"task_type": request.task_type}
    )
    
    # Assign task via delegation agent
    delegation_agent = DelegationAgent()
    agent_type = AgentType(request.agent_type)
    
    # Start assignment in background (in production, this would be async task)
    # For now, we'll just mark it as queued
    
    return TaskResponse(
        task_id=task.id,
        task_type=task.task_type,
        state=task.state.value,
        priority=task.priority,
        assigned_agent_id=task.assigned_agent_id,
        retry_count=task.retry_count,
        created_at=task.created_at.isoformat()
    )


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get task details."""
    task = await TaskCRUD.get_task(db, task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        task_id=task.id,
        task_type=task.task_type,
        state=task.state.value,
        priority=task.priority,
        assigned_agent_id=task.assigned_agent_id,
        retry_count=task.retry_count,
        created_at=task.created_at.isoformat()
    )


@router.post("/override")
async def override_decision(
    request: DecisionOverrideRequest,
    current_user: User = Depends(require_any_role(Role.ADMIN, Role.REVIEWER)),
    db: AsyncSession = Depends(get_db)
):
    """
    Override an agent decision (requires admin or reviewer role).
    """
    # Get task
    task = await TaskCRUD.get_task(db, request.task_id)
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create override
    override = await DecisionOverride.override_decision(
        task_id=request.task_id,
        original_decision=task.output_data or {},
        override_decision=request.override_decision,
        user_id=current_user.user_id,
        reason=request.reason
    )
    
    # Update task with override
    await TaskCRUD.update_task_state(
        db,
        request.task_id,
        TaskState.COMPLETED,
        output_data=request.override_decision
    )
    
    # Log event
    await EventCRUD.create_event(
        db,
        event_type="decision_overridden",
        event_data=override,
        task_id=request.task_id,
        user_id=current_user.user_id
    )
    
    # Audit log
    await AuditCRUD.create_audit(
        db,
        action="decision_override",
        user_id=current_user.user_id,
        user_role=current_user.roles[0],
        task_id=request.task_id,
        details={"reason": request.reason}
    )
    
    return {"success": True, "override": override}


@router.post("/escalate")
async def escalate_task(
    request: EscalateRequest,
    current_user: User = Depends(require_any_role(Role.ADMIN, Role.REVIEWER, Role.AGENT_MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually escalate a task (requires appropriate role).
    """
    delegation_agent = DelegationAgent()
    result = await delegation_agent.escalate_task(
        db,
        request.task_id,
        f"Manual escalation by {current_user.user_id}: {request.reason}"
    )
    
    # Audit log
    await AuditCRUD.create_audit(
        db,
        action="task_escalated",
        user_id=current_user.user_id,
        user_role=current_user.roles[0],
        task_id=request.task_id,
        details={"reason": request.reason}
    )
    
    return result


@router.get("/tasks")
async def list_tasks(
    state: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List tasks with optional filtering."""
    # This would need proper pagination in production
    # For now, return a placeholder
    return {
        "tasks": [],
        "total": 0,
        "limit": limit
    }
