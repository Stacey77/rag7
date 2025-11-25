"""Agent Delegation System for task routing and load balancing."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import redis.asyncio as redis

from app.agents.communication import AgentCommunicationSystem, TaskState


class AgentCapability(str, Enum):
    """Agent capabilities for task routing."""
    TEXT_PROCESSING = "text_processing"
    CODE_ANALYSIS = "code_analysis"
    DATA_EXTRACTION = "data_extraction"
    DECISION_MAKING = "decision_making"
    HUMAN_INTERACTION = "human_interaction"
    ML_INFERENCE = "ml_inference"


class AgentStatus(str, Enum):
    """Agent operational status."""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class AgentProfile:
    """Profile describing an agent's capabilities and status."""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        capabilities: List[AgentCapability],
        max_concurrent_tasks: int = 5,
        priority_level: int = 1,
        status: AgentStatus = AgentStatus.AVAILABLE
    ):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.max_concurrent_tasks = max_concurrent_tasks
        self.priority_level = priority_level
        self.status = status
        self.current_tasks: List[str] = []
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_completion_time": 0.0
        }
    
    @property
    def is_available(self) -> bool:
        return (
            self.status == AgentStatus.AVAILABLE and
            len(self.current_tasks) < self.max_concurrent_tasks
        )
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": [c.value for c in self.capabilities],
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "priority_level": self.priority_level,
            "status": self.status.value,
            "current_tasks": self.current_tasks,
            "metrics": self.metrics
        }


class DelegationStrategy(str, Enum):
    """Task delegation strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    CAPABILITY_MATCH = "capability_match"
    PRIORITY_BASED = "priority_based"


class AgentDelegationSystem:
    """
    Delegation system for routing tasks to appropriate agents.
    
    Features:
    - Register and track agent profiles
    - Route tasks based on capabilities and load
    - Support multiple delegation strategies
    - Track task assignments
    """
    
    def __init__(
        self,
        communication_system: AgentCommunicationSystem,
        strategy: DelegationStrategy = DelegationStrategy.CAPABILITY_MATCH
    ):
        self.comm_system = communication_system
        self.strategy = strategy
        self.agents: Dict[str, AgentProfile] = {}
        self._round_robin_index = 0
    
    def register_agent(self, profile: AgentProfile) -> None:
        """Register an agent with the delegation system."""
        self.agents[profile.agent_id] = profile
    
    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent from the delegation system."""
        if agent_id in self.agents:
            del self.agents[agent_id]
    
    def update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update an agent's status."""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
    
    async def delegate_task(
        self,
        task_id: str,
        payload: dict,
        required_capabilities: Optional[List[AgentCapability]] = None
    ) -> Optional[str]:
        """
        Delegate a task to an appropriate agent.
        
        Returns:
            Agent ID if delegation successful, None otherwise
        """
        # Find suitable agents
        candidates = self._find_suitable_agents(required_capabilities)
        
        if not candidates:
            return None
        
        # Select agent based on strategy
        selected_agent = self._select_agent(candidates)
        
        if not selected_agent:
            return None
        
        # Assign task to agent
        selected_agent.current_tasks.append(task_id)
        
        # Publish task with recipient
        success, ack_data, retry_count = await self.comm_system.publish_task(
            task_id=task_id,
            payload=payload,
            recipient_id=selected_agent.agent_id
        )
        
        if success:
            return selected_agent.agent_id
        else:
            # Remove task from agent if not acked
            if task_id in selected_agent.current_tasks:
                selected_agent.current_tasks.remove(task_id)
            return None
    
    def _find_suitable_agents(
        self,
        required_capabilities: Optional[List[AgentCapability]]
    ) -> List[AgentProfile]:
        """Find agents that can handle the task."""
        candidates = []
        
        for agent in self.agents.values():
            if not agent.is_available:
                continue
            
            if required_capabilities:
                # Check if agent has all required capabilities
                if all(cap in agent.capabilities for cap in required_capabilities):
                    candidates.append(agent)
            else:
                candidates.append(agent)
        
        return candidates
    
    def _select_agent(
        self,
        candidates: List[AgentProfile]
    ) -> Optional[AgentProfile]:
        """Select an agent based on the delegation strategy."""
        if not candidates:
            return None
        
        if self.strategy == DelegationStrategy.ROUND_ROBIN:
            self._round_robin_index = (self._round_robin_index + 1) % len(candidates)
            return candidates[self._round_robin_index]
        
        elif self.strategy == DelegationStrategy.LEAST_LOADED:
            return min(candidates, key=lambda a: len(a.current_tasks))
        
        elif self.strategy == DelegationStrategy.PRIORITY_BASED:
            return max(candidates, key=lambda a: a.priority_level)
        
        else:  # CAPABILITY_MATCH - default to first match
            return candidates[0]
    
    def complete_task(self, agent_id: str, task_id: str, success: bool = True) -> None:
        """Mark a task as completed by an agent."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if task_id in agent.current_tasks:
                agent.current_tasks.remove(task_id)
            
            if success:
                agent.metrics["tasks_completed"] += 1
            else:
                agent.metrics["tasks_failed"] += 1
    
    def get_agent_workload(self) -> Dict[str, dict]:
        """Get current workload for all agents."""
        return {
            agent_id: {
                "current_tasks": len(profile.current_tasks),
                "max_tasks": profile.max_concurrent_tasks,
                "status": profile.status.value,
                "utilization": len(profile.current_tasks) / profile.max_concurrent_tasks
            }
            for agent_id, profile in self.agents.items()
        }
    
    def get_all_agents(self) -> List[dict]:
        """Get all registered agents."""
        return [agent.to_dict() for agent in self.agents.values()]
