"""Tests for the web API."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from src.interfaces.web_api import app
from src.agent.core import ConversationalAgent
from src.integrations.slack import SlackIntegration


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Create mock agent."""
    agent = MagicMock(spec=ConversationalAgent)
    agent.chat = AsyncMock(return_value={
        "response": "Test response",
        "function_calls": [],
        "error": None
    })
    agent.get_integrations_status = AsyncMock(return_value=[
        {
            "name": "slack",
            "healthy": True,
            "functions_count": 2
        }
    ])
    agent.get_available_functions = MagicMock(return_value=[
        {
            "integration": "slack",
            "name": "send_message",
            "full_name": "slack_send_message",
            "description": "Send a message",
            "parameters": []
        }
    ])
    return agent


def test_root_endpoint(client):
    """Test root endpoint returns basic info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert data["name"] == "RAG7 AI Agent Platform"


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@patch("src.interfaces.web_api.agent")
def test_chat_endpoint(mock_agent_global, client, mock_agent):
    """Test chat endpoint with mocked agent."""
    mock_agent_global.return_value = mock_agent
    
    # Mock the global agent
    import src.interfaces.web_api as web_api_module
    web_api_module.agent = mock_agent
    
    response = client.post(
        "/chat",
        json={"message": "Hello, agent!"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert isinstance(data["function_calls"], list)


@patch("src.interfaces.web_api.agent")
def test_integrations_endpoint(mock_agent_global, client, mock_agent):
    """Test integrations endpoint."""
    import src.interfaces.web_api as web_api_module
    web_api_module.agent = mock_agent
    
    response = client.get("/integrations")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@patch("src.interfaces.web_api.agent")
def test_functions_endpoint(mock_agent_global, client, mock_agent):
    """Test functions endpoint."""
    import src.interfaces.web_api as web_api_module
    web_api_module.agent = mock_agent
    
    response = client.get("/functions")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_chat_without_agent(client):
    """Test chat endpoint fails gracefully when agent is not initialized."""
    import src.interfaces.web_api as web_api_module
    web_api_module.agent = None
    
    response = client.post(
        "/chat",
        json={"message": "Hello"}
    )
    
    # Should return 503 Service Unavailable
    assert response.status_code == 503
