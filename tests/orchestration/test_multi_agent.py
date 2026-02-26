"""Multi-agent orchestration tests."""
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock
from src.agents.base_agent import BaseAgent
from src.llm import TaskComplexity


class TestAgent(BaseAgent):
    """Test agent implementation."""
    
    async def process(self, task):
        """Process task."""
        return {"status": "completed", "result": f"Processed: {task.get('data')}"}


@pytest.mark.orchestration
@pytest.mark.asyncio
async def test_multi_agent_collaboration():
    """Test multiple agents collaborating on a task."""
    # Create multiple agents
    agent1 = TestAgent("agent1", "First agent")
    agent2 = TestAgent("agent2", "Second agent")
    agent3 = TestAgent("agent3", "Third agent")
    
    # Create tasks
    task1 = {"id": "task1", "type": "analysis", "data": "test data 1"}
    task2 = {"id": "task2", "type": "synthesis", "data": "test data 2"}
    task3 = {"id": "task3", "type": "validation", "data": "test data 3"}
    
    # Execute tasks concurrently
    results = await asyncio.gather(
        agent1.execute_task(task1),
        agent2.execute_task(task2),
        agent3.execute_task(task3),
    )
    
    # Verify all tasks completed
    assert len(results) == 3
    assert all(r["status"] == "completed" for r in results)


@pytest.mark.orchestration
@pytest.mark.asyncio
async def test_agent_failure_recovery():
    """Test agent recovery from failures."""
    
    class FailingAgent(BaseAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.attempt_count = 0
        
        async def process(self, task):
            self.attempt_count += 1
            if self.attempt_count < 2:
                raise Exception("Simulated failure")
            return {"status": "completed", "attempts": self.attempt_count}
    
    agent = FailingAgent("failing_agent")
    task = {"id": "task1", "type": "test"}
    
    # First attempt should fail
    with pytest.raises(Exception):
        await agent.execute_task(task)
    
    # Second attempt should succeed
    result = await agent.execute_task(task)
    assert result["status"] == "completed"
    assert result["attempts"] == 2


@pytest.mark.orchestration
@pytest.mark.asyncio
async def test_agent_deadlock_detection():
    """Test detection of deadlocks in agent communication."""
    
    class WaitingAgent(BaseAgent):
        def __init__(self, *args, wait_time=0.1, **kwargs):
            super().__init__(*args, **kwargs)
            self.wait_time = wait_time
        
        async def process(self, task):
            await asyncio.sleep(self.wait_time)
            return {"status": "completed"}
    
    # Create agents with different wait times
    agents = [
        WaitingAgent(f"agent{i}", wait_time=0.1)
        for i in range(5)
    ]
    
    # Create tasks
    tasks = [
        {"id": f"task{i}", "type": "test"}
        for i in range(5)
    ]
    
    # Execute with timeout to detect potential deadlocks
    try:
        results = await asyncio.wait_for(
            asyncio.gather(*[
                agent.execute_task(task)
                for agent, task in zip(agents, tasks)
            ]),
            timeout=5.0
        )
        assert len(results) == 5
    except asyncio.TimeoutError:
        pytest.fail("Deadlock detected: Tasks did not complete within timeout")


@pytest.mark.orchestration
@pytest.mark.asyncio
async def test_load_balancing_across_agents():
    """Test load balancing across multiple agents."""
    
    class CountingAgent(BaseAgent):
        def __init__(self, name: str):
            super().__init__(name)
            self._task_count = 0
        
        async def process(self, task):
            self._task_count += 1
            await asyncio.sleep(0.01)  # Simulate work
            return {"status": "completed", "agent": self.name, "count": self._task_count}
    
    # Create agent pool
    agent_pool = [
        CountingAgent(f"agent{i}")
        for i in range(3)
    ]
    
    # Create many tasks
    tasks = [
        {"id": f"task{i}", "type": "test"}
        for i in range(30)
    ]
    
    # Distribute tasks across agents
    results = []
    for i, task in enumerate(tasks):
        agent = agent_pool[i % len(agent_pool)]
        result = await agent.execute_task(task)
        results.append(result)
    
    # Verify all tasks completed
    assert len(results) == 30
    assert all(r["status"] == "completed" for r in results)
    
    # Verify load distribution (each agent should have handled ~10 tasks)
    agent_counts = {}
    for result in results:
        agent_name = result["agent"]
        agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
    
    # Check that load is relatively balanced
    assert all(8 <= count <= 12 for count in agent_counts.values())
