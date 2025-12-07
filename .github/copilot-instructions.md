# Agent Instructions for vendor-connectors

> **Note:** This repository has specialized custom agents and a Copilot Space configured for persistent context.
> - **Copilot Space:** `.github/copilot-space.yml` - Workspace configuration with knowledge base
> - **Custom Agents:** `.github/agents/` - Specialized agents for testing, connector building, AI refactoring
> - See [.github/agents/README.md](.github/agents/README.md) for agent usage

## Repository Overview

**vendor-connectors** is a universal connector library providing standardized access to cloud providers (AWS, Google Cloud), third-party services (GitHub, Slack, Vault, Zoom), and AI APIs (Anthropic Claude, Cursor agents, Meshy 3D). Written in Python 3.10+, the package is part of the jbcom ecosystem and published to PyPI.

**Key Stats:**
- Languages: Python (3.10+ required due to crewai dependency)
- Package Manager: uv (Astral's fast Python package manager)
- Build System: hatchling
- Testing: pytest with coverage tracking (target: 75%, current: ~47%)
- Linting: ruff (120 char line length)
- Lines of Code: ~4,787 (src)
- Test Files: 325+ tests across 20+ test files

## Required Setup - Do These First

### 1. Install uv Package Manager (REQUIRED)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"  # Add to shell session
```

**Verification:** `uv --version` should show version 0.9.16 or newer

### 2. Install Dependencies
```bash
# For basic development (ALWAYS do this first)
uv sync --extra tests

# For all optional features (use when working with AI/MCP/webhooks)
uv sync --all-extras
```

**Important:** The `--extra tests` flag is REQUIRED to run tests. Without it, pytest and related packages won't be installed.

## Development Commands - Validated Order

### Run Tests (60-120 seconds)
```bash
# ALWAYS use uv run prefix for commands
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_aws_connector.py -v

# Run with coverage (takes 60-90 seconds)
uv run pytest tests/ -v --cov=vendor_connectors --cov-report=term-missing

# Just collect tests (no execution, ~2 seconds)
uv run pytest tests/ --co -q
```

**Expected Results:**
- 325 tests total (as of Dec 2025)
- Tests WILL run but coverage will FAIL if below 45% (threshold set in pyproject.toml)
- Coverage target is 75% but threshold is 45% to allow incremental improvement
- Test execution time: 60-120 seconds for full suite

### Lint and Format (15-20 seconds)
```bash
# Check linting (shows errors but doesn't fix)
uvx ruff check src/ tests/

# Auto-fix linting issues
uvx ruff check --fix src/ tests/

# Check formatting (shows files that need formatting)
uvx ruff format --check src/ tests/

# Auto-format code
uvx ruff format src/ tests/
```

**Common Lint Issues to Expect:**
- F841: Unused variables in test files
- W293: Blank lines with whitespace
- F401: Unused imports
Most issues are auto-fixable with `--fix` flag.

### Build Package (10-15 seconds)
```bash
uv build
```

**Expected Output:**
- Creates `dist/vendor_connectors-*.tar.gz`
- Creates `dist/vendor_connectors-*-py3-none-any.whl`

### Type Checking
```bash
uv run mypy src/
```

**Note:** Type checking is configured but not strictly enforced. `disallow_untyped_defs` is False.

## CI Pipeline - GitHub Actions

The CI workflow (`.github/workflows/ci.yml`) runs on push to main and all PRs:

### 1. Build Job
- Uses `hynek/build-and-inspect-python-package@v2`
- Builds source and wheel distributions
- Validates package metadata

### 2. Test Job (Matrix: Python 3.10, 3.13)
```bash
uv sync --all-extras  # Installs ALL optional dependencies
uv run pytest tests -v
```
**Critical:** CI uses `--all-extras` so it tests with ALL optional dependencies installed (crewai, mcp, webhooks, vector, ai-*). Local testing with just `--extra tests` may miss import issues.

### 3. Lint Job
```bash
uvx ruff check src/ tests/
uvx ruff format --check src/ tests/
```

### 4. Release Job (main branch only)
- Uses python-semantic-release for version management
- Auto-publishes to PyPI on conventional commit messages
- Creates GitHub releases

**Conventional Commit Format for Releases:**
- `feat(component):` → Minor version bump
- `fix(component):` → Patch version bump
- `feat!:` or `BREAKING CHANGE:` → Major version bump

## Project Architecture

### Directory Structure
```
vendor-connectors/
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Main CI pipeline (build, test, lint, release)
│       ├── claude.yml                # Claude AI agent workflow
│       ├── claude-code-review.yml    # Code review automation
│       └── docs.yml                  # Documentation builds
├── src/vendor_connectors/
│   ├── __init__.py                   # Public API exports
│   ├── connectors.py                 # VendorConnectors unified API with caching
│   ├── cloud_params.py               # Cloud parameter utilities
│   ├── anthropic/                    # Anthropic Claude API connector
│   ├── aws/                          # AWS (boto3) with Organizations, SSO, S3, CodeDeploy mixins
│   ├── cursor/                       # Cursor Background Agent API
│   ├── github/                       # GitHub API and GraphQL client
│   ├── google/                       # Google Cloud (Workspace, GCP, Billing, Services)
│   ├── meshy/                        # Meshy AI 3D asset generation
│   │   ├── text3d.py, rigging.py, animate.py, retexture.py  # Core 3D ops
│   │   ├── tools.py                  # LangChain StructuredTools
│   │   ├── mcp.py                    # MCP server
│   │   ├── persistence/              # Local caching, vector store (sqlite-vec)
│   │   └── webhooks/                 # FastAPI webhook server (optional)
│   ├── slack/                        # Slack SDK wrapper
│   ├── vault/                        # HashiCorp Vault client
│   └── zoom/                         # Zoom OAuth and API client
├── tests/                            # 325+ tests (pytest)
│   ├── test_*.py                     # Main connector tests
│   └── meshy/                        # Meshy-specific tests
├── docs/                             # Sphinx documentation
├── memory-bank/
│   └── activeContext.md              # Development context (READ THIS FIRST)
├── pyproject.toml                    # Build config, dependencies, tool settings
├── tox.ini                           # Multi-Python testing (3.9-3.13)
└── README.md                         # Public documentation
```

### Key Configuration Files
- **pyproject.toml:** Dependencies, build config, pytest/coverage/ruff/mypy settings
- **tox.ini:** Multi-version testing across Python 3.9-3.13
- **.gitignore:** Excludes uv.lock, .venv/, __pycache__, dist/, build artifacts

### Design Patterns

**Mixin Architecture:**
All AWS connectors use mixins for modular features:
```python
from vendor_connectors.aws import AWSConnector, AWSOrganizationsMixin, AWSS3Mixin

class CustomAWSConnector(AWSConnector, AWSOrganizationsMixin, AWSS3Mixin):
    pass
```

**VendorConnectors Unified API:**
Provides cached client instances with automatic credential loading:
```python
from vendor_connectors import VendorConnectors
vc = VendorConnectors()
s3 = vc.get_aws_client("s3")  # Returns same instance on repeated calls
```

**jbcom Ecosystem Integration:**
All connectors extend `DirectedInputsClass` from directed-inputs-class package:
- Auto-loads credentials from environment variables, stdin, config files
- Structured logging via lifecyclelogging
- Utilities from extended-data-types

### Optional Extras Dependencies

The package has many optional features. **DO NOT** import these modules without the corresponding extras:

| Extra | Modules | Install Command |
|-------|---------|-----------------|
| `tests` | pytest, pytest-cov, pytest-mock | `uv sync --extra tests` |
| `webhooks` | meshy.webhooks (FastAPI, uvicorn, pyngrok) | `uv sync --extra webhooks` |
| `crewai` | meshy tools for CrewAI | `uv sync --extra crewai` |
| `mcp` | meshy MCP server | `uv sync --extra mcp` |
| `vector` | meshy.persistence.vector_store (sqlite-vec, sentence-transformers) | `uv sync --extra vector` |

**Coverage Exclusions:** pyproject.toml excludes `meshy/agent_tools/*` from coverage because they require optional dependencies (crewai, mcp) that aren't installed with `--extra tests`. CI would fail without `--all-extras`.

## Environment Variables

All connectors read from environment. Set these BEFORE importing:

```bash
# AI Services
export ANTHROPIC_API_KEY="sk-ant-..."
export CURSOR_API_KEY="cur_..."
export MESHY_API_KEY="msy_..."

# AWS
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
export EXECUTION_ROLE_ARN="arn:aws:iam::123456789012:role/MyRole"  # For role assumption

# Google Cloud
export GOOGLE_SERVICE_ACCOUNT='{"type":"service_account",...}'  # JSON string

# GitHub
export GITHUB_TOKEN="ghp_..."
export GITHUB_OWNER="myorg"  # Default org/user

# Slack
export SLACK_TOKEN="xoxp-..."  # User token
export SLACK_BOT_TOKEN="xoxb-..."  # Bot token

# Vault
export VAULT_ADDR="https://vault.example.com"
export VAULT_TOKEN="hvs...."  # Or use AppRole:
export VAULT_ROLE_ID="..."
export VAULT_SECRET_ID="..."

# Zoom
export ZOOM_CLIENT_ID="..."
export ZOOM_CLIENT_SECRET="..."
export ZOOM_ACCOUNT_ID="..."
```

## Common Issues and Workarounds

### Issue 1: Tests Fail with ImportError for Optional Dependencies
**Symptom:** `ModuleNotFoundError: No module named 'crewai'` or similar
**Solution:** Use `uv sync --all-extras` instead of `uv sync --extra tests` OR exclude those tests
**Why:** Some modules (ai/, meshy/agent_tools/) require optional extras

### Issue 2: Coverage Fails at 23% (Expected: 45%)
**Symptom:** `FAIL Required test coverage of 45.0% not reached. Total coverage: 23.23%`
**Solution:** This is a KNOWN ISSUE (see Issue #21). Threshold is 45%, target is 75%
**Workaround:** Focus on testing your changes, not hitting the global threshold
**CI Behavior:** CI will FAIL if coverage drops below 45%

### Issue 3: uv Command Not Found
**Symptom:** `bash: uv: command not found`
**Solution:** Install uv and add to PATH:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
```

### Issue 4: Ruff Shows Many Lint Errors in Tests
**Symptom:** F841, W293, F401 errors in test files
**Solution:** This is EXPECTED. Run `uvx ruff check --fix src/ tests/` to auto-fix
**Context:** Test files sometimes have intentionally unused variables for mocking

### Issue 5: Tests Run Forever (>2 minutes)
**Symptom:** `pytest` hangs or takes >5 minutes
**Possible Cause:** Test is waiting for external API or network timeout
**Solution:** Run tests with `-v` flag to see which test is stuck. Use `pytest tests/test_specific.py` to isolate

## Code Style Guidelines

**From pyproject.toml [tool.ruff]:**
- Line length: 120 characters (not 80!)
- Target: Python 3.9+ (but requires 3.10+ due to crewai)
- Select rules: E, W, F, I, B, C4, UP
- Ignore: E501 (line too long), B008, B019, B904, C901, UP006, UP007, UP035, UP045
- `__init__.py` files: Ignore F401 (unused imports), E402 (module level import not at top)

**Type Hints:**
- Required on public functions
- Use modern syntax: `list[str]` not `List[str]`
- imports: NO `from typing import List, Dict` - use built-ins

**Imports:**
- Absolute imports only
- No relative imports (no `from . import ...`)

**Docstrings:**
- Google-style docstrings preferred
- Not strictly enforced

## Validation Checklist Before Submitting

1. **Install and Tests:**
   ```bash
   uv sync --extra tests
   uv run pytest tests/ -v
   ```
   ✓ Tests should pass (allow for coverage being below 75%)

2. **Linting:**
   ```bash
   uvx ruff check src/ tests/
   uvx ruff format --check src/ tests/
   ```
   ✓ No lint errors should remain (or use --fix to auto-fix)

3. **Build:**
   ```bash
   uv build
   ```
   ✓ Should create dist/ with .tar.gz and .whl files

4. **Type Check (Optional but Recommended):**
   ```bash
   uv run mypy src/
   ```
   ✓ Ignore missing stubs warnings for third-party packages

5. **Multi-Python Testing (Optional):**
   ```bash
   tox
   ```
   ✓ Tests across Python 3.9-3.13 (takes 10+ minutes)

## Quick Reference for Common Tasks

### Using Specialized Agents
```bash
# For test coverage improvements
@copilot use agent:test-coverage-agent

# For new connector creation
@copilot use agent:connector-builder-agent

# For adding LangChain tools and MCP servers to connectors
@copilot use agent:ai-refactor-agent
```
See [.github/agents/README.md](.github/agents/README.md) for details.

### Adding a New Connector
1. Create new module in `src/vendor_connectors/your_connector/`
2. Extend `DirectedInputsClass` from directed-inputs-class
3. Export in `src/vendor_connectors/__init__.py`
4. Add to `VendorConnectors` in `src/vendor_connectors/connectors.py`
5. Create tests in `tests/test_your_connector.py`
6. Update README.md with usage examples

### Adding a New Dependency
1. Add to `dependencies` array in `pyproject.toml` OR to `[project.optional-dependencies]` if optional
2. Run `uv sync` to update lock file
3. Verify tests still pass
4. Update README.md if user-facing

### Updating Version
**DO NOT** manually update version. Use conventional commits:
```bash
git commit -m "feat(aws): add new S3 feature"  # → 0.3.0
git commit -m "fix(slack): fix rate limiting"  # → 0.2.1
```
python-semantic-release will auto-bump version on merge to main.

## Current Direction and Open Work

### Recent Changes
**Note:** Check git log and PR history for latest changes.

- **AI tooling refactor complete**: Tools now live with connectors (meshy/tools.py, meshy/mcp.py). No central ai/ package.
- **Meshy connector**: Full 3D asset generation with LangChain tools and MCP server

### Key Open Issues
**Note:** Check issue tracker for current status.

- **Issue #21**: Increase test coverage to 75% (currently ~47%, threshold 45%)
- **Issue #8**: Fix CI/PyPI publish issues
- **Issue #3**: Complete GitHub Actions CI workflow setup

### Strategic Direction
1. **Tools live with connectors**: Each connector owns its LangChain tools and MCP server (no central ai/ package)
2. **Meshy integration**: Comprehensive 3D asset generation with tools.py and mcp.py
3. **Test coverage**: Incrementally improving from 47% to 75% target
4. **Three-interface pattern**: Each connector should provide:
   - Direct Python API (`meshy.text3d.generate()`)
   - LangChain tools (`meshy.tools.get_tools()`)
   - MCP server (`meshy-mcp` CLI)

### Connector Tool Architecture
```
vendor_connectors/<service>/
├── __init__.py    # Python API
├── tools.py       # LangChain StructuredTools
└── mcp.py         # MCP server entry point
```

See `src/vendor_connectors/meshy/` for the canonical example.

## Memory Bank - Read First

**ALWAYS read `memory-bank/activeContext.md` before starting work.** It contains:
- Current development context
- Recent changes and merges
- Known issues and their status
- Active work-in-progress

## Trust These Instructions

These instructions have been validated by running actual commands and observing their behavior. If you find an error or something has changed, update this file, but otherwise **trust that these steps work** and avoid redundant exploration or trial-and-error.
