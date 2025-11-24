# GitHub Copilot Instructions for directed-inputs-class

## CI/CD Workflow - Read This First! 🚨

This repository uses **CalVer auto-versioning** with automatic PyPI releases. Every push to main = new release.

### ✅ What is CORRECT (Do not suggest changing):

1. **CalVer versioning: `YYYY.MM.BUILD`** - Auto-generated, no manual management
2. **No git tags** - Version only in PyPI package metadata
3. **No semantic-release** - We removed it for simplicity
4. **Auto-publish to PyPI** - Every main push gets released after tests pass
5. **No conditional releases** - Simple and predictable

### ❌ Do NOT Suggest:

- Adding semantic-release or conventional commits
- Using git tags for versioning
- Manual version management
- Conditional release logic
- SemVer instead of CalVer

## Code Guidelines

### Imports
Always use extended-data-types utilities when available:
```python
# ✅ Good
from extended_data_types import strtobool, strtoint, strtopath

# ❌ Avoid
def custom_str_to_bool(val): ...
```

### Type Hints
Use modern type hints:
```python
# ✅ Good
from collections.abc import Mapping
def func(data: Mapping[str, Any]) -> dict[str, Any]:

# ❌ Avoid
from typing import Dict
def func(data: Dict[str, Any]) -> Dict[str, Any]:
```

### Testing
- Always run tests locally before suggesting changes
- Maintain or improve test coverage
- Use pytest fixtures appropriately

## Version Management

Version is auto-generated during CI using `.github/scripts/set_version.py`:
- Format: `YYYY.MM.BUILD_NUMBER`
- Example: `2025.11.42`
- Updated automatically in `__init__.py` during release build

DO NOT suggest manual version management. It's fully automated.

## Questions?

See `AGENTS.md` for detailed explanations of our workflow design.
