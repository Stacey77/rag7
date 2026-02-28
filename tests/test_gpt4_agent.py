"""
Tests for the GPT-4 agent.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from agents.gpt4 import GPT4Agent
from agents.base import AgentRequest, AgentResponse


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "This is a test response from GPT-4."
    mock_response.choices[0].finish_reason = "stop"
    mock_response.usage = Mock()
    mock_response.usage.total_tokens = 50
    mock_response.model = "gpt-4"
    return mock_response


@pytest.fixture
def gpt4_agent():
    """Create a GPT-4 agent with a test API key."""
    return GPT4Agent(name="test-agent", api_key="test-key-123")


class TestGPT4AgentInitialization:
    """Tests for agent initialization."""
    
    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        agent = GPT4Agent(name="test", api_key="test-key")
        assert agent.name == "test"
        assert agent.api_key == "test-key"
        assert agent.model == GPT4Agent.DEFAULT_MODEL
    
    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        agent = GPT4Agent(name="test", api_key="test-key", model="gpt-4-turbo")
        assert agent.model == "gpt-4-turbo"
    
    def test_init_without_api_key_raises_error(self):
        """Test that initialization without API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            GPT4Agent(name="test")
    
    def test_init_with_env_var(self, monkeypatch):
        """Test initialization using environment variable."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-key")
        agent = GPT4Agent(name="test")
        assert agent.api_key == "env-key"


class TestGPT4AgentConfiguration:
    """Tests for agent configuration."""
    
    def test_validate_config_valid(self, gpt4_agent):
        """Test validation with valid configuration."""
        assert gpt4_agent.validate_config() is True
    
    def test_validate_config_no_api_key(self):
        """Test validation fails without API key."""
        agent = GPT4Agent.__new__(GPT4Agent)
        agent.api_key = None
        agent.model = "gpt-4"
        agent.logger = Mock()
        assert agent.validate_config() is False
    
    def test_get_capabilities(self, gpt4_agent):
        """Test getting agent capabilities."""
        caps = gpt4_agent.get_capabilities()
        assert caps["name"] == "test-agent"
        assert caps["model"] == "gpt-4"
        assert caps["supports_async"] is True
        assert caps["max_retries"] == GPT4Agent.MAX_RETRIES


class TestGPT4AgentProcessing:
    """Tests for request processing."""
    
    @pytest.mark.asyncio
    async def test_process_request_success(self, gpt4_agent, mock_openai_response):
        """Test successful request processing."""
        with patch.object(
            gpt4_agent.client.chat.completions,
            'create',
            new_callable=AsyncMock,
            return_value=mock_openai_response
        ):
            request = AgentRequest(
                prompt="Test prompt",
                max_tokens=100,
                temperature=0.7
            )
            
            response = await gpt4_agent.process_request(request)
            
            assert response.success is True
            assert response.content == "This is a test response from GPT-4."
            assert response.agent_name == "test-agent"
            assert response.tokens_used == 50
            assert response.error is None
    
    @pytest.mark.asyncio
    async def test_process_request_with_context(self, gpt4_agent, mock_openai_response):
        """Test request processing with context."""
        with patch.object(
            gpt4_agent.client.chat.completions,
            'create',
            new_callable=AsyncMock,
            return_value=mock_openai_response
        ):
            request = AgentRequest(
                prompt="Test prompt",
                context={
                    "system_message": "You are a helpful assistant.",
                    "history": [{"role": "user", "content": "Previous message"}]
                }
            )
            
            response = await gpt4_agent.process_request(request)
            
            assert response.success is True
            assert response.content is not None
    
    @pytest.mark.asyncio
    async def test_process_request_api_error(self, gpt4_agent):
        """Test handling of API errors."""
        from openai import APIError
        
        # Create a proper mock request object
        mock_request = Mock()
        mock_request.method = "POST"
        mock_request.url = "https://api.openai.com/v1/chat/completions"
        mock_body = {"error": {"message": "API Error"}}
        
        with patch.object(
            gpt4_agent.client.chat.completions,
            'create',
            new_callable=AsyncMock,
            side_effect=APIError("API Error", request=mock_request, body=mock_body)
        ):
            request = AgentRequest(prompt="Test prompt")
            response = await gpt4_agent.process_request(request)
            
            assert response.success is False
            assert response.error is not None
            assert "API error" in response.error
    
    @pytest.mark.asyncio
    async def test_process_request_rate_limit(self, gpt4_agent):
        """Test handling of rate limit errors."""
        from openai import RateLimitError
        
        # Create proper mock objects for RateLimitError
        mock_response = Mock()
        mock_response.status_code = 429
        mock_body = {"error": {"message": "Rate limit exceeded"}}
        
        with patch.object(
            gpt4_agent.client.chat.completions,
            'create',
            new_callable=AsyncMock,
            side_effect=RateLimitError("Rate limit exceeded", response=mock_response, body=mock_body)
        ):
            request = AgentRequest(prompt="Test prompt")
            response = await gpt4_agent.process_request(request)
            
            assert response.success is False
            assert "Rate limit" in response.error
    
    @pytest.mark.asyncio
    async def test_process_request_invalid_config(self, gpt4_agent):
        """Test request processing with invalid configuration."""
        gpt4_agent.api_key = None
        
        request = AgentRequest(prompt="Test prompt")
        response = await gpt4_agent.process_request(request)
        
        assert response.success is False
        assert response.error is not None


class TestGPT4AgentErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_create_error_response(self, gpt4_agent):
        """Test error response creation."""
        start_time = datetime.now()
        error_response = gpt4_agent._create_error_response(
            "Test error",
            start_time
        )
        
        assert error_response.success is False
        assert error_response.error == "Test error"
        assert error_response.agent_name == "test-agent"
        assert error_response.content == ""
        assert "processing_time" in error_response.metadata


class TestGPT4AgentRetry:
    """Tests for retry logic."""
    
    @pytest.mark.asyncio
    async def test_retry_on_rate_limit(self, gpt4_agent, mock_openai_response):
        """Test that rate limit errors trigger retry."""
        from openai import RateLimitError
        
        # Create proper mock objects for RateLimitError
        mock_response = Mock()
        mock_response.status_code = 429
        mock_body = {"error": {"message": "Rate limit exceeded"}}
        
        # Simulate: fail twice, then succeed
        call_count = 0
        
        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError("Rate limit", response=mock_response, body=mock_body)
            return mock_openai_response
        
        with patch.object(
            gpt4_agent.client.chat.completions,
            'create',
            new_callable=AsyncMock,
            side_effect=side_effect
        ):
            result = await gpt4_agent._call_openai_api("Test prompt")
            
            assert call_count == 3
            assert result["content"] == "This is a test response from GPT-4."
