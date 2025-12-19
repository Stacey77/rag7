"""Configuration management with environment-based loading and validation."""
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    database: str = Field(default="rag7_db", alias="POSTGRES_DB")
    user: str = Field(default="rag7_user", alias="POSTGRES_USER")
    password: str = Field(default="", alias="POSTGRES_PASSWORD")

    @property
    def url(self) -> str:
        """Get database URL."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class RedisConfig(BaseSettings):
    """Redis configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    db: int = Field(default=0, alias="REDIS_DB")

    @property
    def url(self) -> str:
        """Get Redis URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class QdrantConfig(BaseSettings):
    """Qdrant vector database configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    host: str = Field(default="localhost", alias="QDRANT_HOST")
    port: int = Field(default=6333, alias="QDRANT_PORT")
    api_key: Optional[str] = Field(default=None, alias="QDRANT_API_KEY")

    @property
    def url(self) -> str:
        """Get Qdrant URL."""
        return f"http://{self.host}:{self.port}"


class LLMConfig(BaseSettings):
    """LLM API configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    gemini_api_key: Optional[str] = Field(default=None, alias="GEMINI_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    mistral_api_key: Optional[str] = Field(default=None, alias="MISTRAL_API_KEY")
    litellm_proxy_url: str = Field(default="http://localhost:4000", alias="LITELLM_PROXY_URL")
    litellm_master_key: Optional[str] = Field(default=None, alias="LITELLM_MASTER_KEY")


class GoogleCloudConfig(BaseSettings):
    """Google Cloud Platform configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    project_id: Optional[str] = Field(default=None, alias="GOOGLE_PROJECT_ID")
    region: str = Field(default="us-central1", alias="GOOGLE_REGION")
    credentials_path: Optional[str] = Field(
        default=None, alias="GOOGLE_APPLICATION_CREDENTIALS"
    )


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    prometheus_url: str = Field(default="http://localhost:9090", alias="PROMETHEUS_URL")
    grafana_url: str = Field(default="http://localhost:3000", alias="GRAFANA_URL")
    jaeger_endpoint: str = Field(
        default="http://localhost:14268/api/traces", alias="JAEGER_ENDPOINT"
    )


class CircuitBreakerConfig(BaseSettings):
    """Circuit breaker configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    failure_threshold: int = Field(default=5, alias="CIRCUIT_BREAKER_FAILURE_THRESHOLD")
    timeout: int = Field(default=60, alias="CIRCUIT_BREAKER_TIMEOUT")
    recovery_timeout: int = Field(default=30, alias="CIRCUIT_BREAKER_RECOVERY_TIMEOUT")


class RateLimitConfig(BaseSettings):
    """Rate limiting configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    rpm: int = Field(default=60, alias="RATE_LIMIT_RPM")
    tpm: int = Field(default=100000, alias="RATE_LIMIT_TPM")


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8080, alias="APP_PORT")
    metrics_port: int = Field(default=9090, alias="METRICS_PORT")
    workers: int = Field(default=4, alias="WORKERS")
    max_agents: int = Field(default=10, alias="MAX_AGENTS")

    # Deployment
    deployment_env: str = Field(default="dev", alias="DEPLOYMENT_ENV")
    cloud_run_service_name: str = Field(
        default="rag7-agent-api", alias="CLOUD_RUN_SERVICE_NAME"
    )
    gke_cluster_name: str = Field(default="rag7-cluster", alias="GKE_CLUSTER_NAME")
    gke_namespace: str = Field(default="rag7-dev", alias="GKE_NAMESPACE")

    # Sub-configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    qdrant: QdrantConfig = Field(default_factory=QdrantConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    gcp: GoogleCloudConfig = Field(default_factory=GoogleCloudConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
