"""
LLM API endpoints for interacting with multiple LLM providers.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

from app.services.llm_service import LLMService, get_llm_service
from app.core.logging import app_logger

router = APIRouter()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class CompletionRequest(BaseModel):
    """Request model for LLM completion."""
    prompt: str = Field(..., description="The prompt to send to the LLM")
    provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    system_message: Optional[str] = Field(None, description="System message for the LLM")


class CompletionResponse(BaseModel):
    """Response model for LLM completion."""
    content: str
    provider: str
    model: str
    usage: Dict[str, Any]


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request model for chat completion."""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    provider: LLMProvider = Field(default=LLMProvider.OPENAI, description="LLM provider to use")
    model: Optional[str] = Field(None, description="Specific model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")


@router.post("/completion", response_model=CompletionResponse)
async def create_completion(
    request: CompletionRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate a completion using the specified LLM provider.
    
    This endpoint allows you to interact with multiple LLM providers
    (OpenAI, Anthropic, etc.) through a unified interface.
    """
    try:
        app_logger.info(f"Completion request for provider: {request.provider}")
        
        result = await llm_service.generate_completion(
            prompt=request.prompt,
            provider=request.provider.value,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_message=request.system_message
        )
        
        return result
    
    except Exception as e:
        app_logger.error(f"Error generating completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=CompletionResponse)
async def create_chat_completion(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate a chat completion using the specified LLM provider.
    
    This endpoint supports multi-turn conversations with context.
    """
    try:
        app_logger.info(f"Chat request for provider: {request.provider}")
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        result = await llm_service.generate_chat_completion(
            messages=messages,
            provider=request.provider.value,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return result
    
    except Exception as e:
        app_logger.error(f"Error generating chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers")
async def list_providers():
    """List available LLM providers and their models."""
    return {
        "providers": [
            {
                "name": "openai",
                "models": ["gpt-4", "gpt-4-turbo-preview", "gpt-3.5-turbo"],
                "capabilities": ["completion", "chat", "embeddings"]
            },
            {
                "name": "anthropic",
                "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
                "capabilities": ["completion", "chat"]
            }
        ]
    }
