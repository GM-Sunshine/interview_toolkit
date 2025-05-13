#!/usr/bin/env python3
"""
Release script for the Interview Toolkit.

This script automates the release process by:
1. Bumping the version in version.py
2. Creating a commit for the version bump
3. Creating a tag for the release
4. Pushing the commit and tag to the remote repository
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Literal, Optional, Tuple, Union

VERSION_FILE = Path("src/utils/version.py")
VERSION_PATTERN = r'^__version__\s*=\s*["\']([\d.]+)["\']'
CHANGELOG_FILE = Path("CHANGELOG.md")


class Colors:
    """Terminal colors for output formatting."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text: str, color: str) -> None:
    """Print colored text to the terminal."""
    print(f"{color}{text}{Colors.ENDC}")


def print_header(text: str) -> None:
    """Print a header to the terminal."""
    print("\n" + "=" * 80)
    print_colored(f"  {text}", Colors.HEADER + Colors.BOLD)
    print("=" * 80)


def print_step(text: str) -> None:
    """Print a step to the terminal."""
    print_colored(f"\n➤ {text}", Colors.BLUE)


def print_success(text: str) -> None:
    """Print a success message to the terminal."""
    print_colored(f"✓ {text}", Colors.GREEN)


def print_warning(text: str) -> None:
    """Print a warning to the terminal."""
    print_colored(f"⚠ {text}", Colors.YELLOW)


def print_error(text: str) -> None:
    """Print an error to the terminal."""
    print_colored(f"✗ {text}", Colors.RED)


