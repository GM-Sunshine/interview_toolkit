"""Logging utilities for the Interview Toolkit."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

# Define log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Default date format
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default log directory
DEFAULT_LOG_DIR = "logs"


def get_log_level(level_name: Optional[str] = None) -> int:
    """
    Get the logging level constant from a string.
    
    Args:
        level_name: Name of the log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                   If None, will try to get from environment variable LOG_LEVEL
                   
    Returns:
        Logging level constant
    """
    if level_name is None:
        level_name = os.environ.get("LOG_LEVEL", "INFO")
        
    level_name = level_name.upper()
    return LOG_LEVELS.get(level_name, logging.INFO)


def setup_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    log_file: Optional[str] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    propagate: bool = False,
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.
    
    Args:
        name: Name of the logger
        level: Log level (either a string or a logging constant)
        log_file: Path to the log file (None for no file logging)
        log_format: Format for log messages
        date_format: Format for timestamps
        propagate: Whether to propagate logs to parent loggers
        
    Returns:
        Configured logger
    """
    # Convert level to int if it's a string
    if isinstance(level, str):
        level = get_log_level(level)
    elif level is None:
        level = get_log_level()
    
    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_default_log_file(name: str) -> str:
    """
    Get the default log file path for a module.
    
    Args:
        name: Name of the module
        
    Returns:
        Default log file path
    """
    # Create log directory if it doesn't exist
    os.makedirs(DEFAULT_LOG_DIR, exist_ok=True)
    
    # Create a log file name with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    return os.path.join(DEFAULT_LOG_DIR, f"{name}_{timestamp}.log")


def get_logger(
    name: str,
    level: Optional[Union[str, int]] = None,
    log_file: Optional[str] = None,
    with_timestamp: bool = True,
) -> logging.Logger:
    """
    Get a configured logger.
    
    Args:
        name: Name of the logger
        level: Log level (either a string or a logging constant)
        log_file: Path to the log file (None for automatic file path)
        with_timestamp: Whether to include a timestamp in the automatic file path
        
    Returns:
        Configured logger
    """
    # Determine log file path
    if log_file is None:
        log_file = get_default_log_file(name)
    
    # Set up logger
    return setup_logger(name, level, log_file)


# Create a default logger for the application
app_logger = get_logger("interview_toolkit") 