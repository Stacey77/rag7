"""Tests for configuration management."""
import pytest
from pathlib import Path
import tempfile
import yaml
from rag7.config import ConfigManager, ProviderConfig, RouterConfig, FusionConfig


def test_config_manager_initialization():
    """Test config manager initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        manager = ConfigManager(str(config_path))
        
        assert manager.config is not None
        assert "providers" in manager.config
        assert "router" in manager.config
        assert "fusion" in manager.config


def test_provider_config():
    """Test provider configuration."""
    config = ProviderConfig(
        enabled=True,
        default_model="gpt-4",
        max_tokens=1000,
        temperature=0.7,
        timeout=30,
        max_retries=3
    )
    
    assert config.enabled is True
    assert config.default_model == "gpt-4"
    assert config.max_tokens == 1000


def test_router_config():
    """Test router configuration."""
    config = RouterConfig(
        default_provider="openai",
        enable_fallback=True,
        fallback_chain=["openai", "anthropic", "google"]
    )
    
    assert config.default_provider == "openai"
    assert config.enable_fallback is True
    assert len(config.fallback_chain) == 3


def test_fusion_config():
    """Test fusion configuration."""
    config = FusionConfig(
        default_strategy="voting",
        min_agreement_threshold=0.6,
        enable_quality_ranking=True
    )
    
    assert config.default_strategy == "voting"
    assert config.min_agreement_threshold == 0.6
    assert config.enable_quality_ranking is True


def test_config_manager_get_provider_config():
    """Test getting provider configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        manager = ConfigManager(str(config_path))
        
        openai_config = manager.get_provider_config("openai")
        assert openai_config.default_model == "gpt-4"


def test_config_manager_get_router_config():
    """Test getting router configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        manager = ConfigManager(str(config_path))
        
        router_config = manager.get_router_config()
        assert router_config.default_provider == "openai"
        assert router_config.enable_fallback is True


def test_config_manager_save_and_load():
    """Test saving and loading configuration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.yaml"
        
        # Create manager and modify config
        manager1 = ConfigManager(str(config_path))
        manager1.config["test_key"] = "test_value"
        manager1._save_config()
        
        # Create new manager and verify it loads the saved config
        manager2 = ConfigManager(str(config_path))
        assert manager2.config.get("test_key") == "test_value"
