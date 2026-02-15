"""
Platform Configuration Settings
"""
from typing import Dict, Any, Optional, List
import os


class PlatformSettings:
    """Platform configuration settings"""
    
    def __init__(self):
        # Platform Info
        self.platform_name = "Agentic Infrastructure Platform"
        self.version = "0.1.0"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Agent Configuration
        self.enable_policy_agent = True
        self.enable_intent_agent = True
        self.enable_deployment_agent = True
        self.enable_compliance_agent = True
        self.enable_inference_agent = True
        
        # OPA Configuration
        self.use_opa = os.getenv("USE_OPA", "false").lower() == "true"
        self.opa_url = os.getenv("OPA_URL", "http://localhost:8181")
        
        # AI Configuration
        self.use_ai = os.getenv("USE_AI", "false").lower() == "true"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ai_model = os.getenv("AI_MODEL", "gpt-4")
        
        # gRPC Configuration
        self.grpc_host = os.getenv("GRPC_HOST", "0.0.0.0")
        self.grpc_port = int(os.getenv("GRPC_PORT", "50051"))
        
        # API Configuration
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        self.api_workers = int(os.getenv("API_WORKERS", "4"))
        
        # Kubernetes Configuration
        self.k8s_namespace = os.getenv("K8S_NAMESPACE", "default")
        self.k8s_config_path = os.getenv("K8S_CONFIG_PATH")
        
        # Multi-Region Configuration
        self.default_regions = ["us-east-1", "us-west-2"]
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Security
        self.enable_auth = os.getenv("ENABLE_AUTH", "false").lower() == "true"
        self.jwt_secret = os.getenv("JWT_SECRET")


# Global settings instance
settings = PlatformSettings()
