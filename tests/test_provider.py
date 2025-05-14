"""
Tests for the LLM provider module.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.llm.provider import (
    OllamaProvider,
    OpenAIProvider,
    APIError,
    ConnectionError,
    ParseError,
    ConfigurationError,
    get_llm_provider,
)

# Mock responses
MOCK_OPENAI_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": '[{"question": "Test question?", "answer": "Test answer."}]'
            }
        }
    ]
}

# Skip OpenAI tests if no API key is available or on CI
skip_openai = pytest.mark.skipif(
    os.environ.get("OPENAI_API_KEY") is None or os.environ.get("CI") == "true",
    reason="OpenAI API key not available or running in CI environment",
)


@skip_openai
def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    with patch("src.llm.provider.OPENAI_API_KEY", "test-key"), patch(
        "src.llm.provider.OpenAI"
    ) as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        provider = OpenAIProvider()
        assert provider.model is not None
        mock_client.assert_called_once_with(api_key="test-key")


@skip_openai
def test_openai_provider_missing_key():
    """Test OpenAI provider initialization with missing API key."""
    with patch("src.llm.provider.OPENAI_API_KEY", None):
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIProvider()
        assert "OPENAI_API_KEY not found" in str(exc_info.value)


@skip_openai
def test_openai_provider_generate_completion():
    """Test OpenAI provider question generation."""
    with patch("src.llm.provider.OPENAI_API_KEY", "test-key"), patch(
        "src.llm.provider.OpenAI"
    ) as mock_client:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content='[{"question": "Test?", "answer": "Test."}]'
                    )
                )
            ]
        )
        mock_client.return_value = mock_instance

        provider = OpenAIProvider()
        response = provider.generate_completion(
            system_prompt="Test system prompt", user_prompt="Test user prompt"
        )

        assert isinstance(response, str)
        assert json.loads(response)  # Verify it's valid JSON


@skip_openai
def test_openai_provider_error_handling():
    """Test OpenAI provider error handling."""
    with patch("src.llm.provider.OPENAI_API_KEY", "test-key"), patch(
        "src.llm.provider.OpenAI"
    ) as mock_client:
        mock_instance = MagicMock()

        # Test insufficient quota error
        mock_instance.chat.completions.create.side_effect = Exception(
            "insufficient_quota"
        )
        mock_client.return_value = mock_instance

        provider = OpenAIProvider()
        with pytest.raises(APIError) as exc_info:
            provider.generate_completion(
                system_prompt="Test system prompt", user_prompt="Test user prompt"
            )
        assert "insufficient quota" in str(exc_info.value).lower()

        # Test invalid API key error
        mock_instance.chat.completions.create.side_effect = Exception("invalid_api_key")
        with pytest.raises(ConfigurationError) as exc_info:
            provider.generate_completion(
                system_prompt="Test system prompt", user_prompt="Test user prompt"
            )
        assert "Invalid OpenAI API key" in str(exc_info.value)

        # Test generic error
        mock_instance.chat.completions.create.side_effect = Exception("Generic error")
        with pytest.raises(APIError) as exc_info:
            provider.generate_completion(
                system_prompt="Test system prompt", user_prompt="Test user prompt"
            )
        assert "OpenAI API error" in str(exc_info.value)


def test_get_llm_provider():
    """Test LLM provider factory function."""
    # Test OpenAI provider - skip if no API key
    if os.environ.get("OPENAI_API_KEY") is not None:
        with patch("src.llm.provider.API_TYPE", "openai"), patch(
            "src.llm.provider.OPENAI_API_KEY", "test-key"
        ), patch("src.llm.provider.OpenAI") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            provider = get_llm_provider()
            assert isinstance(provider, OpenAIProvider)
    else:
        # If no API key, just test that the code path works with mocks
        with patch("src.llm.provider.API_TYPE", "openai"), patch(
            "src.llm.provider.OPENAI_API_KEY", "test-key"
        ), patch("src.llm.provider.OpenAI") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            # Just verify we can call the function without errors
            with patch("src.llm.provider.OpenAIProvider") as mock_provider:
                mock_provider_instance = MagicMock()
                mock_provider.return_value = mock_provider_instance
                provider = get_llm_provider()
                assert provider is mock_provider_instance

    # Test Ollama provider with mocked connection
    with patch("src.llm.provider.API_TYPE", "ollama"), patch(
        "requests.get"
    ) as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        provider = get_llm_provider()
        assert isinstance(provider, OllamaProvider)

    # Test invalid provider type
    with patch("src.llm.provider.API_TYPE", "invalid"):
        with pytest.raises(ConfigurationError) as exc_info:
            get_llm_provider()
        assert "Unsupported API type" in str(exc_info.value)
