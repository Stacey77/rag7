"""
pytest fixtures for backend tests
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_flow():
    """Return a sample flow JSON for testing."""
    return {
        "nodes": [
            {
                "id": "node1",
                "type": "input",
                "data": {"label": "Input Node"}
            }
        ],
        "edges": []
    }


@pytest.fixture
def auth_headers():
    """Return mock auth headers for protected endpoints."""
    return {"Authorization": "Bearer test-token"}
