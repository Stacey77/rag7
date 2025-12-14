"""Base agent class for ADK multi-agent system."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import uuid4

from ..llm import TaskComplexity, client, router
from ..observability import get_logger
from ..observability.metrics import agent_tasks_total, agent_task_duration_seconds, active_agents
from ..observability.tracing import trace_agent_conversation
import time

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str, description: str = ""):
        """Initialize agent.
        
        Args:
            name: Agent name
            description: Agent description
        """
        self.name = name
        self.description = description
        self.agent_id = str(uuid4())
        self.llm_client = client
        self.model_router = router
        active_agents.labels(agent_type=self.__class__.__name__).inc()

    @abstractmethod
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task.
        
        Args:
            task: Task data
            
        Returns:
            Task result
        """
        pass

    async def execute_task(
        self,
        task: Dict[str, Any],
        complexity: TaskComplexity = TaskComplexity.MEDIUM,
    ) -> Dict[str, Any]:
        """Execute a task with observability.
        
        Args:
            task: Task data
            complexity: Task complexity level
            
        Returns:
            Task result
        """
        task_id = task.get("id", str(uuid4()))
        start_time = time.time()
        status = "success"

        try:
            with trace_agent_conversation(self.name, task_id):
                logger.info(
                    "Agent task started",
                    agent=self.name,
                    task_id=task_id,
                    task_type=task.get("type", "unknown"),
                )

                result = await self.process(task)

                duration = time.time() - start_time
                agent_task_duration_seconds.labels(
                    agent_name=self.name,
                    task_type=task.get("type", "unknown"),
                    status="success",
                ).observe(duration)

                agent_tasks_total.labels(
                    agent_name=self.name,
                    task_type=task.get("type", "unknown"),
                    status="success",
                ).inc()

                logger.info(
                    "Agent task completed",
                    agent=self.name,
                    task_id=task_id,
                    duration=duration,
                )

                return result

        except Exception as e:
            duration = time.time() - start_time

            agent_task_duration_seconds.labels(
                agent_name=self.name,
                task_type=task.get("type", "unknown"),
                status="error",
            ).observe(duration)

            agent_tasks_total.labels(
                agent_name=self.name,
                task_type=task.get("type", "unknown"),
                status="error",
            ).inc()

            logger.error(
                "Agent task failed",
                agent=self.name,
                task_id=task_id,
                error=str(e),
                duration=duration,
            )
            raise

    async def query_llm(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Query LLM with the given prompt.
        
        Args:
            prompt: Input prompt
            model: Model name (auto-selected if not provided)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM response
        """
        if model is None:
            model = self.model_router.select_model(
                task_complexity=TaskComplexity.MEDIUM
            )

        messages = [{"role": "user", "content": prompt}]
        
        response = await self.llm_client.chat_completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def __del__(self) -> None:
        """Cleanup when agent is destroyed."""
        active_agents.labels(agent_type=self.__class__.__name__).dec()
