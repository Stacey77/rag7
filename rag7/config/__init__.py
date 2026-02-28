"""Configuration management for the multi-LLM framework."""
import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from pydantic_settings import BaseSettings


class ProviderConfig(BaseModel):
    """Configuration for a single LLM provider."""
    enabled: bool = True
    api_key: Optional[str] = None
    default_model: str
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    max_retries: int = 3
    cost_per_1k_tokens: Dict[str, float] = Field(default_factory=dict)


class RouterConfig(BaseModel):
    """Configuration for the router/orchestrator."""
    default_provider: str = "openai"
    enable_fallback: bool = True
    fallback_chain: List[str] = Field(default_factory=lambda: ["openai", "anthropic", "google"])
    task_complexity_routing: Dict[str, str] = Field(
        default_factory=lambda: {
            "simple": "openai",
            "medium": "anthropic",
            "complex": "google"
        }
    )
    cost_optimization: bool = True
    latency_optimization: bool = False


class FusionConfig(BaseModel):
    """Configuration for response fusion."""
    default_strategy: str = "voting"
    min_agreement_threshold: float = 0.6
    enable_quality_ranking: bool = True
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "openai": 1.0,
            "anthropic": 1.0,
            "google": 1.0
        }
    )


class MonitoringConfig(BaseModel):
    """Configuration for monitoring and observability."""
    enable_prometheus: bool = True
    enable_cost_tracking: bool = True
    enable_latency_tracking: bool = True
    log_level: str = "INFO"
    metrics_port: int = 9090


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = ConfigDict(env_file=".env", case_sensitive=False)
    
    # API Keys
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(None, alias="OPENAI_ORG_ID")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(None, alias="GOOGLE_API_KEY")
    
    # Application settings
    default_llm_provider: str = Field("openai", alias="DEFAULT_LLM_PROVIDER")
    enable_parallel_execution: bool = Field(True, alias="ENABLE_PARALLEL_EXECUTION")
    enable_cost_tracking: bool = Field(True, alias="ENABLE_COST_TRACKING")
    max_retries: int = Field(3, alias="MAX_RETRIES")
    request_timeout: int = Field(30, alias="REQUEST_TIMEOUT")
    
    # FastAPI settings
    api_host: str = Field("0.0.0.0", alias="API_HOST")
    api_port: int = Field(8000, alias="API_PORT")
    api_reload: bool = Field(False, alias="API_RELOAD")


class ConfigManager:
    """Manages configuration loading and access."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.settings = Settings()
        self.config_path = config_path or "config.yaml"
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file if exists."""
        config_file = Path(self.config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            # Create default config
            self.config = self._get_default_config()
            self._save_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "providers": {
                "openai": {
                    "enabled": True,
                    "default_model": "gpt-4",
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "timeout": 30,
                    "max_retries": 3,
                    "cost_per_1k_tokens": {
                        "gpt-4": 0.03,
                        "gpt-3.5-turbo": 0.002
                    }
                },
                "anthropic": {
                    "enabled": True,
                    "default_model": "claude-3-opus-20240229",
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "timeout": 30,
                    "max_retries": 3,
                    "cost_per_1k_tokens": {
                        "claude-3-opus-20240229": 0.015,
                        "claude-3-sonnet-20240229": 0.003
                    }
                },
                "google": {
                    "enabled": True,
                    "default_model": "gemini-pro",
                    "max_tokens": 1000,
                    "temperature": 0.7,
                    "timeout": 30,
                    "max_retries": 3,
                    "cost_per_1k_tokens": {
                        "gemini-pro": 0.001
                    }
                }
            },
            "router": {
                "default_provider": "openai",
                "enable_fallback": True,
                "fallback_chain": ["openai", "anthropic", "google"],
                "task_complexity_routing": {
                    "simple": "openai",
                    "medium": "anthropic",
                    "complex": "google"
                },
                "cost_optimization": True,
                "latency_optimization": False
            },
            "fusion": {
                "default_strategy": "voting",
                "min_agreement_threshold": 0.6,
                "enable_quality_ranking": True,
                "weights": {
                    "openai": 1.0,
                    "anthropic": 1.0,
                    "google": 1.0
                }
            },
            "monitoring": {
                "enable_prometheus": True,
                "enable_cost_tracking": True,
                "enable_latency_tracking": True,
                "log_level": "INFO",
                "metrics_port": 9090
            }
        }
    
    def _save_config(self):
        """Save configuration to YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get_provider_config(self, provider: str) -> ProviderConfig:
        """Get configuration for a specific provider."""
        provider_data = self.config.get("providers", {}).get(provider, {})
        return ProviderConfig(**provider_data)
    
    def get_router_config(self) -> RouterConfig:
        """Get router configuration."""
        router_data = self.config.get("router", {})
        return RouterConfig(**router_data)
    
    def get_fusion_config(self) -> FusionConfig:
        """Get fusion configuration."""
        fusion_data = self.config.get("fusion", {})
        return FusionConfig(**fusion_data)
    
    def get_monitoring_config(self) -> MonitoringConfig:
        """Get monitoring configuration."""
        monitoring_data = self.config.get("monitoring", {})
        return MonitoringConfig(**monitoring_data)


# Global config manager instance
config_manager = ConfigManager()
