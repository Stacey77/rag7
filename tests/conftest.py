"""Tests configuration."""
import pytest


# Configure pytest for async tests
pytest_plugins = ['pytest_asyncio']


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("SLACK_BOT_TOKEN", "xoxb-test-token")
    monkeypatch.setenv("GMAIL_SMTP_USER", "test@gmail.com")
    monkeypatch.setenv("GMAIL_SMTP_PASSWORD", "test-password")
    monkeypatch.setenv("NOTION_API_KEY", "secret_test_key")
