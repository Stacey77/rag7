"""
Pydantic models for request/response validation and documentation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


# Authentication Models
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


# Flow Models
class FlowResponse(BaseModel):
    filename: str
    uploaded_at: Optional[datetime] = None


class FlowListResponse(BaseModel):
    flows: List[str]
    count: int


class FlowRunRequest(BaseModel):
    user_input: str = Field(..., max_length=5000)


class FlowRunResponse(BaseModel):
    result: str
    execution_time: Optional[float] = None
    flow_name: Optional[str] = None


# RAG Models
class EmbedTextRequest(BaseModel):
    texts: List[str] = Field(..., min_items=1, max_items=100)
    collection_name: str = Field(default="text_embeddings", max_length=255)
    
    @validator('texts')
    def validate_texts(cls, v):
        for text in v:
            if len(text) > 10000:
                raise ValueError('Each text must be less than 10000 characters')
        return v


class EmbedTextResponse(BaseModel):
    message: str
    collection_name: str
    embedded_count: int
    ids: List[str]


class SearchRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    collection_name: str = Field(default="text_embeddings")
    top_k: int = Field(default=5, ge=1, le=100)


class SearchResult(BaseModel):
    id: str
    text: str
    score: float
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    collection_name: str


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=5000)
    collection_name: str = Field(default="text_embeddings")
    top_k: int = Field(default=5, ge=1, le=100)


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    context: List[SearchResult]
    collection_name: str


class CollectionInfo(BaseModel):
    name: str
    entity_count: int
    description: Optional[str] = None


class CollectionsResponse(BaseModel):
    collections: List[CollectionInfo]
    count: int


# Error Response Model
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Health Check Model
class HealthResponse(BaseModel):
    status: str
    services: Dict[str, bool]
    version: str = "1.0.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
