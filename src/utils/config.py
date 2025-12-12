"""Configuration management for the RAG7 AI Agent Platform."""
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4"
    
    # Slack Integration
    slack_bot_token: str = ""
    slack_app_token: str = ""
    slack_signing_secret: str = ""
    
    # Gmail Integration
    gmail_credentials_file: Optional[str] = None
    gmail_token_file: Optional[str] = None
    gmail_smtp_user: Optional[str] = None
    gmail_smtp_password: Optional[str] = None
    
    # Notion Integration
    notion_api_key: str = ""
    notion_database_id: str = ""
    
    # Database Configuration
    database_url: str = "sqlite:///./rag7.db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # ChromaDB Configuration
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_persistence_dir: str = "./chroma_data"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Environment
    environment: str = "development"
    log_level: str = "INFO"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment."""
    global _settings
    _settings = Settings()
    return _settings
