#!/usr/bin/env python3
"""
Test runner script for the Interview Toolkit.

This script runs tests with coverage reporting and can generate HTML reports.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def print_colored(text: str, color: int) -> None:
    """Print colored text to the terminal."""
    print(f"\033[{color}m{text}\033[0m")


def print_header(text: str) -> None:
    """Print a header to the terminal."""
    print("\n" + "=" * 80)
    print_colored(f"  {text}", 95)
    print("=" * 80)


def print_step(text: str) -> None:
    """Print a step to the terminal."""
    print_colored(f"\n➤ {text}", 94)


def print_success(text: str) -> None:
    """Print a success message to the terminal."""
    print_colored(f"✓ {text}", 92)


def print_warning(text: str) -> None:
    """Print a warning to the terminal."""
    print_colored(f"⚠ {text}", 93)


def print_error(text: str) -> None:
    """Print an error to the terminal."""
    print_colored(f"✗ {text}", 91)


def run_command(
    command: List[str],
    cwd: Optional[str] = None,
    timeout: int = 300,
    env: Optional[dict] = None,
) -> Tuple[int, str, str]:
    """
    Run a command and return the exit code, stdout, and stderr.

    Args:
        command: Command to run as a list of strings
        cwd: Directory to run the command in
        timeout: Maximum time to wait for the command to complete (in seconds)
        env: Environment variables to set for the subprocess

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=cwd,
            env=env,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            process.kill()
            return (
                1,
                "",
                f"Command timed out after {timeout} seconds: {' '.join(command)}",
            )
    except Exception as e:
        return 1, "", str(e)


def run_pytest(
    pytest_args: List[str],
    with_coverage: bool = True,
    html_report: bool = False,
    xml_report: bool = False,
    output_dir: str = "coverage",
    timeout: int = 300,
    skip_external: bool = False,
) -> int:
    """
    Run pytest with the specified arguments.

    Args:
        pytest_args: Additional arguments to pass to pytest
        with_coverage: Whether to run with coverage
        html_report: Whether to generate an HTML coverage report
        xml_report: Whether to generate an XML coverage report
        output_dir: Directory for coverage reports
        timeout: Maximum time to wait for tests to complete (in seconds)
        skip_external: Whether to skip tests that require external services

    Returns:
        Exit code from pytest
    """
    print_step("Running tests")

    # Base pytest command
    command = ["pytest"]

    # Add coverage options if requested
    if with_coverage:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        command.extend(
            [
                "--cov=src",
                "--cov-report=term",
            ]
        )

        if html_report:
            command.append(f"--cov-report=html:{output_dir}/html")

        if xml_report:
            command.append(f"--cov-report=xml:{output_dir}/coverage.xml")

    # Add any additional arguments
    command.extend(pytest_args)

    # Set up environment for the subprocess
    env = os.environ.copy()
    if skip_external:
        env["CI"] = "true"
        print_warning("Skipping tests that require external services (OpenAI, Ollama)")

    # Run the command
    print_step(f"Executing: {' '.join(command)}")
    returncode, stdout, stderr = run_command(command, timeout=timeout, env=env)

    # Print output
    if stdout:
        print(stdout)
    if stderr:
        print_error(stderr)

    if returncode == 0:
        print_success("All tests passed!")
    else:
        print_error(f"Tests failed with exit code {returncode}")

    return returncode


def main() -> int:
    """
    Main entry point for the test runner script.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print_header("Interview Toolkit Test Runner")

    parser = argparse.ArgumentParser(description="Run tests for the Interview Toolkit")
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Run tests without coverage",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML coverage report",
    )
    parser.add_argument(
        "--xml",
        action="store_true",
        help="Generate XML coverage report",
    )
    parser.add_argument(
        "--output-dir",
        default="coverage",
        help="Directory for coverage reports (default: coverage)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Maximum time to wait for tests to complete in seconds (default: 300)",
    )
    parser.add_argument(
        "--skip-external",
        action="store_true",
        help="Skip tests that require external services",
    )
    parser.add_argument(
        "pytest_args",
        nargs="*",
        help="Additional arguments to pass to pytest",
    )

    args = parser.parse_args()

    # Run tests
    return run_pytest(
        pytest_args=args.pytest_args,
        with_coverage=not args.no_coverage,
        html_report=args.html,
        xml_report=args.xml,
        output_dir=args.output_dir,
        timeout=args.timeout,
        skip_external=args.skip_external,
    )


if __name__ == "__main__":
    sys.exit(main())
