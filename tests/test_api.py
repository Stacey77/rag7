"""
Test API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/api")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "RAG7 AI Platform"
    assert data["status"] == "operational"


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_list_llm_providers():
    """Test listing LLM providers."""
    response = client.get("/api/v1/llm/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert len(data["providers"]) > 0


def test_list_agent_types():
    """Test listing agent types."""
    response = client.get("/api/v1/agents/types")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) > 0


def test_list_projects():
    """Test listing projects."""
    response = client.get("/api/v1/projects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_project():
    """Test creating a project."""
    project_data = {
        "name": "Test Project",
        "description": "Test description",
        "use_case": "testing",
        "llm_providers": ["openai"]
    }
    response = client.post("/api/v1/projects/", json=project_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == "planning"


def test_list_deployments():
    """Test listing deployments."""
    response = client.get("/api/v1/deployments/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
