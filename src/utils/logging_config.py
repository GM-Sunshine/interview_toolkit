"""
Logging configuration for the Interview Toolkit.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    log_file = log_dir / "interview_toolkit.log"

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_formatter = logging.Formatter("%(levelname)s: %(message)s")

    # Create handlers
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1024 * 1024, backupCount=5  # 1MB
    )
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")

    return logger
