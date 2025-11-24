# Coding Guidelines for Cloud Connectors

## Code Style

### Python Standards
- Follow PEP 8 for naming and formatting
- Use type hints for all function signatures and return types
- Maximum line length: 100 characters (already in use)
- Use double quotes for strings consistently

### Documentation
- Add docstrings to all public classes and methods
- Use Google-style docstrings with Args, Returns, Raises sections
- Include usage examples in complex methods
- Document environment variables and configuration options

### Type Hints
```python
from typing import Optional, Dict, List, Any

def example_method(
    param: str,
    optional_param: Optional[int] = None,
    config: Dict[str, Any] = None
) -> List[str]:
    """Method docstring here."""
    pass
```

## Connector Pattern

### Base Class Usage
All connectors must:
1. Inherit from `Utils` base class
2. Accept `**kwargs` and pass to `super().__init__(**kwargs)`
3. Initialize cloud clients lazily when possible
4. Cache authenticated sessions/clients

### Standard Init Pattern
```python
class NewConnector(Utils):
    def __init__(
        self,
        required_param: str,
        optional_param: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.required_param = required_param or self.get_input("REQUIRED_PARAM", required=True)
        self.optional_param = optional_param or self.get_input("OPTIONAL_PARAM", required=False)
        # Initialize caches
        self._client_cache = {}
```

## Logging

### Use Structured Logging
```python
self.logged_statement(
    "Operation description",
    labeled_json_data={"context": data},
    log_level="info",
    verbose=True,
    verbosity=1
)
```

### Log Levels
- `debug`: Detailed diagnostic info (default for verbose)
- `info`: General informational messages
- `warning`: Warning messages for recoverable issues
- `error`: Error messages for failures
- `critical`: Critical failures requiring immediate attention

## Error Handling

### Use Custom Exceptions
```python
from cloud_connectors.base.errors import FailedResponseError

try:
    response = client.do_something()
except ClientError as e:
    self.logger.error("Operation failed", exc_info=True)
    raise FailedResponseError(e.response) from e
```

### Error Tracking
- Log errors before raising
- Track errors in `self.errors` list when appropriate
- Use `exc_info=True` for full stack traces in logs

## Testing Patterns (To Be Implemented)

### Unit Tests
```python
# tests/unit/test_aws_connector.py
import pytest
from unittest.mock import Mock, patch
from cloud_connectors.aws import AWSConnector

def test_assume_role():
    connector = AWSConnector(execution_role_arn="arn:aws:iam::123:role/test")
    # Test logic here
```

### Integration Tests
- Use moto for AWS mocking
- Use responses for HTTP mocking
- Create fixtures for common test data

## Configuration Management

### Input Retrieval
```python
# Simple input
value = self.get_input("KEY_NAME", default="default_value", required=False)

# Boolean input
flag = self.get_input("FLAG", is_bool=True, default=False)

# JSON/YAML input
config = self.decode_input("CONFIG", decode_from_json=True, required=True)
```

### Environment Variables
- Prefix project-specific vars appropriately
- Document required vs optional vars
- Provide sensible defaults

## Performance

### Caching
- Cache authenticated clients/sessions
- Use `@lru_cache` for expensive pure functions
- Invalidate caches when credentials expire

### Lazy Loading
- Don't authenticate until first use
- Load heavy dependencies only when needed
- Use property decorators for lazy initialization

## Security

### Credential Handling
- Never log sensitive credentials
- Use masked logging: `credentials["SessionToken"][:10] + "..."`
- Accept credentials from environment, not hardcoded
- Support multiple auth methods (tokens, files, env vars)

### Input Validation
- Validate all external inputs
- Sanitize file paths
- Check URL schemes before making requests
