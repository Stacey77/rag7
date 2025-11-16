"""Task delegation agent module."""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
import math

from app.db.models import TaskState, AgentType
from app.db.crud import TaskCRUD, AgentCRUD, EventCRUD
from app.agents.communication import CommunicationAgent
from app.core import TaskConfig


class DelegationAgent:
    """Handles task assignment and retry logic with ack protocol."""
    
    def __init__(self):
        self.communication = CommunicationAgent()
    
    async def assign_task(
        self,
        db,
        task_id: int,
        agent_type: AgentType
    ) -> Optional[Dict[str, Any]]:
        """Assign a task to an available agent with ack protocol."""
        # Get available agents
        agents = await AgentCRUD.get_available_agents(db, agent_type)
        
        if not agents:
            return {
                "success": False,
                "error": "No available agents",
                "task_id": task_id
            }
        
        # Select agent (simple round-robin for now)
        selected_agent = agents[0]
        
        # Update task state to assigned
        task = await TaskCRUD.update_task_state(
            db,
            task_id,
            TaskState.ASSIGNED,
            assigned_agent_id=selected_agent.id
        )
        
        # Log event
        await EventCRUD.create_event(
            db,
            event_type="task_assigned",
            event_data={
                "task_id": task_id,
                "agent_id": selected_agent.id,
                "agent_type": agent_type.value
            },
            task_id=task_id,
            agent_id=selected_agent.id
        )
        
        # Publish task via communication agent
        await self.communication.publish_task(task_id, {
            "task_id": task_id,
            "agent_id": selected_agent.id,
            "task_type": task.task_type,
            "input_data": task.input_data
        })
        
        # Wait for acknowledgement
        ack = await self.communication.wait_for_ack(
            task_id,
            timeout=task.ack_timeout_seconds
        )
        
        if ack and ack.get("accepted"):
            # Update task state to acked
            await TaskCRUD.update_task_state(db, task_id, TaskState.ACKED)
            await EventCRUD.create_event(
                db,
                event_type="task_acked",
                event_data={
                    "task_id": task_id,
                    "agent_id": selected_agent.id
                },
                task_id=task_id,
                agent_id=selected_agent.id
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "agent_id": selected_agent.id,
                "acked": True
            }
        else:
            # No ack received - handle retry
            return await self.handle_no_ack(db, task_id, selected_agent.id)
    
    async def handle_no_ack(
        self,
        db,
        task_id: int,
        agent_id: int
    ) -> Dict[str, Any]:
        """Handle no acknowledgement - retry or escalate."""
        task = await TaskCRUD.get_task(db, task_id)
        
        if not task:
            return {"success": False, "error": "Task not found"}
        
        # Increment retry count
        await TaskCRUD.increment_retry_count(db, task_id)
        task = await TaskCRUD.get_task(db, task_id)
        
        # Log event
        await EventCRUD.create_event(
            db,
            event_type="task_no_ack",
            event_data={
                "task_id": task_id,
                "agent_id": agent_id,
                "retry_count": task.retry_count
            },
            task_id=task_id,
            agent_id=agent_id
        )
        
        if task.retry_count >= task.max_retries:
            # Escalate
            return await self.escalate_task(db, task_id, "max_retries_exceeded")
        else:
            # Retry with backoff
            backoff_seconds = self.calculate_backoff(task.retry_count)
            await asyncio.sleep(backoff_seconds)
            
            # Reset to queued state for retry
            await TaskCRUD.update_task_state(db, task_id, TaskState.QUEUED)
            
            return {
                "success": False,
                "retry": True,
                "task_id": task_id,
                "retry_count": task.retry_count,
                "backoff_seconds": backoff_seconds
            }
    
    async def escalate_task(
        self,
        db,
        task_id: int,
        reason: str
    ) -> Dict[str, Any]:
        """Escalate a task to human review."""
        # Update task state to escalated
        await TaskCRUD.update_task_state(
            db,
            task_id,
            TaskState.ESCALATED,
            error_message=f"Escalated: {reason}"
        )
        
        # Log event
        await EventCRUD.create_event(
            db,
            event_type="task_escalated",
            event_data={
                "task_id": task_id,
                "reason": reason
            },
            task_id=task_id
        )
        
        # Notify oversight
        await self.communication.notify_oversight(
            "task_escalated",
            {
                "task_id": task_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "success": False,
            "escalated": True,
            "task_id": task_id,
            "reason": reason
        }
    
    @staticmethod
    def calculate_backoff(retry_count: int) -> int:
        """Calculate exponential backoff time."""
        backoff = TaskConfig.RETRY_BACKOFF_BASE ** retry_count
        return min(backoff, TaskConfig.RETRY_BACKOFF_MAX)
