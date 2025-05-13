"""
Custom error handling for the Interview Toolkit.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Type

logger = logging.getLogger(__name__)


class InterviewToolkitError(Exception):
    """Base exception class for Interview Toolkit."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class APIError(InterviewToolkitError):
    """Raised when there's an error with the API."""

    pass


class PDFGenerationError(InterviewToolkitError):
    """Raised when there's an error generating a PDF."""

    pass


class FileOperationError(InterviewToolkitError):
    """Raised when there's an error with file operations."""

    pass


def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Handle errors in a consistent way across the application.

    Args:
        error: The exception that was raised
        context: Additional context about the error
    """
    context = context or {}

    # Log the error
    logger.error(
        f"Error occurred: {str(error)}",
        extra={"error_type": error.__class__.__name__, "context": context},
    )

    # Handle specific error types
    if isinstance(error, APIError):
        logger.error("API Error: %s", error.message)
    elif isinstance(error, PDFGenerationError):
        logger.error("PDF Generation Error: %s", error.message)
    elif isinstance(error, FileOperationError):
        logger.error("File Operation Error: %s", error.message)
    else:
        logger.error("Unexpected error: %s", str(error))


def ensure_directory_exists(path: Path) -> None:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: The directory path to ensure exists

    Raises:
        FileOperationError: If the directory cannot be created
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileOperationError(
            f"Failed to create directory: {path}", {"error": str(e)}
        )


def validate_file_exists(path: Path) -> None:
    """
    Validate that a file exists.

    Args:
        path: The file path to validate

    Raises:
        FileOperationError: If the file does not exist
    """
    if not path.exists():
        raise FileOperationError(f"File does not exist: {path}", {"path": str(path)})
