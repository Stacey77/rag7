"""
RAG7 Multi-LLM Orchestration Framework

A comprehensive framework for orchestrating multiple LLMs (GPT-4, Claude, Gemini)
with intelligent routing, response fusion, and observability.
"""

__version__ = "1.0.0"
__author__ = "Stacey77"

from rag7.models import (
    LLMRequest,
    LLMResponse,
    MultiLLMRequest,
    FusedResponse,
    LLMProvider,
    TaskComplexity,
    FusionStrategy,
)
from rag7.orchestrator import orchestrator
from rag7.fusion import response_fusion
from rag7.monitoring import monitoring_service
from rag7.config import config_manager

__all__ = [
    "LLMRequest",
    "LLMResponse",
    "MultiLLMRequest",
    "FusedResponse",
    "LLMProvider",
    "TaskComplexity",
    "FusionStrategy",
    "orchestrator",
    "response_fusion",
    "monitoring_service",
    "config_manager",
]
