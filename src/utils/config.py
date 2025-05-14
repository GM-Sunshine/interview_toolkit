"""
Configuration module for the Interview Toolkit.

This module loads configuration from environment variables with sensible defaults.
"""

import os
from typing import Dict, Any, Optional

# API Configuration
API_TYPE = os.environ.get("API_TYPE", "openai").lower()  # 'openai' or 'ollama'

# OpenAI Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

# Ollama Configuration
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3:latest")

# Default settings
DEFAULT_QUESTION_COUNT = int(os.environ.get("DEFAULT_QUESTION_COUNT", "20"))
DEFAULT_BATCH_SIZE = int(os.environ.get("DEFAULT_BATCH_SIZE", "20"))
DEFAULT_TEMPERATURE = float(os.environ.get("DEFAULT_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.environ.get("DEFAULT_MAX_TOKENS", "2000"))
DEFAULT_API_TIMEOUT = int(
    os.environ.get("DEFAULT_API_TIMEOUT", "900")
)  # 15 minutes timeout

# PDF Configuration
DEFAULT_COLOR_SCHEME = os.environ.get("DEFAULT_COLOR_SCHEME", "blue")
DEFAULT_OUTPUT_DIR = os.environ.get("DEFAULT_OUTPUT_DIR", "pdf")
DEFAULT_JSON_DIR = os.environ.get("DEFAULT_JSON_DIR", "json")


def _validate_api_type(api_type: str, errors: Dict[str, str]) -> None:
    """Validate API type."""
    if api_type not in ["openai", "ollama"]:
        errors["API_TYPE"] = (
            f"Invalid API type: {api_type}. Must be 'openai' or 'ollama'"
        )


def _validate_openai_config(
    api_type: str, api_key: str, errors: Dict[str, str]
) -> None:
    """Validate OpenAI API configuration."""
    if api_type == "openai" and not api_key:
        errors["OPENAI_API_KEY"] = (
            "OpenAI API key is required when API_TYPE is 'openai'"
        )


def _validate_temperature(temperature: float, errors: Dict[str, str]) -> None:
    """Validate temperature."""
    if temperature < 0 or temperature > 1:
        errors["DEFAULT_TEMPERATURE"] = (
            f"Invalid temperature: {temperature}. Must be between 0 and 1"
        )


def _validate_max_tokens(max_tokens: int, errors: Dict[str, str]) -> None:
    """Validate max tokens."""
    if max_tokens <= 0:
        errors["DEFAULT_MAX_TOKENS"] = (
            f"Invalid max tokens: {max_tokens}. Must be greater than 0"
        )


def _validate_api_timeout(api_timeout: int, errors: Dict[str, str]) -> None:
    """Validate API timeout."""
    if api_timeout <= 0:
        errors["DEFAULT_API_TIMEOUT"] = (
            f"Invalid API timeout: {api_timeout}. Must be greater than 0"
        )


def validate_config() -> Dict[str, str]:
    """
    Validate the configuration and return any errors.

    Returns:
        A dictionary of error messages or an empty dict if no errors.
    """
    errors = {}

    # Validate API_TYPE
    _validate_api_type(API_TYPE, errors)

    # Validate OpenAI configuration
    _validate_openai_config(API_TYPE, OPENAI_API_KEY, errors)

    # Validate numeric values
    _validate_temperature(DEFAULT_TEMPERATURE, errors)
    _validate_max_tokens(DEFAULT_MAX_TOKENS, errors)
    _validate_api_timeout(DEFAULT_API_TIMEOUT, errors)

    return errors


def get_config(key: Optional[str] = None, default: Any = None) -> Any:
    """
    Get configuration values.

    Args:
        key: Optional key to retrieve a specific config value
        default: Default value to return if the key is not found

    Returns:
        Either a specific config value or the entire config dictionary
    """
    config = {
        "API_TYPE": API_TYPE,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "OPENAI_MODEL": OPENAI_MODEL,
        "OLLAMA_BASE_URL": OLLAMA_BASE_URL,
        "OLLAMA_MODEL": OLLAMA_MODEL,
        "DEFAULT_QUESTION_COUNT": DEFAULT_QUESTION_COUNT,
        "DEFAULT_BATCH_SIZE": DEFAULT_BATCH_SIZE,
        "DEFAULT_TEMPERATURE": DEFAULT_TEMPERATURE,
        "DEFAULT_MAX_TOKENS": DEFAULT_MAX_TOKENS,
        "DEFAULT_API_TIMEOUT": DEFAULT_API_TIMEOUT,
        "DEFAULT_COLOR_SCHEME": DEFAULT_COLOR_SCHEME,
        "DEFAULT_OUTPUT_DIR": DEFAULT_OUTPUT_DIR,
        "DEFAULT_JSON_DIR": DEFAULT_JSON_DIR,
    }

    if key is not None:
        return config.get(key, default)

    return config
