"""CRUD operations for database models."""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime

from app.db.models import Event, Task, Agent, Audit, Feedback, Model, TaskState, AgentType


class EventCRUD:
    """CRUD operations for events."""
    
    @staticmethod
    async def create_event(
        db: AsyncSession,
        event_type: str,
        event_data: dict,
        task_id: Optional[int] = None,
        agent_id: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> Event:
        """Create a new event."""
        event = Event(
            event_type=event_type,
            event_data=event_data,
            task_id=task_id,
            agent_id=agent_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event
    
    @staticmethod
    async def get_events_by_task(db: AsyncSession, task_id: int) -> List[Event]:
        """Get all events for a task."""
        result = await db.execute(
            select(Event).where(Event.task_id == task_id).order_by(Event.timestamp)
        )
        return result.scalars().all()


class TaskCRUD:
    """CRUD operations for tasks."""
    
    @staticmethod
    async def create_task(
        db: AsyncSession,
        task_type: str,
        input_data: dict,
        priority: int = 0,
        max_retries: int = 3,
        ack_timeout_seconds: int = 30,
        task_timeout_seconds: int = 300,
    ) -> Task:
        """Create a new task."""
        task = Task(
            task_type=task_type,
            state=TaskState.QUEUED,
            input_data=input_data,
            priority=priority,
            max_retries=max_retries,
            ack_timeout_seconds=ack_timeout_seconds,
            task_timeout_seconds=task_timeout_seconds,
            created_at=datetime.utcnow(),
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    @staticmethod
    async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        result = await db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_task_state(
        db: AsyncSession,
        task_id: int,
        new_state: TaskState,
        **kwargs
    ) -> Optional[Task]:
        """Update task state and related fields."""
        update_data = {"state": new_state}
        
        # Add timestamp fields based on state
        if new_state == TaskState.ASSIGNED:
            update_data["assigned_at"] = datetime.utcnow()
        elif new_state == TaskState.ACKED:
            update_data["acked_at"] = datetime.utcnow()
        elif new_state == TaskState.IN_PROGRESS:
            update_data["started_at"] = datetime.utcnow()
        elif new_state in [TaskState.COMPLETED, TaskState.VERIFIED, TaskState.FAILED]:
            update_data["completed_at"] = datetime.utcnow()
        elif new_state == TaskState.ESCALATED:
            update_data["escalated_at"] = datetime.utcnow()
        
        # Add any additional fields
        update_data.update(kwargs)
        
        await db.execute(
            update(Task).where(Task.id == task_id).values(**update_data)
        )
        await db.commit()
        return await TaskCRUD.get_task(db, task_id)
    
    @staticmethod
    async def increment_retry_count(db: AsyncSession, task_id: int) -> Optional[Task]:
        """Increment retry count for a task."""
        task = await TaskCRUD.get_task(db, task_id)
        if task:
            await db.execute(
                update(Task)
                .where(Task.id == task_id)
                .values(retry_count=task.retry_count + 1)
            )
            await db.commit()
            return await TaskCRUD.get_task(db, task_id)
        return None


class AgentCRUD:
    """CRUD operations for agents."""
    
    @staticmethod
    async def create_agent(
        db: AsyncSession,
        agent_type: AgentType,
        name: str,
        version: str,
        config: Optional[dict] = None,
        max_load: int = 10,
    ) -> Agent:
        """Create a new agent."""
        agent = Agent(
            agent_type=agent_type,
            name=name,
            version=version,
            config=config,
            max_load=max_load,
            is_active=1,
            current_load=0,
            created_at=datetime.utcnow(),
        )
        db.add(agent)
        await db.commit()
        await db.refresh(agent)
        return agent
    
    @staticmethod
    async def get_agent(db: AsyncSession, agent_id: int) -> Optional[Agent]:
        """Get an agent by ID."""
        result = await db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_available_agents(
        db: AsyncSession, agent_type: AgentType
    ) -> List[Agent]:
        """Get available agents of a specific type."""
        result = await db.execute(
            select(Agent)
            .where(Agent.agent_type == agent_type)
            .where(Agent.is_active == 1)
            .where(Agent.current_load < Agent.max_load)
            .order_by(Agent.current_load)
        )
        return result.scalars().all()


class AuditCRUD:
    """CRUD operations for audits."""
    
    @staticmethod
    async def create_audit(
        db: AsyncSession,
        action: str,
        user_id: str,
        user_role: str,
        task_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
    ) -> Audit:
        """Create a new audit log entry."""
        audit = Audit(
            action=action,
            user_id=user_id,
            user_role=user_role,
            task_id=task_id,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
        )
        db.add(audit)
        await db.commit()
        await db.refresh(audit)
        return audit


class FeedbackCRUD:
    """CRUD operations for feedback."""
    
    @staticmethod
    async def create_feedback(
        db: AsyncSession,
        task_id: int,
        user_id: str,
        feedback_type: str,
        rating: Optional[int] = None,
        feedback_text: Optional[str] = None,
        feedback_data: Optional[dict] = None,
    ) -> Feedback:
        """Create new feedback."""
        feedback = Feedback(
            task_id=task_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            feedback_text=feedback_text,
            feedback_data=feedback_data,
            timestamp=datetime.utcnow(),
        )
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return feedback
    
    @staticmethod
    async def get_unused_feedback(db: AsyncSession, limit: int = 100) -> List[Feedback]:
        """Get feedback not yet used for training."""
        result = await db.execute(
            select(Feedback)
            .where(Feedback.used_for_training == 0)
            .limit(limit)
        )
        return result.scalars().all()


class ModelCRUD:
    """CRUD operations for models."""
    
    @staticmethod
    async def create_model(
        db: AsyncSession,
        name: str,
        version: str,
        agent_type: AgentType,
        training_job_id: str,
        model_path: Optional[str] = None,
        model_url: Optional[str] = None,
        metrics: Optional[dict] = None,
    ) -> Model:
        """Create a new model entry."""
        model = Model(
            name=name,
            version=version,
            agent_type=agent_type,
            training_job_id=training_job_id,
            model_path=model_path,
            model_url=model_url,
            metrics=metrics,
            training_completed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
        )
        db.add(model)
        await db.commit()
        await db.refresh(model)
        return model
    
    @staticmethod
    async def get_latest_model(
        db: AsyncSession, agent_type: AgentType
    ) -> Optional[Model]:
        """Get the latest active model for an agent type."""
        result = await db.execute(
            select(Model)
            .where(Model.agent_type == agent_type)
            .where(Model.is_active == 1)
            .order_by(Model.created_at.desc())
        )
        return result.scalar_one_or_none()
