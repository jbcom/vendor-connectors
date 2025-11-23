# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository setup with memory bank (.cursorrules)
- Agentic instruction files in .ruler/ directory
- CHANGELOG.md, CONTRIBUTING.md, SECURITY.md

### Changed
- REVIEW.md corrected to accurately reflect existing implementations

## [0.1.0] - 2024-XX-XX

### Added
- AWSConnector with role assumption and session caching
- GithubConnector with repository and file management
- GoogleConnector with lazy credential loading
- SlackConnector with rate limiting
- VaultConnector with Token and AppRole auth
- ZoomConnector with OAuth2 authentication
- Base Utils class with directed inputs, logging, caching
- Custom error classes for standardized error handling
- Type hints throughout codebase
- MIT License

### Infrastructure
- Python package structure with hatchling build backend
- Support for Python 3.9 through 3.13
- Dependency management via pyproject.toml

[Unreleased]: https://github.com/jbcom/cloud-connectors/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jbcom/cloud-connectors/releases/tag/v0.1.0
