"""
LLM Provider module for the Interview Toolkit.

This module provides interfaces to different LLM providers (OpenAI, Ollama).
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
import threading

import requests
from openai import OpenAI

from src.utils.config import (
    API_TYPE,
    DEFAULT_API_TIMEOUT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    validate_config,
)


class LLMProviderException(Exception):
    """Base exception for LLM provider errors."""

    pass


class ConfigurationError(LLMProviderException):
    """Exception raised for configuration errors."""

    pass


class ConnectionError(LLMProviderException):
    """Exception raised for connection errors."""

    pass


class APIError(LLMProviderException):
    """Exception raised for API errors."""

    pass


class ParseError(LLMProviderException):
    """Exception raised for parsing errors."""

    pass


class RateLimitError(LLMProviderException):
    """Exception raised when rate limit is exceeded."""

    pass


class RateLimiter:
    """
    Token bucket rate limiter for API calls.

    Implements a token bucket algorithm to limit the rate of API calls.
    Tokens are added to the bucket at a constant rate, and each API call
    consumes one or more tokens.
    """

    def __init__(self, tokens_per_second: float, max_tokens: int = 60):
        """
        Initialize the rate limiter.

        Args:
            tokens_per_second: Rate at which tokens are added to the bucket
            max_tokens: Maximum number of tokens the bucket can hold
        """
        self.tokens_per_second = tokens_per_second
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.last_refill = time.time()
        self.lock = threading.Lock()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.tokens_per_second

        with self.lock:
            self.tokens = min(self.max_tokens, self.tokens + new_tokens)
            self.last_refill = now

    def consume(self, tokens: int = 1, wait: bool = True) -> bool:
        """
        Consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume
            wait: Whether to wait if tokens are not available

        Returns:
            True if tokens were consumed, False otherwise
        """
        self._refill()

        with self.lock:
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True

            if not wait:
                return False

            # Calculate wait time
            deficit = tokens - self.tokens
            wait_time = deficit / self.tokens_per_second

            # Wait for tokens
            time.sleep(wait_time)

            # Refill and consume
            self._refill()
            self.tokens -= tokens
            return True


# Create rate limiters for different providers
# OpenAI has a rate limit of 3 requests per second for free tier
openai_limiter = RateLimiter(
    tokens_per_second=3 / 60, max_tokens=3
)  # 3 tokens per minute
# Ollama has no official rate limit, but we'll be conservative
ollama_limiter = RateLimiter(
    tokens_per_second=10, max_tokens=20
)  # 10 tokens per second


def retry_with_exponential_backoff(
    func,
    max_retries: int = 5,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    errors_to_retry=(APIError, ConnectionError),
):
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Factor to increase delay by on each retry
        errors_to_retry: Exception types to retry on

    Returns:
        The result of the function

    Raises:
        The last exception raised by the function
    """
    delay = initial_delay
    last_exception = None

    for retry in range(max_retries + 1):
        try:
            return func()
        except errors_to_retry as e:
            last_exception = e

            if retry >= max_retries:
                break

            # Calculate delay with jitter
            jitter = 1 + 0.2 * (2 * (0.5 - 0.5))  # Add 20% random jitter
            current_delay = min(delay * jitter, max_delay)

            # Log retry information
            print(
                f"Retry {retry + 1}/{max_retries} after {current_delay:.2f}s due to: {str(e)}"
            )

            # Wait before retry
            time.sleep(current_delay)

            # Increase delay for next retry
            delay = min(delay * backoff_factor, max_delay)

    # If we got here, we failed all retries
    raise last_exception


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate_completion(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> str:
        """
        Generate a completion from the LLM provider.

        Args:
            system_prompt: The system prompt to send to the model
            user_prompt: The user prompt to send to the model
            **kwargs: Additional arguments to pass to the provider

        Returns:
            The generated text

        Raises:
            LLMProviderException: If there's an error generating the completion
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self):
        """
        Initialize the OpenAI provider.

        Raises:
            ConfigurationError: If the OpenAI API key is missing or invalid
        """
        # Validate configuration
        errors = validate_config()
        if "OPENAI_API_KEY" in errors:
            raise ConfigurationError(errors["OPENAI_API_KEY"])

        if not OPENAI_API_KEY:
            raise ConfigurationError(
                "OPENAI_API_KEY not found in environment variables"
            )

        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            self.model = OPENAI_MODEL
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize OpenAI client: {str(e)}")

    def generate_completion(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> str:
        """
        Generate a completion using the OpenAI API.

        Args:
            system_prompt: The system prompt to send to the model
            user_prompt: The user prompt to send to the model
            **kwargs: Additional arguments to pass to the API
                temperature: The temperature to use (default: DEFAULT_TEMPERATURE)
                max_tokens: The maximum tokens to generate (default: DEFAULT_MAX_TOKENS)
                debug: Whether to print debug information (default: False)

        Returns:
            The generated text

        Raises:
            APIError: If there's an error calling the OpenAI API
            ConfigurationError: If there's an error with the API key
            RateLimitError: If the rate limit is exceeded
        """
        debug = kwargs.get("debug", False)
        max_retries = kwargs.get("max_retries", 3)

        # Check rate limit
        if not openai_limiter.consume(1, wait=kwargs.get("wait_for_rate_limit", True)):
            raise RateLimitError(
                "OpenAI API rate limit exceeded. Please try again later."
            )

        def _generate_completion():
            if debug:
                print(f"Generating completion with OpenAI model: {self.model}")

            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=kwargs.get("temperature", DEFAULT_TEMPERATURE),
                    max_tokens=kwargs.get("max_tokens", DEFAULT_MAX_TOKENS),
                )
                return response.choices[0].message.content
            except Exception as e:
                error_message = str(e).lower()

                if debug:
                    print(f"OpenAI API error: {error_message}")

                if "insufficient_quota" in error_message:
                    raise APIError(
                        "OpenAI API key has insufficient quota. Please check your balance or use a different API key."
                    )
                elif "invalid_api_key" in error_message:
                    raise ConfigurationError(
                        "Invalid OpenAI API key. Please check your API key configuration."
                    )
                elif "rate_limit" in error_message:
                    raise RateLimitError(
                        "OpenAI API rate limit exceeded. Please try again later."
                    )
                else:
                    raise APIError(f"OpenAI API error: {str(e)}")

        # Retry with exponential backoff
        return retry_with_exponential_backoff(
            _generate_completion,
            max_retries=max_retries,
            errors_to_retry=(APIError, ConnectionError, RateLimitError),
        )


class OllamaProvider(LLMProvider):
    """Ollama API provider implementation."""

    def __init__(self):
        """
        Initialize the Ollama provider.

        Raises:
            ConfigurationError: If the Ollama configuration is invalid
            ConnectionError: If the Ollama server cannot be reached
        """
        self.base_url = OLLAMA_BASE_URL
        self.model = OLLAMA_MODEL

        # Test connection on initialization
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Could not connect to Ollama server at {self.base_url}. "
                "Please make sure Ollama is running and the URL is correct."
            )
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error connecting to Ollama server: {str(e)}")

    def generate_completion(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> str:
        """
        Generate a completion using the Ollama API.

        Args:
            system_prompt: The system prompt to send to the model
            user_prompt: The user prompt to send to the model
            **kwargs: Additional arguments to pass to the API
                temperature: The temperature to use (default: DEFAULT_TEMPERATURE)
                max_tokens: The maximum tokens to generate (default: DEFAULT_MAX_TOKENS)
                timeout: The timeout in seconds (default: DEFAULT_API_TIMEOUT)
                debug: Whether to print debug information (default: False)

        Returns:
            The generated text

        Raises:
            ConnectionError: If there's an error connecting to the Ollama server
            APIError: If there's an error calling the Ollama API
            ParseError: If there's an error parsing the response
            RateLimitError: If the rate limit is exceeded
        """
        debug = kwargs.get("debug", False)
        max_retries = kwargs.get("max_retries", 3)

        # Check rate limit
        if not ollama_limiter.consume(1, wait=kwargs.get("wait_for_rate_limit", True)):
            raise RateLimitError(
                "Ollama API rate limit exceeded. Please try again later."
            )

        def _generate_completion():
            url = f"{self.base_url}/api/chat"

            # Format messages for chat API
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", DEFAULT_TEMPERATURE),
                    "num_predict": kwargs.get("max_tokens", DEFAULT_MAX_TOKENS),
                },
            }

            try:
                # Use a longer timeout for the actual generation
                timeout = kwargs.get("timeout", DEFAULT_API_TIMEOUT)

                if debug:
                    print(
                        f"\nGenerating response with {self.model} (timeout: {timeout}s)..."
                    )
                    print(
                        "This may take a while depending on the model size and complexity of the request."
                    )
                    # Debug: Print request details
                    print(f"\nRequest URL: {url}")
                    print(f"Request payload: {json.dumps(payload, indent=2)}")

                response = requests.post(url, json=payload, timeout=timeout)

                if debug:
                    # Debug: Print response details
                    print(f"\nResponse status: {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")

                if response.status_code != 200:
                    error_msg = (
                        f"Ollama server returned error status: {response.status_code}"
                    )
                    if debug:
                        print(f"\n{error_msg}")
                        print(f"Response content: {response.text}")
                    raise APIError(error_msg)

                if not response.text:
                    raise APIError("Received empty response from Ollama server")

                try:
                    result = response.json()
                except json.JSONDecodeError as e:
                    if debug:
                        print(f"\nJSON Parse Error: {str(e)}")
                        print(f"Raw response content:\n{response.text}")
                    raise ParseError(
                        f"Invalid JSON response from Ollama server: {str(e)}"
                    )

                if "message" not in result or "content" not in result["message"]:
                    if debug:
                        print(
                            f"\nUnexpected response format. Full response:\n{json.dumps(result, indent=2)}"
                        )
                    raise ParseError("Invalid response format from Ollama server")

                # Extract the content from the response
                content = result["message"]["content"]

                # If the content starts with a description, try to extract just the JSON part
                if "[" in content:
                    json_start = content.find("[")
                    content = content[json_start:]

                # Try to parse the content as JSON to validate it
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    if debug:
                        print(f"\nGenerated content is not valid JSON: {str(e)}")
                        print(f"Content:\n{content}")
                    raise ParseError(f"Generated content is not valid JSON: {str(e)}")

                return content

            except requests.exceptions.ConnectionError:
                raise ConnectionError(
                    f"Lost connection to Ollama server at {self.base_url}. "
                    "Please check if Ollama is still running."
                )
            except requests.exceptions.Timeout:
                raise APIError(
                    f"Request to Ollama server timed out after {timeout} seconds. "
                    "The server might be overloaded or the model might be too large. "
                    f"Try increasing DEFAULT_API_TIMEOUT in your configuration (currently {timeout}s)."
                )
            except requests.exceptions.RequestException as e:
                if debug:
                    print(
                        f"\nRequest failed with status {getattr(e.response, 'status_code', 'N/A')}"
                    )
                    if hasattr(e, "response") and e.response is not None:
                        print(f"Response content: {e.response.text}")
                raise APIError(f"Error from Ollama server: {str(e)}")
            except (KeyError, json.JSONDecodeError) as e:
                raise ParseError(f"Invalid response from Ollama server: {str(e)}")

        # Retry with exponential backoff
        return retry_with_exponential_backoff(
            _generate_completion,
            max_retries=max_retries,
            errors_to_retry=(APIError, ConnectionError),
        )


def get_llm_provider() -> LLMProvider:
    """
    Factory function to get the appropriate LLM provider based on configuration.

    Returns:
        An instance of the configured LLM provider

    Raises:
        ConfigurationError: If the API type is not supported
        Other exceptions from the provider initialization
    """
    # Validate configuration
    errors = validate_config()
    if "API_TYPE" in errors:
        raise ConfigurationError(errors["API_TYPE"])

    if API_TYPE == "openai":
        return OpenAIProvider()
    elif API_TYPE == "ollama":
        return OllamaProvider()
    else:
        raise ConfigurationError(f"Unsupported API type: {API_TYPE}")
