"""
Version information for Interview Toolkit.

This module provides version information for the Interview Toolkit.
"""

import os
import sys
from typing import Dict, Tuple


# Version information
__version__ = "0.6.0"  # Use semantic versioning: MAJOR.MINOR.PATCH


def parse_version(version_str: str) -> Tuple[int, int, int]:
    """
    Parse a version string into a tuple of (major, minor, patch).
    
    Args:
        version_str: Version string in format "MAJOR.MINOR.PATCH"
        
    Returns:
        Tuple of (major, minor, patch)
        
    Raises:
        ValueError: If the version string is not in the correct format
    """
    try:
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")
            
        return tuple(int(part) for part in parts)
    except Exception as e:
        raise ValueError(f"Failed to parse version: {str(e)}")


def get_version() -> str:
    """
    Get the current version of the Interview Toolkit.
    
    Returns:
        Version string
    """
    return __version__


def get_version_info() -> Dict[str, str]:
    """
    Get detailed version information.
    
    Returns:
        Dictionary containing version information
    """
    return {
        "version": __version__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
    }


def check_version_compatibility(required_version: str) -> bool:
    """
    Check if the current version is compatible with the required version.
    
    Args:
        required_version: Required version in format "MAJOR.MINOR.PATCH"
        
    Returns:
        True if compatible, False otherwise
    """
    try:
        current = parse_version(__version__)
        required = parse_version(required_version)
        
        # Check major version
        if current[0] != required[0]:
            return False
            
        # If major versions match but minor version is lower, not compatible
        if current[1] < required[1]:
            return False
            
        # If major and minor versions match but patch is lower, it's up to the caller
        # to decide if that's a problem, but generally it should be fine
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    # When run directly, print version information
    print(f"Interview Toolkit version: {get_version()}")
    version_info = get_version_info()
    for key, value in version_info.items():
        print(f"{key}: {value}")
