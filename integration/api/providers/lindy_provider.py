"""
lindy.ai Provider Adapter

Integrates with lindy.ai AI agent platform.
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LindyProvider:
    """Provider adapter for lindy.ai API."""
    
    def __init__(self):
        self.api_key = os.getenv("LINDY_AI_API_KEY", "TODO_ADD_LINDY_API_KEY")
        self.base_url = os.getenv("LINDY_AI_BASE_URL", "https://api.lindy.ai/v1")
        self.timeout = 60.0  # Longer timeout for AI tasks
        
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "RAG7-Integration/1.0"
        }
    
    async def create_agent_task(
        self,
        agent_id: str,
        task: Dict[str, Any],
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Create a new agent task.
        
        Args:
            agent_id: ID of the agent to use
            task: Task definition with type, query, and context
            stream: Whether to stream results
            
        Returns:
            Task creation result with task_id
        """
        logger.info(f"Creating lindy.ai agent task: agent={agent_id}, type={task.get('type')}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/agents/{agent_id}/tasks",
                    headers=self._get_headers(),
                    json={
                        "task": task,
                        "stream": stream
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(
                    f"lindy.ai task created: agent={agent_id}, "
                    f"task_id={result.get('task_id')}"
                )
                return result
                
            except httpx.HTTPError as e:
                logger.error(f"lindy.ai API error: {e}")
                raise Exception(f"lindy.ai API request failed: {str(e)}")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of an agent task.
        
        Args:
            task_id: Task ID returned from create_agent_task
            
        Returns:
            Task status and results
        """
        logger.info(f"Getting lindy.ai task status: {task_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"lindy.ai API error: {e}")
                raise Exception(f"Failed to get task status: {str(e)}")
    
    async def list_agents(self) -> Dict[str, Any]:
        """
        List available AI agents.
        
        Returns:
            List of available agents
        """
        logger.info("Listing lindy.ai agents")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/agents",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"lindy.ai API error: {e}")
                raise Exception(f"Failed to list agents: {str(e)}")
    
    async def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a running task.
        
        Args:
            task_id: Task ID to cancel
            
        Returns:
            Cancellation result
        """
        logger.info(f"Cancelling lindy.ai task: {task_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/tasks/{task_id}/cancel",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"lindy.ai API error: {e}")
                raise Exception(f"Failed to cancel task: {str(e)}")
    
    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get the final result of a completed task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result with findings, sources, etc.
        """
        logger.info(f"Getting lindy.ai task result: {task_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/tasks/{task_id}/result",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"lindy.ai API error: {e}")
                raise Exception(f"Failed to get task result: {str(e)}")


# Global instance
lindy_provider = LindyProvider()
