# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Universal vendor connectors for the jbcom ecosystem, providing standardized access to cloud providers (AWS, Google Cloud), services (GitHub, Slack, Vault, Zoom), and AI APIs (Anthropic Claude, Cursor agents, Meshy 3D).

## Development Commands

```bash
# Install dependencies
uv sync --extra tests

# Run all tests
uv run pytest tests/ -v

# Run a specific test file
uv run pytest tests/test_aws_connector.py -v

# Run a single test
uv run pytest tests/test_aws_connector.py::TestAWSConnector::test_specific -v

# Lint and format
uvx ruff check src/ tests/
uvx ruff format src/ tests/

# Type checking
uv run mypy src/

# Build package
uv build

# Run tests across Python versions (3.9-3.13)
tox
```

## Architecture

### Package Structure
- `src/vendor_connectors/` - Main package source
- `src/vendor_connectors/connectors.py` - `VendorConnectors` unified API with client caching
- Individual connector modules: `aws/`, `google/`, `github/`, `slack/`, `vault/`, `zoom/`, `anthropic/`, `cursor/`, `meshy/`

### Key Design Patterns

**Mixin Architecture**: Connectors use mixins for modular functionality:
```python
# Base connector with mixins for specific features
from vendor_connectors.aws import AWSConnector, AWSOrganizationsMixin

class MyConnector(AWSConnector, AWSOrganizationsMixin):
    pass
```

**VendorConnectors Unified API**: Provides cached access to all connectors:
```python
from vendor_connectors import VendorConnectors
vc = VendorConnectors()
s3 = vc.get_aws_client("s3")
github = vc.get_github_client(github_owner="org")
```

**jbcom Ecosystem**: All connectors extend `DirectedInputsClass` for automatic credential loading from environment variables, stdin, and config files.

### Meshy AI Module
The `meshy/` module has its own substructure:
- `text3d.py`, `rigging.py`, `animate.py`, `retexture.py` - Core 3D operations
- AI tool integrations live in `vendor_connectors/ai/`
- `webhooks/` - Webhook server for async job notifications
- `persistence/` - Local caching and vector store

## Environment Variables

All connectors read credentials from environment variables:
- `ANTHROPIC_API_KEY`, `CURSOR_API_KEY`, `MESHY_API_KEY` - AI services
- `AWS_*`, `EXECUTION_ROLE_ARN` - AWS credentials
- `GOOGLE_SERVICE_ACCOUNT` - Google Cloud JSON credentials
- `GITHUB_TOKEN`, `GITHUB_OWNER` - GitHub access
- `SLACK_TOKEN`, `SLACK_BOT_TOKEN` - Slack
- `VAULT_ADDR`, `VAULT_TOKEN` - HashiCorp Vault
- `ZOOM_CLIENT_ID`, `ZOOM_CLIENT_SECRET`, `ZOOM_ACCOUNT_ID` - Zoom OAuth

## Code Style

- Python 3.10+ required (crewai dependency)
- Ruff for linting and formatting (120 char line length)
- Type hints required on public functions
- Use modern Python style (`list[str]` not `List[str]`)
- Use absolute imports
- Google-style docstrings

## Commit Messages

Use conventional commits:
- `feat(aws): new AWS feature` - minor version
- `feat(meshy): Meshy feature` - minor version
- `fix(connector): bug fix` - patch version

## GitHub Authentication

```bash
GH_TOKEN="$GITHUB_TOKEN" gh <command>
```
