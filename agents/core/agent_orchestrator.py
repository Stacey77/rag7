"""
Agent Orchestrator - Coordinates all agents in the platform
"""
import asyncio
import logging
from typing import Dict, List, Optional
from .base_agent import BaseAgent, Message

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Singleton orchestrator for managing all agents"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if AgentOrchestrator._instance is not None:
            raise Exception("AgentOrchestrator is a singleton!")
        
        self.agents: Dict[str, BaseAgent] = {}
        self.running_tasks: List[asyncio.Task] = []
        self.logger = logging.getLogger("orchestrator")
        AgentOrchestrator._instance = self
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the orchestrator"""
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_id}")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    async def route_message(self, message: Message):
        """Route message to target agent"""
        if message.receiver not in self.agents:
            self.logger.error(f"Target agent not found: {message.receiver}")
            return
        
        target_agent = self.agents[message.receiver]
        await target_agent.receive_message(message)
        self.logger.debug(
            f"Routed message from {message.sender} to {message.receiver}"
        )
    
    async def broadcast_message(self, message: Message, exclude: Optional[List[str]] = None):
        """Broadcast message to all agents except excluded ones"""
        exclude = exclude or []
        for agent_id, agent in self.agents.items():
            if agent_id not in exclude:
                modified_message = Message(
                    sender=message.sender,
                    receiver=agent_id,
                    message_type=message.message_type,
                    payload=message.payload,
                    correlation_id=message.correlation_id
                )
                await agent.receive_message(modified_message)
    
    async def start_all_agents(self):
        """Start all registered agents"""
        self.logger.info("Starting all agents...")
        
        for agent_id, agent in self.agents.items():
            task = asyncio.create_task(agent.start())
            self.running_tasks.append(task)
            self.logger.info(f"Started agent: {agent_id}")
    
    async def stop_all_agents(self):
        """Stop all running agents"""
        self.logger.info("Stopping all agents...")
        
        # Stop all agents
        for agent in self.agents.values():
            await agent.stop()
        
        # Wait for all tasks to complete
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks, return_exceptions=True)
            self.running_tasks.clear()
        
        self.logger.info("All agents stopped")
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict]:
        """Get status of specific agent"""
        if agent_id in self.agents:
            return self.agents[agent_id].get_status()
        return None
    
    def get_all_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    async def execute_workflow(self, workflow_name: str, params: Dict) -> Dict:
        """Execute a predefined workflow across multiple agents"""
        self.logger.info(f"Executing workflow: {workflow_name}")
        
        # Example workflow coordination
        results = {
            "workflow": workflow_name,
            "status": "initiated",
            "steps": []
        }
        
        return results
