"""
Configuration management for RAG7 agents.
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

from dotenv import load_dotenv


class Config:
    """
    Configuration manager for RAG7 multi-LLM system.
    
    Loads configuration from environment variables and config files.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file (optional)
        """
        # Load environment variables
        if env_file and Path(env_file).exists():
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env if exists
        
        self.logger = logging.getLogger("config")
    
    def get_gpt4_config(self) -> Dict[str, Any]:
        """
        Get GPT-4 agent configuration.
        
        Returns:
            Configuration dictionary for GPT-4 agent
        """
        return {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("GPT4_MODEL", "gpt-4"),
            "max_tokens": int(os.getenv("GPT4_MAX_TOKENS", "2048")),
            "temperature": float(os.getenv("GPT4_TEMPERATURE", "0.7")),
        }
    
    def get_fusion_config(self) -> Dict[str, Any]:
        """
        Get fusion layer configuration.
        
        Returns:
            Configuration dictionary for fusion layer
        """
        return {
            "strategy": os.getenv("FUSION_STRATEGY", "consensus"),
            "separator": os.getenv("FUSION_SEPARATOR", "\n\n---\n\n"),
            "weights": self._parse_weights(os.getenv("FUSION_WEIGHTS", "")),
        }
    
    def _parse_weights(self, weights_str: str) -> Dict[str, float]:
        """
        Parse agent weights from string.
        
        Format: "gpt4:1.0,claude:0.9,gemini:0.8"
        
        Args:
            weights_str: Comma-separated weight specifications
            
        Returns:
            Dictionary mapping agent names to weights
        """
        if not weights_str:
            return {}
        
        weights = {}
        try:
            for pair in weights_str.split(","):
                if ":" in pair:
                    agent, weight = pair.split(":")
                    weights[agent.strip()] = float(weight.strip())
        except Exception as e:
            self.logger.warning(f"Failed to parse weights: {e}")
        
        return weights
    
    def setup_logging(
        self,
        level: str = "INFO",
        log_file: Optional[str] = None
    ):
        """
        Setup logging configuration.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Optional log file path
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        
        # Configure root logger
        handlers = [logging.StreamHandler()]
        
        if log_file:
            handlers.append(logging.FileHandler(log_file))
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        
        self.logger.info(f"Logging configured at {level} level")
