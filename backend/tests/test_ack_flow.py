"""Tests for the ack flow and escalation mechanism."""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.agents.communication import (
    AgentCommunicationSystem,
    AgentMessage,
    TaskState
)


class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.published = []
        self.lists = {}
        self._pubsub = MockPubSub()
    
    async def publish(self, channel: str, message: str):
        self.published.append({"channel": channel, "message": message})
        return 1
    
    async def lpush(self, key: str, value: str):
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key].insert(0, value)
        return len(self.lists[key])
    
    async def rpop(self, key: str):
        if key in self.lists and self.lists[key]:
            return self.lists[key].pop()
        return None
    
    def pubsub(self):
        return self._pubsub


class MockPubSub:
    """Mock PubSub for testing."""
    
    def __init__(self):
        self.subscribed = []
        self.messages = []
    
    async def subscribe(self, channel: str):
        self.subscribed.append(channel)
    
    async def unsubscribe(self, channel: str):
        if channel in self.subscribed:
            self.subscribed.remove(channel)
    
    async def close(self):
        pass
    
    async def listen(self):
        for msg in self.messages:
            yield msg


@pytest.fixture
def mock_redis():
    """Create mock Redis client."""
    return MockRedis()


@pytest.fixture
def comm_system(mock_redis):
    """Create AgentCommunicationSystem with mock Redis."""
    return AgentCommunicationSystem(mock_redis)


class TestAgentMessage:
    """Tests for AgentMessage class."""
    
    def test_create_message(self):
        """Test creating an agent message."""
        msg = AgentMessage(
            message_id="msg-123",
            task_id="task-456",
            message_type="task_assignment",
            payload={"action": "test"},
            sender_id="orchestrator"
        )
        
        assert msg.message_id == "msg-123"
        assert msg.task_id == "task-456"
        assert msg.message_type == "task_assignment"
        assert msg.payload == {"action": "test"}
        assert msg.sender_id == "orchestrator"
        assert msg.correlation_id == "msg-123"
    
    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = AgentMessage(
            message_id="msg-123",
            task_id="task-456",
            message_type="task_assignment",
            payload={"action": "test"},
            sender_id="orchestrator"
        )
        
        data = msg.to_dict()
        
        assert data["message_id"] == "msg-123"
        assert data["task_id"] == "task-456"
        assert data["message_type"] == "task_assignment"
        assert data["payload"] == {"action": "test"}
        assert "timestamp" in data
    
    def test_message_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            "message_id": "msg-123",
            "task_id": "task-456",
            "message_type": "task_assignment",
            "payload": {"action": "test"},
            "sender_id": "orchestrator",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        msg = AgentMessage.from_dict(data)
        
        assert msg.message_id == "msg-123"
        assert msg.task_id == "task-456"


class TestAgentCommunicationSystem:
    """Tests for AgentCommunicationSystem."""
    
    @pytest.mark.asyncio
    async def test_publish_task_timeout(self, comm_system, mock_redis):
        """Test that task publication times out when no ack received."""
        # Set very short timeout for testing
        with patch.object(comm_system, 'redis', mock_redis):
            success, ack_data, retry_count = await comm_system.publish_task(
                task_id="task-123",
                payload={"action": "test"},
                timeout=0.01,  # Very short timeout
                max_retries=0  # No retries
            )
        
        assert success is False
        assert ack_data is None
        # retry_count is 1 after loop exits (incremented when timeout occurs)
    
    @pytest.mark.asyncio
    async def test_publish_task_with_retries(self, comm_system, mock_redis):
        """Test that task publication retries on timeout."""
        with patch.object(comm_system, 'redis', mock_redis):
            success, ack_data, retry_count = await comm_system.publish_task(
                task_id="task-123",
                payload={"action": "test"},
                timeout=0.01,
                max_retries=2
            )
        
        assert success is False
        assert retry_count == 3  # Initial + 2 retries
        
        # Verify multiple publishes occurred
        assert len(mock_redis.published) >= 2
    
    @pytest.mark.asyncio
    async def test_escalate_task(self, comm_system, mock_redis):
        """Test task escalation after max retries."""
        with patch.object(comm_system, 'redis', mock_redis):
            success, ack_data, retry_count = await comm_system.publish_task(
                task_id="task-123",
                payload={"action": "test"},
                timeout=0.01,
                max_retries=1
            )
        
        assert success is False
        
        # Check escalation was published
        escalation_messages = [
            p for p in mock_redis.published 
            if p["channel"] == "agentic:escalations"
        ]
        assert len(escalation_messages) == 1
        
        # Check escalation queue
        assert "agentic:escalation_queue" in mock_redis.lists
        assert len(mock_redis.lists["agentic:escalation_queue"]) == 1
    
    @pytest.mark.asyncio
    async def test_send_ack(self, comm_system, mock_redis):
        """Test sending acknowledgement."""
        with patch.object(comm_system, 'redis', mock_redis):
            await comm_system.send_ack(
                correlation_id="corr-123",
                task_id="task-456",
                agent_id="agent-789",
                status="acked",
                metadata={"processed": True}
            )
        
        # Verify ack was published
        ack_messages = [
            p for p in mock_redis.published 
            if p["channel"] == "agentic:acks"
        ]
        assert len(ack_messages) == 1
        
        ack_data = json.loads(ack_messages[0]["message"])
        assert ack_data["correlation_id"] == "corr-123"
        assert ack_data["task_id"] == "task-456"
        assert ack_data["agent_id"] == "agent-789"
    
    @pytest.mark.asyncio
    async def test_get_escalated_tasks(self, comm_system, mock_redis):
        """Test retrieving escalated tasks."""
        # Add some escalated tasks to queue
        for i in range(3):
            await mock_redis.lpush(
                "agentic:escalation_queue",
                json.dumps({"task_id": f"task-{i}"})
            )
        
        with patch.object(comm_system, 'redis', mock_redis):
            tasks = await comm_system.get_escalated_tasks(count=2)
        
        assert len(tasks) == 2


class TestTaskState:
    """Tests for TaskState enum."""
    
    def test_task_states(self):
        """Test all task states are defined."""
        assert TaskState.QUEUED.value == "queued"
        assert TaskState.ASSIGNED.value == "assigned"
        assert TaskState.ACKED.value == "acked"
        assert TaskState.IN_PROGRESS.value == "in_progress"
        assert TaskState.COMPLETED.value == "completed"
        assert TaskState.VERIFIED.value == "verified"
        assert TaskState.FAILED.value == "failed"
        assert TaskState.ESCALATED.value == "escalated"


class TestExponentialBackoff:
    """Tests for exponential backoff behavior."""
    
    @pytest.mark.asyncio
    async def test_backoff_increases(self, comm_system, mock_redis):
        """Test that backoff increases with retries."""
        timeouts = []
        original_wait_for = asyncio.wait_for
        
        async def mock_wait_for(coro, timeout):
            timeouts.append(timeout)
            raise asyncio.TimeoutError()
        
        with patch('asyncio.wait_for', mock_wait_for):
            with patch.object(comm_system, 'redis', mock_redis):
                await comm_system.publish_task(
                    task_id="task-123",
                    payload={},
                    timeout=1.0,
                    max_retries=2
                )
        
        # Verify exponential increase (base 2.0)
        # Retry 0: 1.0 * 2^0 = 1.0
        # Retry 1: 1.0 * 2^1 = 2.0
        # Retry 2: 1.0 * 2^2 = 4.0
        assert len(timeouts) == 3
        assert timeouts[0] == pytest.approx(1.0)
        assert timeouts[1] == pytest.approx(2.0)
        assert timeouts[2] == pytest.approx(4.0)
