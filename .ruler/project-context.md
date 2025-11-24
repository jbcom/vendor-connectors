# Cloud Connectors Project Context

## Project Identity
This is a Python package providing universal cloud provider connectors with standardized interfaces and transparent secret management.

## Core Architecture

### Base Framework
All connectors inherit from `Utils` class (`src/cloud_connectors/base/utils.py`) which provides:
- Directed inputs from environment variables, config files, or stdin
- Lifecycle logging with rich formatting and verbosity controls
- File operations supporting JSON, YAML, and HCL2 formats
- Caching and memoization capabilities
- Standardized error handling

### Implemented Connectors
1. **AWSConnector** - Role assumption, session caching, retry logic
2. **GithubConnector** - Repository management, file operations, GraphQL
3. **GoogleConnector** - Workspace & Cloud Platform APIs with lazy loading
4. **SlackConnector** - Messaging, channels, rate limiting
5. **VaultConnector** - Token & AppRole auth, lazy initialization
6. **ZoomConnector** - OAuth2, user management

## Package Structure
```
src/cloud_connectors/
├── __init__.py (exports: AWSConnector, GithubConnector, GoogleConnector, SlackConnector, VaultConnector, ZoomConnector)
├── base/ (utils.py, errors.py, logging.py)
└── {aws,github,google,slack,vault,zoom}/ (each with __init__.py containing connector)
```

## Technical Details
- Python ≥3.9
- Build system: hatchling
- Version: 0.1.0
- License: MIT
- Type hints: Extensively used throughout
- Dependencies: boto3, PyGithub, google-cloud-*, slack-sdk, hvac, requests

## Current Gaps
- No tests exist yet
- No CI/CD pipelines
- Missing: CHANGELOG, CONTRIBUTING, SECURITY docs
- Limited documentation beyond README
- No published package on PyPI

## Development Standards
- Use type hints for all functions
- Follow PEP 8
- Add docstrings to public methods
- Use `self.logged_statement()` for logging
- Handle errors with custom classes from `base.errors`
- Cache clients/sessions to avoid repeated auth
