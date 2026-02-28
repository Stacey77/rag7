"""
Configuration management for RAG7 platform.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_env: str = "development"
    
    # LLM Provider API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Vector Database Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: Optional[str] = None
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    
    # Database Configuration
    database_url: str = "sqlite:///./rag7.db"
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "change_this_secret_key_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Enterprise Features
    enable_metrics: bool = True
    enable_tracing: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
