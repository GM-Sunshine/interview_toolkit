"""
Tests for the configuration module.
"""
import os
from unittest import mock

import pytest

from src.utils.config import (API_TYPE, DEFAULT_BATCH_SIZE, DEFAULT_QUESTION_COUNT,
                           DEFAULT_TEMPERATURE, OLLAMA_BASE_URL, OPENAI_API_KEY,
                           get_config, validate_config)
# Import internal function for direct testing
from src.utils.config import _validate_api_type


@pytest.fixture
def mock_env_vars():
    """Fixture to set up mock environment variables for testing."""
    with mock.patch.dict(os.environ, {
        "API_TYPE": "openai",
        "OPENAI_API_KEY": "mock_api_key",
        "OPENAI_MODEL": "gpt-3.5-turbo",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3:latest",
        "DEFAULT_QUESTION_COUNT": "25",
        "DEFAULT_BATCH_SIZE": "10",
        "DEFAULT_TEMPERATURE": "0.8",
        "DEFAULT_MAX_TOKENS": "1500",
        "DEFAULT_API_TIMEOUT": "600",
        "DEFAULT_COLOR_SCHEME": "blue",
        "DEFAULT_OUTPUT_DIR": "test_pdf",
        "DEFAULT_JSON_DIR": "test_json",
    }):
        yield


class TestConfig:
    """Tests for the configuration module."""

    def test_config_default_values(self):
        """Test that config values have sensible defaults."""
        assert API_TYPE in ["openai", "ollama"]
        assert isinstance(DEFAULT_QUESTION_COUNT, int)
        assert isinstance(DEFAULT_BATCH_SIZE, int)
        assert isinstance(DEFAULT_TEMPERATURE, float)
        assert 0 <= DEFAULT_TEMPERATURE <= 1, "Temperature should be between 0 and 1"
        
    def test_get_config(self):
        """Test that get_config returns a dictionary with all config values."""
        config = get_config()
        assert isinstance(config, dict)
        assert "API_TYPE" in config
        assert "OPENAI_API_KEY" in config
        assert "OPENAI_MODEL" in config
        assert "OLLAMA_BASE_URL" in config
        assert "OLLAMA_MODEL" in config
        assert "DEFAULT_QUESTION_COUNT" in config
        assert "DEFAULT_BATCH_SIZE" in config
        assert "DEFAULT_TEMPERATURE" in config
        assert "DEFAULT_MAX_TOKENS" in config
        assert "DEFAULT_API_TIMEOUT" in config
        assert "DEFAULT_COLOR_SCHEME" in config
        assert "DEFAULT_OUTPUT_DIR" in config
        assert "DEFAULT_JSON_DIR" in config
        
    def test_validate_config_valid(self, mock_env_vars):
        """Test that validate_config returns no errors for valid config."""
        errors = validate_config()
        assert not errors, f"Unexpected errors: {errors}"
        
    def test_validate_config_invalid_api_type(self):
        """Test that validate_config catches invalid API type."""
        # Test by directly calling the validation function with an invalid value
        errors = {}
        _validate_api_type("invalid_type", errors)
        assert "API_TYPE" in errors
        assert "Invalid API type" in errors["API_TYPE"]
            
    def test_validate_config_missing_openai_key(self):
        """Test that validate_config catches missing OpenAI API key."""
        errors = {}
        from src.utils.config import _validate_openai_config
        _validate_openai_config("openai", "", errors)
        assert "OPENAI_API_KEY" in errors
        assert "OpenAI API key is required" in errors["OPENAI_API_KEY"]
            
    def test_validate_config_invalid_temperature(self):
        """Test that validate_config catches invalid temperature."""
        errors = {}
        from src.utils.config import _validate_temperature
        _validate_temperature(1.5, errors)
        assert "DEFAULT_TEMPERATURE" in errors
        assert "Invalid temperature" in errors["DEFAULT_TEMPERATURE"]
            
    def test_validate_config_invalid_max_tokens(self):
        """Test that validate_config catches invalid max tokens."""
        errors = {}
        from src.utils.config import _validate_max_tokens
        _validate_max_tokens(0, errors)
        assert "DEFAULT_MAX_TOKENS" in errors
        assert "Invalid max tokens" in errors["DEFAULT_MAX_TOKENS"]
            
    def test_validate_config_invalid_api_timeout(self):
        """Test that validate_config catches invalid API timeout."""
        errors = {}
        from src.utils.config import _validate_api_timeout
        _validate_api_timeout(-10, errors)
        assert "DEFAULT_API_TIMEOUT" in errors
        assert "Invalid API timeout" in errors["DEFAULT_API_TIMEOUT"] 