"""Unit tests for configuration module."""
import os
import pytest
from src.config import Settings, DatabaseConfig, RedisConfig


@pytest.mark.unit
def test_database_config_url():
    """Test database URL generation."""
    config = DatabaseConfig(
        host="localhost",
        port=5432,
        database="test_db",
        user="test_user",
        password="test_pass",
    )
    assert config.url == "postgresql+asyncpg://test_user:test_pass@localhost:5432/test_db"


@pytest.mark.unit
def test_redis_config_url_without_password():
    """Test Redis URL generation without password."""
    config = RedisConfig(
        host="localhost",
        port=6379,
        db=0,
    )
    assert config.url == "redis://localhost:6379/0"


@pytest.mark.unit
def test_redis_config_url_with_password():
    """Test Redis URL generation with password."""
    config = RedisConfig(
        host="localhost",
        port=6379,
        password="secret",
        db=0,
    )
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
def test_settings_environment_validation():
    """Test environment validation."""
    with pytest.raises(ValueError):
        Settings(environment="invalid")


@pytest.mark.unit
def test_settings_log_level_validation():
    """Test log level validation."""
    with pytest.raises(ValueError):
        Settings(log_level="INVALID")
