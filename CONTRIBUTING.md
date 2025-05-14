# Contributing to Interview Toolkit

Thank you for your interest in contributing to the Interview Toolkit! This document provides guidelines for contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment

## Development Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings
```

## Code Quality

We use the following tools for quality assurance:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pytest**: Testing

Run pre-commit hooks to ensure code quality:

```bash
pre-commit install  # Only needed once
pre-commit run --all-files
```

## Type Checking

We're gradually adding type annotations to the codebase. See [TYPING.md](TYPING.md) for details on our type checking strategy.

To run mypy with our current settings:

```bash
python scripts/run_mypy.py
```

## Testing

There are two ways to run tests:

### Using pytest directly

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_config.py
```

### Using the test runner script

We provide a convenient script to run tests with additional options:

```bash
# Run all tests
python scripts/run_tests.py

# Skip tests that require external services (OpenAI, Ollama)
python scripts/run_tests.py --skip-external

# Set a timeout to prevent tests from hanging
python scripts/run_tests.py --timeout 60

# Generate HTML coverage report
python scripts/run_tests.py --html

# Run specific tests
python scripts/run_tests.py -- tests/test_config.py
```

### Writing Tests

- Write tests for new features and bug fixes
- Tests should be in the `tests/` directory
- Use the skip decorators for tests that require external services:

```python
@skip_openai
def test_that_needs_openai():
    # This test will be skipped in CI environments
    ...

@skip_ollama
def test_that_needs_ollama():
    # This test will be skipped in CI environments
    ...
```

## Pull Request Process

1. Create a branch for your feature or fix
2. Make your changes
3. Run tests and code quality checks
4. Submit a pull request
5. Fill in the PR template with relevant information

## Issue Reporting

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment information

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

Thank you for contributing to the Interview Toolkit! 