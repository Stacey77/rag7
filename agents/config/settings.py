"""
Platform Configuration Settings
"""
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class PlatformSettings(BaseSettings):
    """Platform configuration settings"""
    
    # Platform Info
    platform_name: str = "Agentic Infrastructure Platform"
    version: str = "0.1.0"
    environment: str = "development"
    
    # Agent Configuration
    enable_policy_agent: bool = True
    enable_intent_agent: bool = True
    enable_deployment_agent: bool = True
    enable_compliance_agent: bool = True
    enable_inference_agent: bool = True
    
    # OPA Configuration
    use_opa: bool = False
    opa_url: str = "http://localhost:8181"
    
    # AI Configuration
    use_ai: bool = False
    openai_api_key: Optional[str] = None
    ai_model: str = "gpt-4"
    
    # gRPC Configuration
    grpc_host: str = "0.0.0.0"
    grpc_port: int = 50051
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Kubernetes Configuration
    k8s_namespace: str = "default"
    k8s_config_path: Optional[str] = None
    
    # Multi-Region Configuration
    default_regions: list = Field(default_factory=lambda: ["us-east-1", "us-west-2"])
    
    # Logging
    log_level: str = "INFO"
    
    # Security
    enable_auth: bool = False
    jwt_secret: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = PlatformSettings()
