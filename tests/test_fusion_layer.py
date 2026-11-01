"""
Tests for the fusion layer.
"""

import pytest
from datetime import datetime
from agents.fusion import ResponseFusionLayer, FusedResponse
from agents.base import AgentResponse


@pytest.fixture
def successful_responses():
    """Create sample successful responses from multiple agents."""
    return [
        AgentResponse(
            content="Response from GPT-4: Quantum computing uses quantum mechanics.",
            agent_name="gpt4",
            model="gpt-4",
            timestamp=datetime.now(),
            tokens_used=50,
            success=True
        ),
        AgentResponse(
            content="Response from Claude: Quantum computing leverages superposition.",
            agent_name="claude",
            model="claude-2",
            timestamp=datetime.now(),
            tokens_used=45,
            success=True
        ),
        AgentResponse(
            content="Response from Gemini: Quantum computing is a revolutionary technology.",
            agent_name="gemini",
            model="gemini-pro",
            timestamp=datetime.now(),
            tokens_used=40,
            success=True
        )
    ]


@pytest.fixture
def mixed_responses(successful_responses):
    """Create responses with some failures."""
    failed_response = AgentResponse(
        content="",
        agent_name="failed-agent",
        model="unknown",
        timestamp=datetime.now(),
        error="Connection timeout",
        success=False
    )
    return successful_responses + [failed_response]


class TestFusionLayerInitialization:
    """Tests for fusion layer initialization."""
    
    def test_init_default(self):
        """Test initialization with defaults."""
        fusion = ResponseFusionLayer()
        assert fusion.strategy == "consensus"
        assert fusion.config == {}
    
    def test_init_custom_strategy(self):
        """Test initialization with custom strategy."""
        fusion = ResponseFusionLayer(strategy="best")
        assert fusion.strategy == "best"
    
    def test_init_with_config(self):
        """Test initialization with configuration."""
        config = {"weights": {"gpt4": 1.0, "claude": 0.9}}
        fusion = ResponseFusionLayer(strategy="weighted", config=config)
        assert fusion.config == config


class TestConsensusFusion:
    """Tests for consensus fusion strategy."""
    
    @pytest.mark.asyncio
    async def test_consensus_fusion_success(self, successful_responses):
        """Test consensus fusion with successful responses."""
        fusion = ResponseFusionLayer(strategy="consensus")
        fused = await fusion.fuse_responses(successful_responses)
        
        assert isinstance(fused, FusedResponse)
        assert fused.content != ""
        assert len(fused.contributing_agents) == 3
        assert fused.confidence > 0
        assert fused.metadata["strategy"] == "consensus"
    
    @pytest.mark.asyncio
    async def test_consensus_selects_longest(self, successful_responses):
        """Test that consensus selects the longest response."""
        # Add a clearly longest response
        successful_responses[0].content = "This is a much longer response " * 10
        
        fusion = ResponseFusionLayer(strategy="consensus")
        fused = await fusion.fuse_responses(successful_responses)
        
        assert "much longer response" in fused.content


class TestBestResponseFusion:
    """Tests for best response fusion strategy."""
    
    @pytest.mark.asyncio
    async def test_best_response_fusion(self, successful_responses):
        """Test best response fusion."""
        fusion = ResponseFusionLayer(strategy="best")
        fused = await fusion.fuse_responses(successful_responses)
        
        assert fused.content != ""
        assert len(fused.contributing_agents) == 1
        assert fused.metadata["strategy"] == "best"
        assert fused.confidence == 0.9
    
    @pytest.mark.asyncio
    async def test_best_selects_most_tokens(self, successful_responses):
        """Test that best selects response with most tokens."""
        fusion = ResponseFusionLayer(strategy="best")
        fused = await fusion.fuse_responses(successful_responses)
        
        # Should select gpt4 which has 50 tokens
        assert fused.metadata["selected_agent"] == "gpt4"


