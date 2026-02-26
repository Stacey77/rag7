"""Chaos engineering tests for agent resilience."""
import asyncio
import random
import pytest
from unittest.mock import patch
from src.agents.base_agent import BaseAgent


class ResilientAgent(BaseAgent):
    """Agent for chaos testing."""
    
    async def process(self, task):
        """Process task with potential failures."""
        await asyncio.sleep(0.01)  # Simulate work
        return {"status": "completed", "data": task.get("data")}


@pytest.mark.chaos
@pytest.mark.slow
@pytest.mark.asyncio
async def test_random_agent_failures():
    """Test system resilience with random agent failures."""
    
    class ChaoticAgent(BaseAgent):
        def __init__(self, *args, failure_rate=0.3, **kwargs):
            super().__init__(*args, **kwargs)
            self.failure_rate = failure_rate
        
        async def process(self, task):
            # Randomly fail based on failure rate
            if random.random() < self.failure_rate:
                raise Exception("Random chaos failure")
            return {"status": "completed"}
    
    agents = [ChaoticAgent(f"chaos_agent{i}", failure_rate=0.3) for i in range(5)]
    tasks = [{"id": f"task{i}", "type": "test"} for i in range(20)]
    
    # Execute tasks and count successes/failures
    successes = 0
    failures = 0
    
    for agent, task in zip(agents * 4, tasks):  # Cycle through agents
        try:
            await agent.execute_task(task)
            successes += 1
        except Exception:
            failures += 1
    
    # Verify some tasks succeeded despite failures
    assert successes > 0
    assert successes + failures == 20
    
    # With 30% failure rate, expect roughly 14 successes
    assert 10 <= successes <= 18


@pytest.mark.chaos
@pytest.mark.slow
@pytest.mark.asyncio
async def test_network_latency_injection():
    """Test agent performance under network latency."""
    
    class LatencyAgent(BaseAgent):
        async def process(self, task):
            # Inject random latency (50-500ms)
            latency = random.uniform(0.05, 0.5)
            await asyncio.sleep(latency)
            return {"status": "completed", "latency": latency}
    
    agent = LatencyAgent("latency_agent")
    tasks = [{"id": f"task{i}", "type": "test"} for i in range(10)]
    
    start_time = asyncio.get_event_loop().time()
    results = []
    
    for task in tasks:
        result = await agent.execute_task(task)
        results.append(result)
    
    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start_time
    
    # Verify all tasks completed despite latency
    assert len(results) == 10
    assert all(r["status"] == "completed" for r in results)
    
    # Total time should be at least 0.5s (minimum latency per task)
    assert total_time >= 0.5


@pytest.mark.chaos
@pytest.mark.slow
@pytest.mark.asyncio
async def test_rate_limiting_chaos():
    """Test system behavior under rate limiting."""
    
    class RateLimitedAgent(BaseAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.request_times = []
            self.max_rpm = 10  # 10 requests per minute
        
        async def process(self, task):
            current_time = asyncio.get_event_loop().time()
            
            # Remove old requests (older than 1 minute)
            self.request_times = [
                t for t in self.request_times
                if current_time - t < 60
            ]
            
            # Check rate limit
            if len(self.request_times) >= self.max_rpm:
                raise Exception("Rate limit exceeded")
            
            self.request_times.append(current_time)
            return {"status": "completed"}
    
    agent = RateLimitedAgent("rate_limited_agent")
    tasks = [{"id": f"task{i}", "type": "test"} for i in range(15)]
    
    successes = 0
    rate_limit_errors = 0
    
    for task in tasks:
        try:
            await agent.execute_task(task)
            successes += 1
        except Exception as e:
            if "Rate limit exceeded" in str(e):
                rate_limit_errors += 1
    
    # Should hit rate limit
    assert successes <= 10
    assert rate_limit_errors > 0


@pytest.mark.chaos
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_chaos():
    """Test system under concurrent chaos conditions."""
    
    class ComplexChaoticAgent(BaseAgent):
        async def process(self, task):
            # Multiple chaos scenarios
            chaos_type = random.choice(["latency", "failure", "success"])
            
            if chaos_type == "latency":
                await asyncio.sleep(random.uniform(0.1, 0.3))
            elif chaos_type == "failure":
                if random.random() < 0.2:  # 20% failure rate
                    raise Exception("Chaos failure")
            
            return {"status": "completed", "chaos_type": chaos_type}
    
    # Create multiple agents
    agents = [ComplexChaoticAgent(f"agent{i}") for i in range(5)]
    tasks = [{"id": f"task{i}", "type": "test"} for i in range(50)]
    
    # Execute concurrently
    async def execute_with_agent(agent, task):
        try:
            return await agent.execute_task(task)
        except Exception:
            return {"status": "failed"}
    
    results = await asyncio.gather(*[
        execute_with_agent(agents[i % len(agents)], task)
        for i, task in enumerate(tasks)
    ])
    
    # Count outcomes
    successes = sum(1 for r in results if r["status"] == "completed")
    failures = sum(1 for r in results if r["status"] == "failed")
    
    # Verify system maintained some level of functionality
    assert successes > 30  # At least 60% success rate
    assert len(results) == 50
