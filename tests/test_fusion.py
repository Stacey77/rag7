"""Tests for response fusion."""
import pytest
from rag7.fusion import ResponseFusion
from rag7.models import LLMResponse, LLMProvider, FusionStrategy


@pytest.fixture
def sample_responses():
    """Create sample responses for testing."""
    return [
        LLMResponse(
            content="Python is a high-level programming language.",
            provider=LLMProvider.OPENAI,
            model="gpt-4",
            tokens_used=50,
            cost=0.0015,
            latency_ms=300.0
        ),
        LLMResponse(
            content="Python is a versatile high-level programming language.",
            provider=LLMProvider.ANTHROPIC,
            model="claude-3",
            tokens_used=60,
            cost=0.0018,
            latency_ms=350.0
        ),
        LLMResponse(
            content="Python is a popular high-level language for programming.",
            provider=LLMProvider.GOOGLE,
            model="gemini-pro",
            tokens_used=55,
            cost=0.0011,
            latency_ms=280.0
        )
    ]


def test_fusion_initialization():
    """Test fusion initialization."""
    fusion = ResponseFusion()
    assert fusion.config is not None


def test_single_response_fusion(sample_responses):
    """Test fusion with single response."""
    fusion = ResponseFusion()
    single_response = [sample_responses[0]]
    
    result = fusion.fuse_responses(single_response)
    
    assert result.final_content == sample_responses[0].content
    assert result.fusion_strategy == FusionStrategy.FIRST
    assert result.confidence_score == 1.0
    assert len(result.individual_responses) == 1


def test_voting_fusion(sample_responses):
    """Test voting fusion strategy."""
    fusion = ResponseFusion()
    result = fusion.fuse_responses(sample_responses, FusionStrategy.VOTING)
    
    assert result.fusion_strategy == FusionStrategy.VOTING
    assert len(result.individual_responses) == 3
    assert result.confidence_score is not None
    assert result.confidence_score > 0
    assert result.total_cost > 0


def test_ranking_fusion(sample_responses):
    """Test ranking fusion strategy."""
    fusion = ResponseFusion()
    result = fusion.fuse_responses(sample_responses, FusionStrategy.RANKING)
    
    assert result.fusion_strategy == FusionStrategy.RANKING
    assert len(result.individual_responses) == 3
    assert "selected_provider" in result.metadata
    assert "ranking_scores" in result.metadata


def test_merging_fusion(sample_responses):
    """Test merging fusion strategy."""
    fusion = ResponseFusion()
    result = fusion.fuse_responses(sample_responses, FusionStrategy.MERGING)
    
    assert result.fusion_strategy == FusionStrategy.MERGING
    assert len(result.individual_responses) == 3
    assert "# Synthesized Response" in result.final_content
    assert "openai" in result.final_content.lower()
    assert "anthropic" in result.final_content.lower()


def test_first_fusion(sample_responses):
    """Test first fusion strategy."""
    fusion = ResponseFusion()
    result = fusion.fuse_responses(sample_responses, FusionStrategy.FIRST)
    
    assert result.fusion_strategy == FusionStrategy.FIRST
    assert result.final_content == sample_responses[0].content
    assert result.metadata["selected_provider"] == "openai"


def test_fusion_cost_calculation(sample_responses):
    """Test that fusion calculates total cost correctly."""
    fusion = ResponseFusion()
    result = fusion.fuse_responses(sample_responses, FusionStrategy.VOTING)
    
    expected_cost = sum(r.cost for r in sample_responses)
    assert abs(result.total_cost - expected_cost) < 0.0001


def test_fusion_latency_calculation(sample_responses):
    """Test that fusion calculates total latency correctly."""
    fusion = ResponseFusion()
    result = fusion.fuse_responses(sample_responses, FusionStrategy.VOTING)
    
    expected_latency = sum(r.latency_ms for r in sample_responses)
    assert abs(result.total_latency_ms - expected_latency) < 0.1


def test_fusion_empty_responses():
    """Test fusion with empty responses list."""
    fusion = ResponseFusion()
    
    with pytest.raises(ValueError, match="No responses to fuse"):
        fusion.fuse_responses([])
