"""
Test configuration and setup.
"""
import pytest
from app.core.config import settings


def test_settings_loaded():
    """Test that settings can be loaded."""
    assert settings is not None
    assert settings.api_host is not None
    assert settings.api_port is not None


def test_default_values():
    """Test default configuration values."""
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8000
    assert settings.api_env == "development"
