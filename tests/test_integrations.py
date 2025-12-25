"""Tests for integrations."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.integrations.slack import SlackIntegration
from src.integrations.gmail import GmailIntegration
from src.integrations.notion import NotionIntegration


@pytest.mark.asyncio
async def test_slack_integration_functions():
    """Test Slack integration lists functions."""
    slack = SlackIntegration(bot_token="xoxb-test-token")
    
    functions = slack.get_functions()
    assert len(functions) > 0
    
    # Check send_message function exists
    send_message = next((f for f in functions if f.name == "send_message"), None)
    assert send_message is not None
    assert send_message.description != ""


@pytest.mark.asyncio
async def test_slack_integration_to_openai_format():
    """Test Slack integration converts to OpenAI function format."""
    slack = SlackIntegration(bot_token="xoxb-test-token")
    
    openai_functions = slack.to_openai_functions()
    assert len(openai_functions) > 0
    
    # Check format
    func = openai_functions[0]
    assert "name" in func
    assert "description" in func
    assert "parameters" in func
    assert func["parameters"]["type"] == "object"


@pytest.mark.asyncio
async def test_slack_send_message_without_token():
    """Test Slack send_message fails gracefully without token."""
    slack = SlackIntegration(bot_token=None)
    
    result = await slack.execute("send_message", channel="test", text="Hello")
    
    assert result["success"] is False
    assert "not configured" in result["error"].lower()


@pytest.mark.asyncio
async def test_gmail_integration_functions():
    """Test Gmail integration lists functions."""
    gmail = GmailIntegration()
    
    functions = gmail.get_functions()
    assert len(functions) > 0
    
    # Check send_email function exists
    send_email = next((f for f in functions if f.name == "send_email"), None)
    assert send_email is not None


@pytest.mark.asyncio
async def test_gmail_integration_stub_response():
    """Test Gmail integration returns stub responses."""
    gmail = GmailIntegration(smtp_user="test@gmail.com", smtp_password="test")
    
    result = await gmail.execute(
        "send_email",
        to="recipient@example.com",
        subject="Test",
        body="Test body"
    )
    
    assert result["success"] is True
    assert "stub" in result["data"]["status"].lower()


@pytest.mark.asyncio
async def test_notion_integration_functions():
    """Test Notion integration lists functions."""
    notion = NotionIntegration(api_key="secret_test_key")
    
    functions = notion.get_functions()
    assert len(functions) > 0
    
    # Check create_page function exists
    create_page = next((f for f in functions if f.name == "create_page"), None)
    assert create_page is not None


@pytest.mark.asyncio
async def test_notion_integration_stub_response():
    """Test Notion integration returns stub responses."""
    notion = NotionIntegration(api_key="secret_test_key")
    
    result = await notion.execute(
        "create_page",
        title="Test Page",
        content="Test content"
    )
    
    assert result["success"] is True
    assert "page_id" in result["data"]


@pytest.mark.asyncio
async def test_integration_health_checks():
    """Test health checks for all integrations."""
    slack = SlackIntegration(bot_token=None)
    gmail = GmailIntegration()
    notion = NotionIntegration(api_key=None)
    
    # Without credentials, health checks should handle gracefully
    slack_health = await slack.health_check()
    gmail_health = await gmail.health_check()
    notion_health = await notion.health_check()
    
    assert isinstance(slack_health, bool)
    assert isinstance(gmail_health, bool)
    assert isinstance(notion_health, bool)


def test_integrations_are_discoverable():
    """Test that integrations can be imported and instantiated."""
    # This ensures the package structure is correct
    slack = SlackIntegration()
    gmail = GmailIntegration()
    notion = NotionIntegration()
    
    assert slack.name == "slack"
    assert gmail.name == "gmail"
    assert notion.name == "notion"
