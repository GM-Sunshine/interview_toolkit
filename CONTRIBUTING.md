# Contributing to Interview Toolkit

Thank you for your interest in contributing to the Interview Toolkit! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Coding Standards](#coding-standards)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [your.email@example.com](mailto:your.email@example.com).

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/interview_toolkit.git
   cd interview_toolkit
   ```
3. Add the original repository as an upstream remote:
   ```bash
   git remote add upstream https://github.com/original-owner/interview_toolkit.git
   ```
4. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

1. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

4. Create a local configuration file:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## Coding Standards

We use several tools to maintain code quality:

- **Black**: For code formatting (line length: 88 characters)
- **isort**: For import sorting
- **flake8**: For linting
- **mypy**: For static type checking
- **pylint**: For additional linting

Run them all at once using pre-commit:
```bash
pre-commit run --all-files
```

### Style Guidelines

- Use type hints for all function parameters and return values
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- Write clear docstrings for all modules, classes, and functions
- Use descriptive variable names
- Keep functions focused on a single responsibility
- Comment complex logic, but prefer readable code over comments

Example function with proper formatting:

```python
def calculate_score(answers: List[str], reference: List[str]) -> float:
    """
    Calculate score based on answers compared to reference.
    
    Args:
        answers: List of user-provided answers
        reference: List of reference answers to compare against
        
    Returns:
        The calculated score as a float between 0 and 1
        
    Raises:
        ValueError: If the lists are of different lengths
    """
    if len(answers) != len(reference):
        raise ValueError("Answer and reference lists must be the same length")
        
    # Calculate matching score
    score = sum(a == r for a, r in zip(answers, reference)) / len(answers)
    return score
```

## Pull Request Process

1. Update your fork with the latest changes from upstream:
   ```bash
   git fetch upstream
   git merge upstream/main
   ```

2. Run all tests before submitting:
   ```bash
   pytest
   ```

3. Run code quality checks:
   ```bash
   pre-commit run --all-files
   ```

4. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request from your fork to the original repository

6. Fill in the Pull Request template with:
   - A description of the changes
   - Any related issues
   - Screenshots for UI changes
   - Notes about testing done

7. A maintainer will review your Pull Request and may request changes

8. Once approved, your changes will be merged

## Testing

- All code changes must include appropriate tests
- Maintain or improve the current test coverage
- Tests should be in the `tests/` directory with filenames matching `test_*.py`
- Run tests with `pytest`

Example test:

```python
def test_calculate_score():
    """Test the calculate_score function with various inputs."""
    # Test perfect match
    assert calculate_score(["A", "B", "C"], ["A", "B", "C"]) == 1.0
    
    # Test partial match
    assert calculate_score(["A", "B", "D"], ["A", "B", "C"]) == 2/3
    
    # Test no match
    assert calculate_score(["X", "Y", "Z"], ["A", "B", "C"]) == 0.0
    
    # Test error condition
    with pytest.raises(ValueError):
        calculate_score(["A", "B"], ["A", "B", "C"])
```

## Documentation

- Update documentation when changing code
- Add documentation for new features
- Follow the docstring style in existing code
- Update the README.md if necessary

## Issue Reporting

When reporting issues, please include:

- A clear, descriptive title
- A detailed description of the issue
- Steps to reproduce the behavior
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment information (OS, Python version, package versions)
- Possible solutions if you have suggestions

## Feature Requests

Feature requests are welcome! When submitting a feature request:

- Describe the problem your feature would solve
- Explain why this feature would be useful
- Provide examples of how the feature would be used
- Be open to discussion about alternative solutions

## License

By contributing to this project, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

Thank you for contributing to the Interview Toolkit! 