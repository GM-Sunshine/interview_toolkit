#!/usr/bin/env python3
"""
Installation script for Interview Toolkit.

This script automates the setup process for the Interview Toolkit,
including creating necessary directories, installing dependencies,
and setting up the environment.
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


def run_command(command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
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


def check_python_version() -> bool:
    """
    Check if the Python version is compatible.
    
    Returns:
        True if the Python version is compatible, False otherwise
    """
    print_step("Checking Python version")
    
    major = sys.version_info.major
    minor = sys.version_info.minor
    required_major, required_minor = 3, 8
    
    if major < required_major or (major == required_major and minor < required_minor):
        print_error(f"Python {required_major}.{required_minor}+ is required, but found {major}.{minor}")
        return False
    
    print_success(f"Python version {major}.{minor} is compatible")
    return True


def create_directories() -> bool:
    """
    Create necessary directories.
    
    Returns:
        True if all directories were created successfully, False otherwise
    """
    print_step("Creating necessary directories")
    
    directories = ["json", "pdf", "logs"]
    success = True
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print_success(f"Created directory: {directory}")
        except Exception as e:
            print_error(f"Failed to create directory {directory}: {str(e)}")
            success = False
    
    # Create an empty .gitkeep file in each directory to ensure they're tracked in git
    for directory in directories:
        try:
            gitkeep_path = os.path.join(directory, ".gitkeep")
            with open(gitkeep_path, "w") as f:
                pass
            print_success(f"Created {gitkeep_path}")
        except Exception as e:
            print_warning(f"Failed to create .gitkeep in {directory}: {str(e)}")
    
    return success


def setup_virtual_environment() -> bool:
    """
    Set up a virtual environment.
    
    Returns:
        True if the virtual environment was set up successfully, False otherwise
    """
    print_step("Setting up virtual environment")
    
    # Check if venv module is available
    try:
        import venv
    except ImportError:
        print_error("The venv module is not available. Please install it first.")
        return False
    
    venv_path = "venv"
    
    # Check if virtual environment already exists
    if os.path.exists(venv_path):
        response = input(f"Virtual environment already exists at {venv_path}. Recreate? (y/n): ")
        if response.lower() == "y":
            try:
                shutil.rmtree(venv_path)
                print_success(f"Removed existing virtual environment at {venv_path}")
            except Exception as e:
                print_error(f"Failed to remove existing virtual environment: {str(e)}")
                return False
        else:
            print_warning("Using existing virtual environment")
            return True
    
    try:
        # Create virtual environment
        venv.create(venv_path, with_pip=True)
        print_success(f"Created virtual environment at {venv_path}")
        return True
    except Exception as e:
        print_error(f"Failed to create virtual environment: {str(e)}")
        return False


def install_dependencies(dev: bool = False) -> bool:
    """
    Install dependencies.
    
    Args:
        dev: Whether to install development dependencies
        
    Returns:
        True if dependencies were installed successfully, False otherwise
    """
    print_step("Installing dependencies")
    
    # Determine the Python executable path in the virtual environment
    if platform.system() == "Windows":
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Check if pip exists
    if not os.path.exists(pip_path):
        pip_path = "pip"  # Fallback to system pip
        print_warning("Using system pip - virtual environment may not be activated")
    
    # Upgrade pip first
    return_code, stdout, stderr = run_command([pip_path, "install", "--upgrade", "pip"])
    if return_code != 0:
        print_error(f"Failed to upgrade pip: {stderr}")
        return False
    
    print_success("Upgraded pip")
    
    # Install dependencies
    return_code, stdout, stderr = run_command([pip_path, "install", "-e", "."])
    if return_code != 0:
        print_error(f"Failed to install package: {stderr}")
        return False
    
    print_success("Installed package in development mode")
    
    # Install development dependencies if requested
    if dev:
        print_step("Installing development dependencies")
        
        # Install development dependencies
        return_code, stdout, stderr = run_command([pip_path, "install", "-e", ".[dev]"])
        if return_code != 0:
            print_error(f"Failed to install development dependencies: {stderr}")
            return False
        
        print_success("Installed development dependencies")
        
        # Install pre-commit hooks
        print_step("Installing pre-commit hooks")
        
        if platform.system() == "Windows":
            pre_commit_path = os.path.join("venv", "Scripts", "pre-commit")
        else:
            pre_commit_path = os.path.join("venv", "bin", "pre-commit")
        
        return_code, stdout, stderr = run_command([pre_commit_path, "install"])
        if return_code != 0:
            print_error(f"Failed to install pre-commit hooks: {stderr}")
            return False
        
        print_success("Installed pre-commit hooks")
    
    return True


def setup_environment_file() -> bool:
    """
    Set up the environment file.
    
    Returns:
        True if the environment file was set up successfully, False otherwise
    """
    print_step("Setting up environment file")
    
    env_example_path = ".env.example"
    env_path = ".env"
    
    # Check if .env already exists
    if os.path.exists(env_path):
        response = input(f"Environment file already exists at {env_path}. Overwrite? (y/n): ")
        if response.lower() != "y":
            print_warning("Using existing environment file")
            return True
    
    # Check if .env.example exists
    if not os.path.exists(env_example_path):
        print_error(f"Could not find {env_example_path}")
        return False
    
    try:
        # Copy .env.example to .env
        shutil.copy(env_example_path, env_path)
        print_success(f"Created environment file at {env_path}")
        
        # Prompt user to edit the environment file
        print_warning(f"Please edit {env_path} to set your API keys and other configuration")
        
        return True
    except Exception as e:
        print_error(f"Failed to create environment file: {str(e)}")
        return False


def run_tests() -> bool:
    """
    Run tests.
    
    Returns:
        True if tests passed, False otherwise
    """
    print_step("Running tests")
    
    # Determine the pytest executable path in the virtual environment
    if platform.system() == "Windows":
        pytest_path = os.path.join("venv", "Scripts", "pytest")
    else:
        pytest_path = os.path.join("venv", "bin", "pytest")
    
    # Check if pytest exists
    if not os.path.exists(pytest_path):
        print_warning("pytest not found, skipping tests")
        return True
    
    # Run tests
    return_code, stdout, stderr = run_command([pytest_path])
    if return_code != 0:
        print_error(f"Tests failed: {stderr}")
        return False
    
    print_success("Tests passed")
    return True


def print_activation_instructions() -> None:
    """Print instructions for activating the virtual environment."""
    print_step("Activating the virtual environment")
    
    if platform.system() == "Windows":
        print_colored("Run the following command to activate the virtual environment:", Colors.BLUE)
        print_colored("    venv\\Scripts\\activate", Colors.YELLOW)
    else:
        print_colored("Run the following command to activate the virtual environment:", Colors.BLUE)
        print_colored("    source venv/bin/activate", Colors.YELLOW)


def print_next_steps() -> None:
    """Print next steps for the user."""
    print_header("Next Steps")
    
    print_colored("1. Edit the .env file to set your API keys and other configuration", Colors.BLUE)
    print_colored("2. Activate the virtual environment", Colors.BLUE)
    print_colored("3. Run the application with:", Colors.BLUE)
    print_colored("    python interview_toolkit.py", Colors.YELLOW)
    
    print("\nFor more information, see the README.md file.")


def main() -> int:
    """
    Main entry point for the installation script.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print_header("Interview Toolkit Installation")
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Install Interview Toolkit")
    parser.add_argument("--dev", action="store_true", help="Install development dependencies")
    parser.add_argument("--no-venv", action="store_true", help="Skip virtual environment creation")
    parser.add_argument("--no-deps", action="store_true", help="Skip dependency installation")
    parser.add_argument("--no-env", action="store_true", help="Skip environment file setup")
    parser.add_argument("--no-tests", action="store_true", help="Skip running tests")
    args = parser.parse_args()
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    if not create_directories():
        print_warning("Failed to create some directories, but continuing installation")
    
    # Set up virtual environment
    if not args.no_venv:
        if not setup_virtual_environment():
            return 1
    else:
        print_warning("Skipping virtual environment creation")
    
    # Install dependencies
    if not args.no_deps:
        if not install_dependencies(dev=args.dev):
            return 1
    else:
        print_warning("Skipping dependency installation")
    
    # Set up environment file
    if not args.no_env:
        if not setup_environment_file():
            return 1
    else:
        print_warning("Skipping environment file setup")
    
    # Run tests
    if not args.no_tests and args.dev:
        if not run_tests():
            print_warning("Tests failed, but continuing installation")
    elif not args.no_tests:
        print_warning("Skipping tests (install with --dev to run tests)")
    else:
        print_warning("Skipping tests")
    
    # Print activation instructions
    if not args.no_venv:
        print_activation_instructions()
    
    # Print next steps
    print_next_steps()
    
    print_success("Installation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 