"""Core Pydantic models for request/response validation."""
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class TaskComplexity(str, Enum):
    """Task complexity levels for routing."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class FusionStrategy(str, Enum):
    """Response fusion strategies."""
    VOTING = "voting"
    RANKING = "ranking"
    MERGING = "merging"
    FIRST = "first"


class LLMRequest(BaseModel):
    """Request model for LLM queries."""
    prompt: str = Field(..., description="The prompt to send to the LLM")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for sampling")
    max_tokens: Optional[int] = Field(None, ge=1, description="Maximum tokens to generate")
    provider: Optional[LLMProvider] = Field(None, description="Specific provider to use")
    system_prompt: Optional[str] = Field(None, description="System prompt for the model")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LLMResponse(BaseModel):
    """Response model from LLM providers."""
    content: str = Field(..., description="The generated content")
    provider: LLMProvider = Field(..., description="Provider that generated the response")
    model: str = Field(..., description="Model that generated the response")
    tokens_used: int = Field(..., description="Number of tokens used")
    cost: float = Field(..., description="Cost of the request in USD")
    latency_ms: float = Field(..., description="Latency in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MultiLLMRequest(BaseModel):
    """Request model for multi-LLM queries."""
    prompt: str = Field(..., description="The prompt to send to LLMs")
    providers: Optional[List[LLMProvider]] = Field(None, description="Providers to query")
    fusion_strategy: FusionStrategy = Field(FusionStrategy.VOTING, description="Fusion strategy")
    parallel: bool = Field(True, description="Execute in parallel")
    task_complexity: Optional[TaskComplexity] = Field(None, description="Task complexity hint")
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1)
    system_prompt: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FusedResponse(BaseModel):
    """Response from the fusion layer."""
    final_content: str = Field(..., description="Final fused content")
    individual_responses: List[LLMResponse] = Field(..., description="Individual LLM responses")
    fusion_strategy: FusionStrategy = Field(..., description="Strategy used for fusion")
    total_cost: float = Field(..., description="Total cost across all providers")
    total_latency_ms: float = Field(..., description="Total latency")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProviderMetrics(BaseModel):
    """Metrics for a specific provider."""
    provider: LLMProvider
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    average_latency_ms: float = 0.0
    last_request_time: Optional[datetime] = None


class HealthCheck(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    providers: Dict[str, bool] = Field(default_factory=dict)
    version: str = "1.0.0"
