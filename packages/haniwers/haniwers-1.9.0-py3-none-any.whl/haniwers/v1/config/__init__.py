"""Configuration module for loading and validating haniwers settings.

This package provides:
- `config.model`: Pydantic models for configuration sections
- `config.loader`: Logic to find and load configuration files
- `config.generator`: Logic to create configuration files
"""

from .model import HaniwersConfig
from .loader import ConfigLoader

__all__ = ["HaniwersConfig", "ConfigLoader"]
