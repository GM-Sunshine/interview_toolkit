"""
Tests for the logging configuration module.
"""

import logging
import pytest
from unittest.mock import patch, MagicMock, call


class MockFormatter:
    def __init__(self, fmt):
        self._fmt = fmt


@patch("logging.getLogger")
@patch("pathlib.Path.mkdir")
@patch("logging.handlers.RotatingFileHandler")
@patch("logging.StreamHandler")
@patch("logging.Formatter")
def test_setup_logging_creates_directory(
    mock_formatter, mock_stream, mock_rotating, mock_mkdir, mock_get_logger
):
    """Test that setup_logging creates the logs directory if it doesn't exist."""
    # Set up mocks
    mock_logger = MagicMock()
    mock_root_logger = MagicMock()
    mock_stream_instance = MagicMock()
    mock_rotating_instance = MagicMock()
    mock_file_formatter = MockFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    mock_console_formatter = MockFormatter("%(levelname)s: %(message)s")

    # Configure returns
    mock_get_logger.side_effect = [mock_root_logger, mock_logger]
    mock_stream.return_value = mock_stream_instance
    mock_rotating.return_value = mock_rotating_instance
    mock_formatter.side_effect = [mock_file_formatter, mock_console_formatter]

    # Call the function to test
    from src.utils.logging_config import setup_logging

    setup_logging()

    # Verify directory creation
    mock_mkdir.assert_called_once_with(exist_ok=True)


@patch("logging.getLogger")
@patch("pathlib.Path.mkdir")
@patch("logging.handlers.RotatingFileHandler")
@patch("logging.StreamHandler")
@patch("logging.Formatter")
def test_setup_logging_returns_logger(
    mock_formatter, mock_stream, mock_rotating, mock_mkdir, mock_get_logger
):
    """Test that setup_logging returns a logger instance."""
    # Set up mocks
    mock_logger = MagicMock()
    mock_root_logger = MagicMock()
    mock_stream_instance = MagicMock()
    mock_rotating_instance = MagicMock()

    # Configure returns
    mock_get_logger.side_effect = [mock_root_logger, mock_logger]
    mock_stream.return_value = mock_stream_instance
    mock_rotating.return_value = mock_rotating_instance

    # Call the function to test
    from src.utils.logging_config import setup_logging

    logger = setup_logging()

    # Verify logger is returned
    assert logger == mock_logger

    # Verify handlers were added to root logger
    assert mock_root_logger.addHandler.call_count == 2

    # Check log level set to INFO
    mock_root_logger.setLevel.assert_called_once_with(logging.INFO)


@patch("logging.getLogger")
@patch("pathlib.Path.mkdir")
@patch("logging.handlers.RotatingFileHandler")
@patch("logging.StreamHandler")
@patch("logging.Formatter")
def test_setup_logging_formatters(
    mock_formatter, mock_stream, mock_rotating, mock_mkdir, mock_get_logger
):
    """Test that setup_logging configures the correct formatters."""
    # Set up mocks
    mock_logger = MagicMock()
    mock_root_logger = MagicMock()
    mock_stream_instance = MagicMock()
    mock_rotating_instance = MagicMock()

    # Configure returns
    mock_get_logger.side_effect = [mock_root_logger, mock_logger]
    mock_stream.return_value = mock_stream_instance
    mock_rotating.return_value = mock_rotating_instance

    # Call the function to test
    from src.utils.logging_config import setup_logging

    setup_logging()

    # Verify formatters were created with correct formats
    formatter_calls = mock_formatter.call_args_list
    assert len(formatter_calls) == 2

    # Check file formatter format string
    file_format = formatter_calls[0].args[0]
    assert "%(asctime)s" in file_format
    assert "%(name)s" in file_format
    assert "%(levelname)s" in file_format
    assert "%(message)s" in file_format

    # Check console formatter format string
    console_format = formatter_calls[1].args[0]
    assert "%(levelname)s" in console_format
    assert "%(message)s" in console_format


def test_logging_rotation_settings():
    """Test that the logging rotation settings are defined correctly."""
    import inspect
    import os
    from src.utils import logging_config

    # Get the source code of the module
    source_file = inspect.getsourcefile(logging_config)
    with open(source_file, "r") as f:
        source_code = f.read()

    # Look for rotation settings in the source code
    assert (
        "maxBytes=1024 * 1024" in source_code
    ), "MaxBytes setting not found in source code"
    assert (
        "backupCount=5" in source_code
    ), "BackupCount setting not found in source code"
    assert (
        "interview_toolkit.log" in source_code
    ), "Log filename not found in source code"
