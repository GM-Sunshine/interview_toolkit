"""
Tests for the error handling module
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.utils.error_handling import (APIError, FileOperationError,
                                      InterviewToolkitError,
                                      PDFGenerationError,
                                      ensure_directory_exists, handle_error,
                                      validate_file_exists)


def test_interview_toolkit_error():
    """Test the base exception class"""
    # Test with just a message
    error = InterviewToolkitError("Test error")
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.details == {}

    # Test with message and details
    details = {"key": "value", "code": 123}
    error = InterviewToolkitError("Test error with details", details)
    assert error.message == "Test error with details"
    assert error.details == details


def test_api_error():
    """Test the API error class"""
    error = APIError("API error", {"status_code": 404})
    assert isinstance(error, InterviewToolkitError)
    assert error.message == "API error"
    assert error.details == {"status_code": 404}


def test_pdf_generation_error():
    """Test the PDF generation error class"""
    error = PDFGenerationError("PDF error", {"page": 5})
    assert isinstance(error, InterviewToolkitError)
    assert error.message == "PDF error"
    assert error.details == {"page": 5}


def test_file_operation_error():
    """Test the file operation error class"""
    error = FileOperationError("File error", {"path": "/test/path"})
    assert isinstance(error, InterviewToolkitError)
    assert error.message == "File error"
    assert error.details == {"path": "/test/path"}


def test_handle_error_api_error(caplog):
    """Test handling API errors"""
    with caplog.at_level(logging.ERROR):
        error = APIError("Test API error")
        handle_error(error)

    assert "Error occurred: Test API error" in caplog.text
    assert "API Error: Test API error" in caplog.text


def test_handle_error_pdf_error(caplog):
    """Test handling PDF generation errors"""
    with caplog.at_level(logging.ERROR):
        error = PDFGenerationError("Test PDF error")
        handle_error(error)

    assert "Error occurred: Test PDF error" in caplog.text
    assert "PDF Generation Error: Test PDF error" in caplog.text


def test_handle_error_file_error(caplog):
    """Test handling file operation errors"""
    with caplog.at_level(logging.ERROR):
        error = FileOperationError("Test file error")
        handle_error(error)

    assert "Error occurred: Test file error" in caplog.text
    assert "File Operation Error: Test file error" in caplog.text


def test_handle_error_generic(caplog):
    """Test handling generic errors"""
    with caplog.at_level(logging.ERROR):
        error = ValueError("Test generic error")
        handle_error(error, {"context_key": "context_value"})

    assert "Error occurred: Test generic error" in caplog.text
    assert "Unexpected error: Test generic error" in caplog.text
    # The context is added as 'extra' to the logger, which doesn't show up in caplog.text
    # So we just check that the log messages are correct


def test_ensure_directory_exists():
    """Test ensuring a directory exists"""
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        # Test successful directory creation
        path = Path("/test/path")
        ensure_directory_exists(path)
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Test failed directory creation
        mock_mkdir.reset_mock()
        mock_mkdir.side_effect = PermissionError("Permission denied")

        with pytest.raises(FileOperationError) as exc_info:
            ensure_directory_exists(path)

        assert "Failed to create directory:" in str(exc_info.value)
        assert "Permission denied" in str(exc_info.value.details)


def test_validate_file_exists():
    """Test validating a file exists"""
    test_path = Path("/test/path/file.txt")

    # Test file exists
    with patch("pathlib.Path.exists", return_value=True):
        # Should not raise an error
        validate_file_exists(test_path)

    # Test file does not exist
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(FileOperationError) as exc_info:
            validate_file_exists(test_path)

        assert "File does not exist:" in str(exc_info.value)
        assert str(test_path) in str(exc_info.value.details["path"])
