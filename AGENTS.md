# Agent Instructions for vendor-connectors

> **Critical:** This repository uses the jbcom ecosystem patterns. Read this ENTIRE file before making changes.
> 
> **Cursor Agents:** See `.cursor/rules/` for detailed guidelines and agent profiles
> **Memory Bank:** Check `memory-bank/activeContext.md` for current development context

## Repository Overview

**vendor-connectors** is a universal connector library providing standardized access to:
- Cloud providers: AWS, Google Cloud
- Third-party services: GitHub, Slack, Vault, Zoom
- AI APIs: Anthropic Claude, Cursor agents, Meshy 3D

Written in Python 3.10+, the package is part of the jbcom ecosystem and published to PyPI.

**Key Stats:**
- Languages: Python 3.10+ (required due to crewai dependency)
- Package Manager: uv (Astral's fast Python package manager)
- Build System: hatchling
- Testing: pytest with coverage tracking (target: 75%, threshold: 45%)
- Linting: ruff (120 char line length)
- Lines of Code: ~5,000+ (src)
- Test Files: 325+ tests across 20+ test files

## CRITICAL: Authentication Tokens

### GitHub Token (ALWAYS use this pattern)
```bash
# For jbcom repositories, ALWAYS use GITHUB_JBCOM_TOKEN
GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh <command>

# Examples:
GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh pr list
GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh issue view 33
GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh pr create --title "..." --body "..."
```

**NEVER** use `$GITHUB_TOKEN` directly - always use `GH_TOKEN="$GITHUB_JBCOM_TOKEN"` wrapper.

### API Keys for Development
```bash
# AI Services (for E2E testing)
ANTHROPIC_API_KEY=sk-ant-...      # Required for LangChain/CrewAI/Strands agent tests
MESHY_API_KEY=msy_...             # Required for 3D generation E2E tests

# Cloud Services
AWS_ACCESS_KEY_ID=...             # AWS operations
AWS_SECRET_ACCESS_KEY=...
GOOGLE_SERVICE_ACCOUNT='{...}'    # Google Cloud (JSON)

# Third-party Services  
GITHUB_TOKEN=ghp_...              # GitHub API (NOT for gh CLI - see above)
SLACK_TOKEN=xoxb-...              # Slack
VAULT_ADDR=https://...            # HashiCorp Vault
VAULT_TOKEN=hvs.xxx
```

## Required Setup - Do These First

### 1. Install uv Package Manager (REQUIRED)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

**Verification:** `uv --version` should show version 0.9.16 or newer

### 2. Install Dependencies
```bash
# For basic development (ALWAYS do this first)
uv sync --extra tests

# For all optional features (AI tools, webhooks, MCP)
uv sync --all-extras
```

**Important:** The `--extra tests` flag is REQUIRED to run tests.

### 3. Check Memory Bank Context
```bash
cat memory-bank/activeContext.md 2>/dev/null || echo "No active context"
```

## Development Commands - Validated

### Run Tests (60-120 seconds)
```bash
# ALWAYS use uv run prefix
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/meshy/test_tools.py -v

# Run with coverage
uv run pytest tests/ -v --cov=vendor_connectors --cov-report=term-missing

# Run E2E tests (requires API keys, takes 5-10 minutes)
uv run pytest tests/e2e/ -v --timeout=600
```

**Expected Results:**
- 325+ tests total
- Coverage FAILS if below 45% threshold
- E2E tests save real GLB files to `tests/e2e/fixtures/models/`

### Lint and Format (15-20 seconds)
```bash
# Check linting
uvx ruff check src/ tests/

# Auto-fix linting issues
uvx ruff check --fix src/ tests/

# Format code
uvx ruff format src/ tests/
```

### Build Package
```bash
uv build
```

## Architecture

### Package Structure
```
src/vendor_connectors/
├── __init__.py          # Main exports
├── base.py              # VendorConnectorBase - base class for ALL connectors
├── connectors.py        # VendorConnectors unified API with caching
├── aws/                 # AWS connector with mixins
├── google/              # Google Cloud connector with mixins
├── github/              # GitHub connector
├── slack/               # Slack connector
├── vault/               # HashiCorp Vault connector
├── zoom/                # Zoom connector
├── anthropic/           # Anthropic Claude connector
├── cursor/              # Cursor AI connector
└── meshy/               # Meshy AI 3D generation
    ├── base.py          # HTTP client with DirectedInputsClass
    ├── text3d.py        # Text-to-3D generation
    ├── rigging.py       # Character rigging
    ├── animate.py       # Animation application
    ├── tools.py         # LangChain StructuredTools
    ├── mcp.py           # MCP server implementation
    └── webhooks/        # Async job notifications
```

### Key Design Patterns

**1. VendorConnectorBase** (NEW - use for all new connectors)
```python
from vendor_connectors.base import VendorConnectorBase

class MyConnector(VendorConnectorBase):
    BASE_URL = "https://api.example.com"
    API_KEY_ENV = "MY_API_KEY"
    
    def my_operation(self):
        return self.get("/endpoint").json()
```

**2. DirectedInputsClass** (inherited from VendorConnectorBase)
All connectors automatically load credentials from:
- Environment variables (e.g., `MESHY_API_KEY`)
- Direct parameters (e.g., `MyConnector(api_key="xxx")`)
- stdin JSON input

**3. Mixin Architecture**
```python
from vendor_connectors.aws import AWSConnector, AWSOrganizationsMixin

class MyConnector(AWSConnector, AWSOrganizationsMixin):
    pass
```

**4. Three-Interface Pattern** (for AI-enabled connectors)
Each connector should provide:
1. **Python API** - Direct programmatic access
2. **LangChain Tools** - `tools.py` with StructuredTools
3. **MCP Server** - `mcp.py` for Model Context Protocol

### Meshy AI Example (Reference Implementation)
```python
# Python API
from vendor_connectors.meshy import text3d
result = text3d.generate("a medieval sword")

# LangChain Tools
from vendor_connectors.meshy.tools import get_tools
tools = get_tools()  # Returns list of StructuredTools

# MCP Server
from vendor_connectors.meshy.mcp import create_server, run_server
run_server()  # Starts MCP server on stdio
```

## CI Pipeline

GitHub Actions workflow: `.github/workflows/ci.yml`

```
build → test (py3.10, py3.13) → lint → [release on tag]
```

**Coverage:** CI will FAIL if coverage drops below 45%

## Code Style

- Python 3.10+ required
- Ruff for linting and formatting (120 char line length)
- Type hints required on public functions
- Modern Python style: `list[str]` not `List[str]`
- Absolute imports only
- Google-style docstrings

## Commit Messages

Use conventional commits:
```
feat(aws): add new S3 operation         # Minor version bump
feat(meshy): add texture generation     # Minor version bump  
fix(connector): handle timeout error    # Patch version bump
docs(readme): update installation       # No version bump
test(meshy): add E2E tests              # No version bump
```

## Common Issues and Solutions

### 1. `ModuleNotFoundError: No module named 'pytest'`
**Solution:** Run `uv sync --extra tests`

### 2. Coverage failure: total of XX is less than fail-under=45
**Solution:** This is expected when running partial test suites. Run full suite: `uv run pytest tests/ -v`

### 3. `MESHY_API_KEY not set`
**Solution:** Export the API key or use DirectedInputsClass:
```python
from vendor_connectors.meshy import base
base.configure(api_key="msy_xxx")
```

### 4. GitHub CLI authentication fails
**Solution:** ALWAYS use `GH_TOKEN="$GITHUB_JBCOM_TOKEN"`:
```bash
GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh pr list
```

### 5. ArtStyle validation error
**Solution:** Meshy API only supports `realistic` and `sculpture` art styles (not `cartoon`, `low-poly`, etc.)

## E2E Testing

E2E tests prove end-to-end functionality by:
1. Creating real AI agents (LangChain, CrewAI, Strands)
2. Invoking Meshy tools to generate 3D models
3. **Waiting for completion** (tests take 1-5 minutes each)
4. Downloading and saving GLB files to `tests/e2e/fixtures/models/`
5. Recording API interactions with pytest-vcr cassettes

**To record new cassettes:**
```bash
# Requires ANTHROPIC_API_KEY and MESHY_API_KEY
rm tests/e2e/meshy/cassettes/*.yaml
uv run pytest tests/e2e/meshy/test_langchain.py -v -s --timeout=600
```

## Session Management

### Start of Session
```bash
# Check current context
cat memory-bank/activeContext.md

# Check open issues
GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh issue list

# Check PR status
GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh pr status
```

### End of Session
```bash
# Update memory bank
echo "## Session: $(date +%Y-%m-%d)" >> memory-bank/activeContext.md
echo "- Completed: <summary of work>" >> memory-bank/activeContext.md

# Stage and commit
git add -A
git commit -m "feat(component): description"
```

## Related Documentation

- `CLAUDE.md` - Claude Code specific instructions
- `.cursor/rules/` - Cursor agent rules and profiles
- `.github/copilot-instructions.md` - GitHub Copilot instructions
- `.github/agents/` - Custom Copilot agent profiles
- `memory-bank/activeContext.md` - Current development context
