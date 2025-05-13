"""
Tests for the LLM provider module.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.llm.provider import (
    OllamaProvider, OpenAIProvider, APIError, 
    ConnectionError, ParseError, ConfigurationError,
    get_llm_provider
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

MOCK_OLLAMA_RESPONSE = {
    "message": {"content": '[{"question": "Test question?", "answer": "Test answer."}]'}
}


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


def test_openai_provider_missing_key():
    """Test OpenAI provider initialization with missing API key."""
    with patch("src.llm.provider.OPENAI_API_KEY", None):
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIProvider()
        assert "OPENAI_API_KEY not found" in str(exc_info.value)


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


def test_ollama_provider_initialization():
    """Test Ollama provider initialization."""
    with patch("requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200)
        provider = OllamaProvider()
        assert provider.model is not None
        assert provider.base_url is not None


def test_ollama_provider_connection_error():
    """Test Ollama provider initialization with connection error."""
    with patch("requests.get") as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        with pytest.raises(ConnectionError) as exc_info:
            OllamaProvider()
        assert "Could not connect to Ollama server" in str(exc_info.value)


def test_ollama_provider_generate_completion():
    """Test Ollama provider question generation."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock successful initialization
        mock_get.return_value = MagicMock(status_code=200)

        # Mock successful generation
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_OLLAMA_RESPONSE
        )

        provider = OllamaProvider()
        response = provider.generate_completion(
            system_prompt="Test system prompt", user_prompt="Test user prompt"
        )

        assert isinstance(response, str)
        assert json.loads(response)  # Verify it's valid JSON


def test_ollama_provider_debug_mode():
    """Test Ollama provider in debug mode."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post, patch(
        "builtins.print"
    ) as mock_print:
        # Mock successful initialization
        mock_get.return_value = MagicMock(status_code=200)

        # Mock successful generation
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: MOCK_OLLAMA_RESPONSE
        )

        provider = OllamaProvider()
        response = provider.generate_completion(
            system_prompt="Test system prompt",
            user_prompt="Test user prompt",
            debug=True,
        )

        # Verify debug info was printed
        assert mock_print.call_count > 0
        assert isinstance(response, str)
        assert json.loads(response)  # Verify it's valid JSON


def test_ollama_provider_empty_response():
    """Test Ollama provider with empty response."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock successful initialization
        mock_get.return_value = MagicMock(status_code=200)

        # Mock empty response
        mock_post.return_value = MagicMock(status_code=200, text="")

        provider = OllamaProvider()
        with pytest.raises(APIError) as exc_info:
            provider.generate_completion(
                system_prompt="Test system prompt", user_prompt="Test user prompt"
            )
        assert "Received empty response" in str(exc_info.value)


def test_ollama_provider_json_decode_error():
    """Test Ollama provider with JSON decode error."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock successful initialization
        mock_get.return_value = MagicMock(status_code=200)

        # Mock invalid JSON response
        mock_post.return_value = MagicMock(
            status_code=200,
            text="invalid json",
            json=MagicMock(side_effect=json.JSONDecodeError("Invalid JSON", "", 0)),
        )

        provider = OllamaProvider()
        with pytest.raises(ParseError) as exc_info:
            provider.generate_completion(
                system_prompt="Test system prompt", user_prompt="Test user prompt"
            )
        assert "Invalid JSON response" in str(exc_info.value)


def test_ollama_provider_invalid_response_format():
    """Test Ollama provider with invalid response format."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock successful initialization
        mock_get.return_value = MagicMock(status_code=200)

        # Mock response with invalid format
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: {"invalid": "format"}
        )

        provider = OllamaProvider()
        with pytest.raises(ParseError) as exc_info:
            provider.generate_completion(
                system_prompt="Test system prompt", user_prompt="Test user prompt"
            )
        assert "Invalid response format" in str(exc_info.value)


def test_ollama_provider_timeout():
    """Test Ollama provider timeout handling."""
    with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
        # Mock successful initialization
        mock_get.return_value = MagicMock(status_code=200)

        # Mock timeout
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        provider = OllamaProvider()
        with pytest.raises(APIError) as exc_info:
            provider.generate_completion(
                system_prompt="Test system prompt", user_prompt="Test user prompt"
            )
        assert "Request to Ollama server timed out" in str(exc_info.value)


def test_get_llm_provider():
    """Test LLM provider factory function."""
    # Test OpenAI provider
    with patch("src.llm.provider.API_TYPE", "openai"), patch(
        "src.llm.provider.OPENAI_API_KEY", "test-key"
    ), patch("src.llm.provider.OpenAI") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        provider = get_llm_provider()
        assert isinstance(provider, OpenAIProvider)

    # Test Ollama provider
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
