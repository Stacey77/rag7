"""Unit tests for configuration module."""
import os
import pytest
from src.config import Settings, DatabaseConfig, RedisConfig


@pytest.mark.unit
def test_database_config_url(monkeypatch):
    """Test database URL generation."""
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_pass")
    
    config = DatabaseConfig()
    assert config.url == "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"


@pytest.mark.unit
def test_redis_config_url_without_password(monkeypatch):
    """Test Redis URL generation without password."""
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_DB", "0")
    
    config = RedisConfig()
    assert config.url == "redis://localhost:6379/0"


@pytest.mark.unit
def test_redis_config_url_with_password(monkeypatch):
    """Test Redis URL generation with password."""
    monkeypatch.setenv("REDIS_HOST", "localhost")
    monkeypatch.setenv("REDIS_PORT", "6379")
    monkeypatch.setenv("REDIS_PASSWORD", "secret")
    monkeypatch.setenv("REDIS_DB", "0")
    
    config = RedisConfig()
    assert config.url == "redis://:secret@localhost:6379/0"


@pytest.mark.unit
def test_settings_defaults():
    """Test default settings values."""
    settings = Settings()
    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.app_port == 8080
    assert settings.is_development is True
    assert settings.is_production is False


@pytest.mark.unit
def test_settings_environment_validation(monkeypatch):
    """Test environment validation."""
    monkeypatch.setenv("ENVIRONMENT", "invalid")
    with pytest.raises(ValueError, match="Environment must be one of"):
        Settings()


@pytest.mark.unit
def test_settings_log_level_validation(monkeypatch):
    """Test log level validation."""
    monkeypatch.setenv("LOG_LEVEL", "INVALID")
    with pytest.raises(ValueError, match="Log level must be one of"):
        Settings()