def run_command(command: list[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """
    Run a command and return the exit code, stdout, and stderr.
    
    Args:
        command: Command to run as a list of strings
        cwd: Directory to run the command in
        
    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)


def get_current_version() -> str:
    """
    Get the current version from the version file.
    
    Returns:
        Current version string
    """
    if not VERSION_FILE.exists():
        print_error(f"Version file not found at {VERSION_FILE}")
        sys.exit(1)
        
    content = VERSION_FILE.read_text()
    match = re.search(VERSION_PATTERN, content, re.MULTILINE)
    
    if not match:
        print_error(f"Could not find version in {VERSION_FILE}")
        sys.exit(1)
        
    return match.group(1)


def bump_version(
    current_version: str, 
    bump_type: Literal["major", "minor", "patch"]
) -> str:
    """
    Bump the version according to semantic versioning.
    
    Args:
        current_version: Current version string
        bump_type: Type of version bump (major, minor, or patch)
        
    Returns:
        New version string
    """
    major, minor, patch = map(int, current_version.split("."))
    
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    
    return f"{major}.{minor}.{patch}"


def update_version_file(new_version: str) -> None:
    """
    Update the version in the version file.
    
    Args:
        new_version: New version string
    """
    if not VERSION_FILE.exists():
        print_error(f"Version file not found at {VERSION_FILE}")
        sys.exit(1)
        
    content = VERSION_FILE.read_text()
    new_content = re.sub(
        VERSION_PATTERN,
        f'__version__ = "{new_version}"',
        content,
        flags=re.MULTILINE
    )
    
    VERSION_FILE.write_text(new_content)
    print_success(f"Updated version to {new_version} in {VERSION_FILE}")


def update_changelog(new_version: str, message: str) -> None:
    """
    Update the changelog with the new version.
    
    Args:
        new_version: New version string
        message: Release message
    """
    if not CHANGELOG_FILE.exists():
        print_warning(f"Changelog file not found at {CHANGELOG_FILE}. Creating it.")
        CHANGELOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHANGELOG_FILE.write_text("# Changelog\n\n")
    
    content = CHANGELOG_FILE.read_text()
    today = subprocess.check_output(["date", "+%Y-%m-%d"]).decode().strip()
    
    new_entry = f"## [{new_version}] - {today}\n\n{message}\n\n"
    
    # Insert after the first line (the title)
    lines = content.splitlines()
    if len(lines) < 2:
        # If the file is too short, just append
        new_content = content + "\n" + new_entry
    else:
        # Otherwise, insert after the title
        new_content = lines[0] + "\n\n" + new_entry + "\n".join(lines[1:])
    
    CHANGELOG_FILE.write_text(new_content)
    print_success(f"Updated changelog at {CHANGELOG_FILE}")


def create_git_commit(new_version: str) -> bool:
    """
    Create a git commit for the version bump.
    
    Args:
        new_version: New version string
        
    Returns:
        True if successful, False otherwise
    """
    print_step("Creating git commit")
    
    # Check if git is available
    returncode, _, _ = run_command(["git", "--version"])
    if returncode != 0:
        print_error("Git not found. Please install git.")
        return False
    
    # Check if working directory is clean
    returncode, stdout, _ = run_command(["git", "status", "--porcelain"])
    if returncode != 0:
        print_error("Failed to check git status.")
        return False
    
    # If there are uncommitted changes other than the version files, ask user to commit them first
    uncommitted = stdout.strip()
    if uncommitted and any(
        not line.strip().endswith(str(VERSION_FILE)) and 
        not line.strip().endswith(str(CHANGELOG_FILE)) 
        for line in uncommitted.splitlines()
    ):
        print_warning("There are uncommitted changes. Please commit them first.")
        print(uncommitted)
        return False
    
    # Add the version file
    returncode, _, stderr = run_command(["git", "add", str(VERSION_FILE)])
    if returncode != 0:
        print_error(f"Failed to add version file to git: {stderr}")
        return False
    
    # Add the changelog file
    if CHANGELOG_FILE.exists():
        returncode, _, stderr = run_command(["git", "add", str(CHANGELOG_FILE)])
        if returncode != 0:
            print_error(f"Failed to add changelog file to git: {stderr}")
            return False
    
    # Create commit
    commit_message = f"Bump version to {new_version}"
    returncode, _, stderr = run_command(["git", "commit", "-m", commit_message])
    if returncode != 0:
        print_error(f"Failed to create git commit: {stderr}")
        return False
    
    print_success(f"Created git commit: {commit_message}")
    return True


def create_git_tag(new_version: str) -> bool:
    """
    Create a git tag for the release.
    
    Args:
        new_version: New version string
        
    Returns:
        True if successful, False otherwise
    """
    print_step(f"Creating git tag v{new_version}")
    
    # Create tag
    tag_name = f"v{new_version}"
    tag_message = f"Release {new_version}"
    returncode, _, stderr = run_command(["git", "tag", "-a", tag_name, "-m", tag_message])
    if returncode != 0:
        print_error(f"Failed to create git tag: {stderr}")
        return False
    
    print_success(f"Created git tag: {tag_name}")
    return True


def push_to_remote(new_version: str, remote: str = "origin") -> bool:
    """
    Push the commit and tag to the remote repository.
    
    Args:
        new_version: New version string
        remote: Remote repository name
        
    Returns:
        True if successful, False otherwise
    """
    print_step(f"Pushing to remote {remote}")
    
    # Push commit
    returncode, _, stderr = run_command(["git", "push", remote])
    if returncode != 0:
        print_error(f"Failed to push commit: {stderr}")
        return False
    
    # Push tag
    tag_name = f"v{new_version}"
    returncode, _, stderr = run_command(["git", "push", remote, tag_name])
    if returncode != 0:
        print_error(f"Failed to push tag: {stderr}")
        return False
    
    print_success(f"Pushed commit and tag to {remote}")
    return True


def main() -> int:
    """
    Main entry point for the release script.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print_header("Interview Toolkit Release")
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Release a new version of the Interview Toolkit")
    parser.add_argument(
        "bump_type", 
        choices=["major", "minor", "patch"],
        help="Type of version bump"
    )
    parser.add_argument(
        "--message", "-m",
        help="Release message for the changelog",
        default="",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the commit and tag to the remote repository",
    )
    parser.add_argument(
        "--remote",
        default="origin",
        help="Remote repository name (default: origin)",
    )
    args = parser.parse_args()
    
    # Get current version
    current_version = get_current_version()
    print_step(f"Current version: {current_version}")
    
    # Bump version
    new_version = bump_version(current_version, args.bump_type)
    print_step(f"New version: {new_version}")
    
    # Update version file
    update_version_file(new_version)
    
    # Update changelog
    if args.message:
        update_changelog(new_version, args.message)
    else:
        message = input("Enter a release message for the changelog: ")
        if message:
            update_changelog(new_version, message)
        else:
            print_warning("No release message provided. Skipping changelog update.")
    
    # Create git commit
    if not create_git_commit(new_version):
        return 1
    
    # Create git tag
    if not create_git_tag(new_version):
        return 1
    
    # Push to remote
    if args.push:
        if not push_to_remote(new_version, args.remote):
            return 1
    else:
        print_warning(f"Not pushing to remote. To push, run: git push {args.remote} && git push {args.remote} v{new_version}")
    
    print_success(f"Released version {new_version}")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 