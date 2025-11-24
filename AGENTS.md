# AI Agent Guidelines for directed-inputs-class

This document provides critical context for AI coding assistants (Cursor, Codex, Copilot, Gemini, etc.) working on this repository.

## 🚨 CRITICAL: CI/CD Workflow Design Philosophy

### Our Unified CI Workflow Approach

**This repository uses a UNIFIED CI workflow** that combines testing, quality checks, AND release automation in a **single `ci.yml` file**. This is an INTENTIONAL design decision.

### Key Design Decisions (DO NOT SUGGEST CHANGING THESE)

#### 1. **Semantic Release Configuration in CI YAML, NOT pyproject.toml**

❌ **INCORRECT Agent Suggestion:**
> "Add `[tool.semantic_release]` configuration to `pyproject.toml`"

✅ **CORRECT Design:**
- All semantic-release configuration is done via **workflow parameters**
- The workflow uses these specific flags:
  ```yaml
  build: false          # We build with hynek/build-and-inspect-python-package
  vcs_release: true     # Create GitHub releases
  commit: false         # NO automatic commits
  tag: true             # Create version tags
  push: false           # Tags are pushed separately
  changelog: false      # NO automatic changelog commits
  ```

**WHY:**
- We use `hynek/build-and-inspect-python-package` for building (industry best practice)
- Semantic-release handles ONLY versioning and GitHub releases
- We do NOT want automated changelog commits cluttering git history
- Manual changelog management provides better control and context

#### 2. **No `pyproject.toml` Semantic Release Section Needed**

The workflow explicitly sets `commit: false` and `changelog: false` because:
- ✅ We manage changelogs manually
- ✅ Version is read from `__init__.py` via hatch/setuptools
- ✅ Semantic-release only creates tags and GitHub releases
- ❌ We don't want bot commits in git history

#### 3. **The `push: false` Flag is CORRECT**

❌ **INCORRECT Agent Suggestion:**
> "Set `push: true` to push tags to remote"

✅ **CORRECT Design:**
- `push: false` is intentional
- The workflow runs on GitHub, tags are already in GitHub
- We don't need to push back to ourselves
- This prevents potential authentication issues

#### 4. **Artifact Download Versions**

Both `actions/download-artifact@v4` and `@v6` are acceptable:
- We use `@v6` for build artifacts in test jobs
- We use `@v4` for release artifacts (compatibility with signed builds)
- This is NOT a mistake or inconsistency
- DO NOT suggest "fixing" this

### What This Workflow DOES

```
On Push to main:
  ↓
1. Build & verify package ✓
  ↓
2. Run tests across all Python versions ✓
  ↓
3. Type checking with pyright ✓
  ↓
4. Linting with pre-commit ✓
  ↓
5. Generate coverage report ✓
  ↓
6. IF all pass → Semantic Release:
   - Analyze commit messages
   - Determine next version
   - Create Git tag
   - Create GitHub release
   ↓
7. Build signed attestation ✓
  ↓
8. Publish to PyPI ✓
```

### What This Workflow DOES NOT DO

❌ Create changelog commits
❌ Commit version bumps to files
❌ Require `[tool.semantic_release]` in pyproject.toml
❌ Use multiple workflow files
❌ Push tags back to GitHub (they're already there)

## 📝 Making Code Changes

### When Reviewing PRs

**DO:**
- ✅ Review code quality and correctness
- ✅ Check test coverage
- ✅ Verify type hints
- ✅ Suggest API improvements
- ✅ Check for security issues

**DO NOT:**
- ❌ Suggest adding semantic-release config to pyproject.toml
- ❌ Recommend splitting ci.yml back into multiple files
- ❌ Suggest automated changelog generation
- ❌ Recommend changing release workflow parameters
- ❌ Flag the unified workflow as "incorrect" or "missing configuration"

### Understanding Version Management

```
Version Source: src/directed_inputs_class/__init__.py
   ↓
__version__ = "1.0.0"
   ↓
Read by: hatchling (setuptools backend)
   ↓
Used by: semantic-release for version detection
   ↓
Tag Created: v1.0.0 (or next version based on commits)
   ↓
Published to: PyPI with that version
```

**We do NOT:**
- ❌ Have semantic-release auto-increment `__version__` in files
- ❌ Commit version changes back to repository
- ❌ Use version_tostring or version_variable in semantic-release config

### Commit Message Format

We follow conventional commits:
- `feat:` - New features (minor version bump)
- `fix:` - Bug fixes (patch version bump)
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Test improvements
- `ci:` - CI/CD changes

**Breaking changes:**
- Add `BREAKING CHANGE:` in commit body for major version bumps
- Or use `feat!:` / `fix!:` notation

## 🔧 Development Workflow

### Local Development

```bash
# Install dependencies
pip install -e ".[tests,typing,docs]"

# Run tests
pytest

# Run type checking
mypy src/

# Run linting
pre-commit run --all-files
```

### Creating PRs

1. Create a feature branch
2. Make your changes
3. Run tests locally
4. Create PR against `main`
5. CI will run automatically
6. Merge to main when approved

### Releases (Automated)

When PR is merged to main:
1. CI runs all checks
2. Semantic-release analyzes commits since last tag
3. If release needed:
   - Creates version tag
   - Creates GitHub release
   - Builds signed package
   - Publishes to PyPI
4. **NO commits are made to the repository**

## 🎯 Common Agent Misconceptions

### Misconception #1: "Missing semantic-release config"

**Agent says:** "The workflow uses python-semantic-release but there's no [tool.semantic_release] section"

**Reality:** This is BY DESIGN. All configuration is in the workflow YAML via parameters.

### Misconception #2: "Workflow will fail without config"

**Agent says:** "The release job will likely fail without semantic-release config"

**Reality:** The workflow has successfully run hundreds of times across our repositories. It works as designed.

### Misconception #3: "Need to add changelog configuration"

**Agent says:** "Enable changelog: true for automated changelog updates"

**Reality:** We intentionally set `changelog: false` because we maintain changelogs manually for better quality and context.

### Misconception #4: "Version variable needed"

**Agent says:** "Add version_variable to auto-update __version__"

**Reality:** Version is read from the file but NOT written back. Tags are the source of truth.

### Misconception #5: "Multiple files better"

**Agent says:** "Consider splitting ci.yml and release.yml for separation of concerns"

**Reality:** We INTENTIONALLY unified them. This is the modern pattern we're adopting across all repos.

## 📚 Reference Implementation

This workflow design is based on:
- ✅ extended-data-types (the parent library)
- ✅ hynek/build-and-inspect-python-package best practices
- ✅ Python Packaging Authority recommendations
- ✅ Trusted publishing to PyPI (no tokens needed)

## 🤝 Getting Help

If you're an AI agent uncertain about a suggestion:
1. Check this document first
2. Look at the extended-data-types repository for reference
3. When in doubt, DO NOT suggest changes to the CI workflow
4. Focus on code quality, tests, and documentation

---

**Last Updated:** 2025-11-24
**Workflow Version:** Unified CI v1.0 (python-semantic-release@v9.17.0)