class TestWeightedFusion:
    """Tests for weighted fusion strategy."""
    
    @pytest.mark.asyncio
    async def test_weighted_fusion(self, successful_responses):
        """Test weighted fusion."""
        config = {"weights": {"gpt4": 1.0, "claude": 0.5, "gemini": 0.3}}
        fusion = ResponseFusionLayer(strategy="weighted", config=config)
        fused = await fusion.fuse_responses(successful_responses)
        
        assert fused.content != ""
        assert fused.metadata["strategy"] == "weighted"
        assert fused.metadata["selected_agent"] == "gpt4"
    
    @pytest.mark.asyncio
    async def test_weighted_without_config(self, successful_responses):
        """Test weighted fusion without weight configuration."""
        fusion = ResponseFusionLayer(strategy="weighted")
        fused = await fusion.fuse_responses(successful_responses)
        
        # Should work with default weights of 1.0
        assert fused.content != ""


class TestConcatenateFusion:
    """Tests for concatenate fusion strategy."""
    
    @pytest.mark.asyncio
    async def test_concatenate_fusion(self, successful_responses):
        """Test concatenate fusion."""
        fusion = ResponseFusionLayer(strategy="concatenate")
        fused = await fusion.fuse_responses(successful_responses)
        
        # Should contain content from all agents
        assert "gpt4" in fused.content
        assert "claude" in fused.content
        assert "gemini" in fused.content
        assert len(fused.contributing_agents) == 3
    
    @pytest.mark.asyncio
    async def test_concatenate_custom_separator(self, successful_responses):
        """Test concatenate with custom separator."""
        config = {"separator": "\n\n===\n\n"}
        fusion = ResponseFusionLayer(strategy="concatenate", config=config)
        fused = await fusion.fuse_responses(successful_responses)
        
        assert "===" in fused.content


class TestFusionErrorHandling:
    """Tests for fusion error handling."""
    
    @pytest.mark.asyncio
    async def test_fuse_empty_list(self):
        """Test fusion with empty response list."""
        fusion = ResponseFusionLayer()
        
        with pytest.raises(ValueError, match="No responses to fuse"):
            await fusion.fuse_responses([])
    
    @pytest.mark.asyncio
    async def test_fuse_all_failed(self):
        """Test fusion when all responses failed."""
        failed_responses = [
            AgentResponse(
                content="",
                agent_name=f"agent-{i}",
                model="model",
                timestamp=datetime.now(),
                error=f"Error {i}",
                success=False
            )
            for i in range(3)
        ]
        
        fusion = ResponseFusionLayer()
        fused = await fusion.fuse_responses(failed_responses)
        
        assert "All agents failed" in fused.content
        assert fused.confidence == 0.0
        assert fused.metadata["all_failed"] is True
    
    @pytest.mark.asyncio
    async def test_fuse_mixed_responses(self, mixed_responses):
        """Test fusion with mixed success/failure responses."""
        fusion = ResponseFusionLayer()
        fused = await fusion.fuse_responses(mixed_responses)
        
        # Should successfully fuse the successful ones
        assert fused.content != ""
        assert len(fused.contributing_agents) == 3  # Only successful ones
        assert fused.confidence > 0
    
    @pytest.mark.asyncio
    async def test_invalid_strategy(self, successful_responses):
        """Test fusion with invalid strategy."""
        fusion = ResponseFusionLayer(strategy="invalid")
        
        with pytest.raises(ValueError, match="Unknown fusion strategy"):
            await fusion.fuse_responses(successful_responses)


class TestResponseValidation:
    """Tests for response validation."""
    
    def test_validate_successful_response(self):
        """Test validation of successful response."""
        fusion = ResponseFusionLayer()
        response = AgentResponse(
            content="Valid content",
            agent_name="test",
            model="test-model",
            timestamp=datetime.now(),
            success=True
        )
        
        assert fusion.validate_response(response) is True
    
    def test_validate_failed_response(self):
        """Test validation of failed response."""
        fusion = ResponseFusionLayer()
        response = AgentResponse(
            content="",
            agent_name="test",
            model="test-model",
            timestamp=datetime.now(),
            error="Error",
            success=False
        )
        
        assert fusion.validate_response(response) is False
    
    def test_validate_empty_content(self):
        """Test validation of response with empty content."""
        fusion = ResponseFusionLayer()
        response = AgentResponse(
            content="   ",
            agent_name="test",
            model="test-model",
            timestamp=datetime.now(),
            success=True
        )
        
        assert fusion.validate_response(response) is False
