"""
Integration Routes

API routes for provider integrations (kiro.ai, lindy.ai).
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from providers.kiro_provider import kiro_provider
from providers.lindy_provider import lindy_provider

router = APIRouter()


# Request/Response Models
class KiroExecuteRequest(BaseModel):
    automation_id: str
    parameters: Dict[str, Any]
    wait_for_completion: bool = False


class LindyTaskRequest(BaseModel):
    agent_id: str
    task: Dict[str, Any]
    stream: bool = False


# kiro.ai endpoints
@router.post("/kiro/execute")
async def execute_kiro_automation(request: KiroExecuteRequest):
    """
    Execute a kiro.ai automation.
    
    Example:
    ```bash
    curl -X POST http://localhost:8000/v1/integrations/kiro/execute \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer YOUR_API_KEY" \\
      -d '{
        "automation_id": "auto_123",
        "parameters": {"input": "data"},
        "wait_for_completion": false
      }'
    ```
    """
    try:
        result = await kiro_provider.execute_automation(
            automation_id=request.automation_id,
            parameters=request.parameters,
            wait_for_completion=request.wait_for_completion
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kiro/status/{job_id}")
async def get_kiro_job_status(job_id: str):
    """
    Get the status of a kiro.ai automation job.
    
    Example:
    ```bash
    curl http://localhost:8000/v1/integrations/kiro/status/job_456 \\
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
    """
    try:
        result = await kiro_provider.get_automation_status(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kiro/automations")
async def list_kiro_automations():
    """
    List available kiro.ai automations.
    
    Example:
    ```bash
    curl http://localhost:8000/v1/integrations/kiro/automations \\
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
    """
    try:
        result = await kiro_provider.list_automations()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kiro/cancel/{job_id}")
async def cancel_kiro_job(job_id: str):
    """
    Cancel a running kiro.ai automation job.
    
    Example:
    ```bash
    curl -X POST http://localhost:8000/v1/integrations/kiro/cancel/job_456 \\
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
    """
    try:
        result = await kiro_provider.cancel_automation(job_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# lindy.ai endpoints
@router.post("/lindy/tasks")
async def create_lindy_task(request: LindyTaskRequest):
    """
    Create a new lindy.ai agent task.
    
    Example:
    ```bash
    curl -X POST http://localhost:8000/v1/integrations/lindy/tasks \\
      -H "Content-Type: application/json" \\
      -H "Authorization: Bearer YOUR_API_KEY" \\
      -d '{
        "agent_id": "agent_789",
        "task": {
          "type": "research",
          "query": "Find information about topic X",
          "max_duration_minutes": 5
        }
      }'
    ```
    """
    try:
        result = await lindy_provider.create_agent_task(
            agent_id=request.agent_id,
            task=request.task,
            stream=request.stream
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lindy/tasks/{task_id}")
async def get_lindy_task_status(task_id: str):
    """
    Get the status of a lindy.ai agent task.
    
    Example:
    ```bash
    curl http://localhost:8000/v1/integrations/lindy/tasks/task_123 \\
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
    """
    try:
        result = await lindy_provider.get_task_status(task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lindy/tasks/{task_id}/result")
async def get_lindy_task_result(task_id: str):
    """
    Get the result of a completed lindy.ai task.
    
    Example:
    ```bash
    curl http://localhost:8000/v1/integrations/lindy/tasks/task_123/result \\
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
    """
    try:
        result = await lindy_provider.get_task_result(task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lindy/agents")
async def list_lindy_agents():
    """
    List available lindy.ai agents.
    
    Example:
    ```bash
    curl http://localhost:8000/v1/integrations/lindy/agents \\
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
    """
    try:
        result = await lindy_provider.list_agents()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lindy/tasks/{task_id}/cancel")
async def cancel_lindy_task(task_id: str):
    """
    Cancel a running lindy.ai task.
    
    Example:
    ```bash
    curl -X POST http://localhost:8000/v1/integrations/lindy/tasks/task_123/cancel \\
      -H "Authorization: Bearer YOUR_API_KEY"
    ```
    """
    try:
        result = await lindy_provider.cancel_task(task_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
