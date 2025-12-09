"""
kiro.ai Provider Adapter

Integrates with kiro.ai automation platform.
"""

import os
import httpx
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class KiroProvider:
    """Provider adapter for kiro.ai API."""
    
    def __init__(self):
        self.api_key = os.getenv("KIRO_AI_API_KEY", "TODO_ADD_KIRO_API_KEY")
        self.base_url = os.getenv("KIRO_AI_BASE_URL", "https://api.kiro.ai/v1")
        self.timeout = 30.0
        
    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "RAG7-Integration/1.0"
        }
    
    async def execute_automation(
        self,
        automation_id: str,
        parameters: Dict[str, Any],
        wait_for_completion: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a kiro.ai automation.
        
        Args:
            automation_id: ID of the automation to execute
            parameters: Parameters to pass to the automation
            wait_for_completion: Whether to wait for completion (sync)
            
        Returns:
            Execution result or job info
        """
        logger.info(f"Executing kiro.ai automation: {automation_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/automations/{automation_id}/execute",
                    headers=self._get_headers(),
                    json={
                        "parameters": parameters,
                        "wait_for_completion": wait_for_completion
                    }
                )
                response.raise_for_status()
                result = response.json()
                
                logger.info(
                    f"kiro.ai automation executed: {automation_id}, "
                    f"status={result.get('status')}"
                )
                return result
                
            except httpx.HTTPError as e:
                logger.error(f"kiro.ai API error: {e}")
                raise Exception(f"kiro.ai API request failed: {str(e)}")
    
    async def get_automation_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of an automation execution.
        
        Args:
            job_id: Job ID returned from execute_automation
            
        Returns:
            Job status and results
        """
        logger.info(f"Getting kiro.ai job status: {job_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/jobs/{job_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"kiro.ai API error: {e}")
                raise Exception(f"Failed to get job status: {str(e)}")
    
    async def list_automations(self) -> Dict[str, Any]:
        """
        List available automations.
        
        Returns:
            List of available automations
        """
        logger.info("Listing kiro.ai automations")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/automations",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"kiro.ai API error: {e}")
                raise Exception(f"Failed to list automations: {str(e)}")
    
    async def cancel_automation(self, job_id: str) -> Dict[str, Any]:
        """
        Cancel a running automation.
        
        Args:
            job_id: Job ID to cancel
            
        Returns:
            Cancellation result
        """
        logger.info(f"Cancelling kiro.ai job: {job_id}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/jobs/{job_id}/cancel",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                logger.error(f"kiro.ai API error: {e}")
                raise Exception(f"Failed to cancel job: {str(e)}")


# Global instance
kiro_provider = KiroProvider()
