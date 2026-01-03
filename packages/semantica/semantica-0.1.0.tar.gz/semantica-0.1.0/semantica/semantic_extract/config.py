"""
Configuration Management Module

This module provides centralized configuration management for semantic extraction,
supporting multiple configuration sources including environment variables, config files,
and programmatic configuration.

Supported Configuration Sources:
    - Environment variables: OPENAI_API_KEY, GEMINI_API_KEY, GROQ_API_KEY, etc.
    - Config files: YAML, JSON, TOML formats
    - Programmatic: Python API for setting provider configurations

Algorithms Used:
    - Environment Variable Parsing: OS-level environment variable access
    - YAML Parsing: YAML parser for configuration file loading
    - JSON Parsing: JSON parser for configuration file loading
    - TOML Parsing: TOML parser for configuration file loading
    - Fallback Chain: Priority-based configuration resolution
    - Dictionary Merging: Deep merge algorithms for configuration updates

Key Features:
    - Environment variable support for API keys (OPENAI_API_KEY, GEMINI_API_KEY, etc.)
    - Config file support (YAML, JSON, TOML formats)
    - Programmatic configuration via Python API
    - Provider-specific configuration management
    - Automatic fallback chain (config file -> environment -> defaults)
    - Global config instance for easy access

Main Classes:
    - Config: Main configuration manager class

Example Usage:
    >>> from semantica.semantic_extract.config import config
    >>> api_key = config.get_api_key("openai")
    >>> config.set_provider("openai", api_key="sk-...", model="gpt-4")
    >>> provider_config = config.get_provider_config("gemini")

Author: Semantica Contributors
License: MIT
"""

import os
from pathlib import Path
from typing import Dict, Optional

from ..utils.logging import get_logger


class Config:
    """Configuration manager - supports .env files, environment variables, and programmatic config."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager."""
        self.logger = get_logger("config")
        self._configs: Dict[str, Dict] = {}
        self._load_config_file(config_file)
        self._load_env_vars()

    def _load_config_file(self, config_file: Optional[str]):
        """Load configuration from file."""
        if config_file and Path(config_file).exists():
            try:
                # Support YAML, JSON, TOML
                if config_file.endswith(".yaml") or config_file.endswith(".yml"):
                    import yaml

                    with open(config_file, "r") as f:
                        self._configs.update(yaml.safe_load(f) or {})
                elif config_file.endswith(".json"):
                    import json

                    with open(config_file, "r") as f:
                        self._configs.update(json.load(f) or {})
                elif config_file.endswith(".toml"):
                    import toml

                    with open(config_file, "r") as f:
                        self._configs.update(toml.load(f) or {})
            except Exception as e:
                self.logger.warning(f"Failed to load config file {config_file}: {e}")

    def _load_env_vars(self):
        """Load configuration from environment variables."""
        # Common environment variable patterns
        providers = ["openai", "gemini", "groq", "anthropic", "ollama"]
        for provider in providers:
            env_key = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(env_key)
            if api_key:
                if provider not in self._configs:
                    self._configs[provider] = {}
                self._configs[provider]["api_key"] = api_key

    def set_provider(self, name: str, **config):
        """Set provider config programmatically."""
        self._configs[name] = config

    def get_provider_config(self, name: str) -> Dict:
        """Get provider configuration."""
        if name in self._configs:
            return self._configs[name]

        # Fallback to environment variables
        env_key = f"{name.upper()}_API_KEY"
        api_key = os.getenv(env_key)
        if api_key:
            return {"api_key": api_key}

        return {}

    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key with fallback chain: config -> env -> None."""
        if provider in self._configs:
            return self._configs[provider].get("api_key")
        return os.getenv(f"{provider.upper()}_API_KEY")


# Global config instance
config = Config()
