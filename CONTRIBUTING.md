# Contributing to Cloud Connectors

Thank you for your interest in contributing to Cloud Connectors! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jbcom/cloud-connectors.git
   cd cloud-connectors
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[tests]"
   ```

4. **Install pre-commit hooks (when available):**
   ```bash
   pre-commit install
   ```

### Project Structure

```
src/cloud_connectors/
├── __init__.py          # Package exports
├── base/
│   ├── utils.py         # Base Utils class
│   ├── errors.py        # Error classes
│   └── logging.py       # Logging infrastructure
├── aws/__init__.py      # AWSConnector
├── github/__init__.py   # GithubConnector
├── google/__init__.py   # GoogleConnector
├── slack/__init__.py    # SlackConnector
├── vault/__init__.py    # VaultConnector
└── zoom/__init__.py     # ZoomConnector
```

## Development Guidelines

### Code Style

- **Follow PEP 8** for Python code style
- **Use type hints** for all function signatures
- **Maximum line length:** 100 characters
- **Docstrings:** Use Google-style docstrings
- **Import order:** Standard library, third-party, local (use isort)

### Connector Pattern

All connectors must inherit from the `Utils` base class:

```python
from cloud_connectors.base.utils import Utils
from typing import Optional

class NewConnector(Utils):
    def __init__(
        self,
        required_param: str,
        optional_param: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.required_param = required_param or self.get_input(
            "REQUIRED_PARAM",
            required=True
        )
        self.optional_param = optional_param
```

### Testing Requirements

- **Write tests** for all new functionality
- **Mock external services** - never hit real APIs in tests
- **Aim for 80%+ code coverage**
- **Test both success and error cases**

Example test structure:
```python
import pytest
from unittest.mock import Mock, patch
from cloud_connectors.new_connector import NewConnector

class TestNewConnector:
    @pytest.fixture
    def connector(self):
        return NewConnector(required_param="value")
    
    def test_method(self, connector):
        """Test method does X when Y."""
        # Arrange
        # Act
        # Assert
```

### Logging

Use structured logging via the Utils base class:

```python
self.logged_statement(
    "Operation description",
    labeled_json_data={"key": "value"},
    log_level="info",
    verbose=True,
    verbosity=1
)
```

### Error Handling

Use custom error classes from `base.errors`:

```python
from cloud_connectors.base.errors import FailedResponseError

try:
    result = api_call()
except Exception as e:
    self.logger.error("Operation failed", exc_info=True)
    raise FailedResponseError(response) from e
```

## Pull Request Process

### Before Submitting

1. **Write tests** for your changes
2. **Run tests:** `pytest`
3. **Run linters:** `black .`, `isort .`, `flake8`
4. **Check type hints:** `mypy src/`
5. **Update documentation** if needed
6. **Add changelog entry** under [Unreleased]

### PR Guidelines

1. **Create a feature branch:** `git checkout -b feature/your-feature-name`
2. **Make focused commits:** Each commit should be a logical unit
3. **Write descriptive commit messages:**
   ```
   Add retry logic to GoogleConnector
   
   - Implement exponential backoff for rate limits
   - Add configurable max retry attempts
   - Update tests to cover retry scenarios
   ```
4. **Push and create PR:** Include description of what and why
5. **Link related issues:** Use "Fixes #123" or "Closes #456"
6. **Respond to review feedback** promptly

### PR Title Format

Use conventional commit format:
- `feat: Add Azure connector`
- `fix: Handle rate limiting in SlackConnector`
- `docs: Update README with authentication examples`
- `test: Add integration tests for AWSConnector`
- `refactor: Simplify credential caching logic`
- `chore: Update dependencies`

### Review Process

- All PRs require at least one approval
- CI checks must pass (when implemented)
- PRs should be up to date with main branch
- Address or respond to all review comments

## Adding a New Connector

### Steps

1. **Create connector directory:**
   ```bash
   mkdir -p src/cloud_connectors/new_service
   touch src/cloud_connectors/new_service/__init__.py
   ```

2. **Implement connector class:**
   ```python
   # src/cloud_connectors/new_service/__init__.py
   from cloud_connectors.base.utils import Utils
   
   class NewServiceConnector(Utils):
       def __init__(self, api_key: str, **kwargs):
           super().__init__(**kwargs)
           self.api_key = api_key or self.get_input("NEW_SERVICE_API_KEY", required=True)
   ```

3. **Export in package init:**
   ```python
   # src/cloud_connectors/__init__.py
   from .new_service import NewServiceConnector
   
   __all__ = [..., "NewServiceConnector"]
   ```

4. **Add tests:**
   ```bash
   touch tests/unit/test_new_service_connector.py
   ```

5. **Update documentation:**
   - Add to README.md
   - Update CHANGELOG.md
   - Add usage examples

6. **Add dependencies** to `pyproject.toml` if needed

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/cloud_connectors --cov-report=html

# Run specific test file
pytest tests/unit/test_aws_connector.py

# Run specific test
pytest tests/unit/test_aws_connector.py::TestAWSConnector::test_init
```

### Writing Tests

- Use `pytest` fixtures for setup
- Mock external API calls using `unittest.mock` or service-specific mocks
- Test both happy paths and error conditions
- Use descriptive test names: `test_<what>_<condition>_<expected>`

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def method_name(param1: str, param2: int) -> bool:
    """Brief description of what the method does.
    
    More detailed explanation if needed. Can span multiple lines
    and include examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param1 is invalid
        RuntimeError: When operation fails
        
    Example:
        >>> connector = Connector()
        >>> result = connector.method_name("value", 42)
        >>> print(result)
        True
    """
```

## Getting Help

- **Questions:** Open a discussion on GitHub
- **Bugs:** Open an issue with reproduction steps
- **Features:** Open an issue describing the use case

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- Project README (for major features)

Thank you for contributing to Cloud Connectors! 🚀
