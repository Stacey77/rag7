"""Configuration settings for the LangGraph multi-agent system."""

import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = ""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Agent Configuration
    agent_max_iterations: int = 10
    quality_threshold: float = 0.8

    # Model Configuration
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 4096

    # LangChain Configuration
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "agentic-patterns"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    """Get application settings singleton."""
    return Settings()
