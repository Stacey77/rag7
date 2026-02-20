"""Configuration utilities for the vision module."""

import os
from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).parent


def load_config(name: str) -> dict:
    """Load a YAML config file from the config directory.

    Args:
        name: Config file name without extension (e.g. ``"detection_config"``).

    Returns:
        Parsed YAML as a plain :class:`dict`.
    """
    path = CONFIG_DIR / f"{name}.yaml"
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}
