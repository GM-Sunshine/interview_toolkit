# Changelog

## [0.5.0] - 2025-05-14

fixed pytest-cov version


## [0.4.0] - 2025-05-14

fixed pydantic version


## [0.3.0] - 2025-05-14

fixed pillow version


## [0.2.0] - 2025-05-14

fixed pillow version


## [0.3.0] - 2025-05-14

Launched Interview Toolkit — your AI sidekick for killer questions & slick PDFs! 


All notable changes to the Interview Toolkit project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2023-10-15

### Added
- Implemented rate limiting for API calls to prevent excessive usage
- Added comprehensive error handling throughout the application
- Created a version tracking module for better version management
- Created an installation script for easier setup
- Added pre-commit hooks for code quality enforcement
- Implemented CI/CD pipeline using GitHub Actions

### Changed
- Replaced hardcoded IP addresses with localhost for improved security
- Enhanced input validation for user-provided inputs
- Updated configuration management to be more robust
- Modernized Python packaging with pyproject.toml
- Improved PDF generation with better formatting

### Fixed
- Fixed duplicate function definitions in question generator
- Addressed security vulnerabilities in file handling
- Fixed error handling in LLM providers
- Resolved configuration loading issues

## [0.1.0] - 2023-08-01

### Added
- Initial release of the Interview Toolkit
- Basic question generation using OpenAI and Ollama
- PDF export functionality
- Command-line interface for interaction
- Configuration system for API keys and settings 