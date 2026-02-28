"""
AGI System - Core Configuration Module
Manages system-wide configuration and settings
"""
import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ModelConfig(BaseModel):
    """Configuration for AI models"""
    default_model: str = Field(default="gpt-4")
    embedding_model: str = Field(default="text-embedding-ada-002")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2000, gt=0)


class VectorDBConfig(BaseModel):
    """Configuration for vector database"""
    db_type: str = Field(default="chromadb")
    persist_dir: str = Field(default="./data/chroma")
    collection_name: str = Field(default="agi_knowledge")


class MemoryConfig(BaseModel):
    """Configuration for memory systems"""
    memory_type: str = Field(default="in-memory")
    redis_host: Optional[str] = None
    redis_port: Optional[int] = None
    max_short_term_memories: int = Field(default=10)
    max_long_term_memories: int = Field(default=1000)


class JavaServiceConfig(BaseModel):
    """Configuration for Java service integration"""
    host: str = Field(default="localhost")
    port: int = Field(default=50051)
    timeout: int = Field(default=30)


class AGIConfig(BaseModel):
    """Main AGI system configuration"""
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    model: ModelConfig = Field(default_factory=ModelConfig)
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    java_service: JavaServiceConfig = Field(default_factory=JavaServiceConfig)
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="./logs/agi_system.log")
    
    class Config:
        env_prefix = ""


def get_config() -> AGIConfig:
    """Get the global AGI configuration"""
    return AGIConfig()


# Global configuration instance
config = get_config()
