"""
pytest fixtures for RAG service tests
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
    """Create a test client for the RAG service."""
    return TestClient(app)


@pytest.fixture
def sample_texts():
    """Return sample texts for embedding tests."""
    return [
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with many layers.",
        "Natural language processing helps computers understand text."
    ]


@pytest.fixture
def sample_query():
    """Return a sample query for RAG tests."""
    return "What is machine learning?"
