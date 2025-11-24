# Testing Guidelines for Cloud Connectors

## Testing Strategy

### Test Pyramid
```
         /\
        /  \  E2E Tests (few)
       /----\
      /      \ Integration Tests (some)
     /--------\
    /          \ Unit Tests (many)
   /____________\
```

## Unit Testing

### Structure
```
tests/
├── unit/
│   ├── test_aws_connector.py
│   ├── test_github_connector.py
│   ├── test_google_connector.py
│   ├── test_slack_connector.py
│   ├── test_vault_connector.py
│   └── test_zoom_connector.py
├── integration/
│   └── (integration tests with mocked services)
├── fixtures/
│   └── (shared test data and fixtures)
└── conftest.py (pytest configuration)
```

### Unit Test Pattern
```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from cloud_connectors.aws import AWSConnector

class TestAWSConnector:
    @pytest.fixture
    def connector(self):
        """Fixture providing a test connector instance."""
        return AWSConnector(
            execution_role_arn="arn:aws:iam::123456789012:role/TestRole",
            inputs={"VERBOSE": "false"}
        )
    
    def test_init(self, connector):
        """Test connector initialization."""
        assert connector.execution_role_arn == "arn:aws:iam::123456789012:role/TestRole"
        assert connector.aws_sessions == {}
    
    @patch('boto3.Session')
    def test_assume_role(self, mock_session, connector):
        """Test role assumption."""
        # Setup mock
        mock_sts = Mock()
        mock_session.return_value.client.return_value = mock_sts
        mock_sts.assume_role.return_value = {
            'Credentials': {
                'AccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
                'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
                'SessionToken': 'TOKEN',
                'Expiration': datetime.now()
            }
        }
        
        # Execute
        session = connector.assume_role(
            execution_role_arn="arn:aws:iam::123:role/Test",
            role_session_name="test-session"
        )
        
        # Assert
        assert session is not None
        mock_sts.assume_role.assert_called_once()
```

## Integration Testing

### Mocking Services
- **AWS**: Use `moto` library
- **HTTP APIs**: Use `responses` library
- **GitHub**: Mock PyGithub objects
- **Google**: Mock googleapiclient
- **Slack**: Mock slack_sdk WebClient
- **Vault**: Mock hvac.Client

### Integration Test Pattern
```python
import pytest
from moto import mock_sts, mock_s3
from cloud_connectors.aws import AWSConnector

@mock_sts
@mock_s3
class TestAWSIntegration:
    def test_s3_operations(self):
        """Test S3 operations with mocked AWS."""
        connector = AWSConnector()
        s3 = connector.get_aws_client("s3")
        
        # Test bucket operations
        s3.create_bucket(Bucket='test-bucket')
        response = s3.list_buckets()
        
        assert len(response['Buckets']) == 1
        assert response['Buckets'][0]['Name'] == 'test-bucket'
```

## Test Fixtures

### Common Fixtures (`conftest.py`)
```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_logger():
    """Provide a mock logger."""
    return Mock()

@pytest.fixture
def test_inputs():
    """Provide test input dictionary."""
    return {
        "VERBOSE": "false",
        "VERBOSITY": "1",
        "LOG_FILE_NAME": "test.log"
    }

@pytest.fixture
def aws_credentials():
    """Provide mock AWS credentials."""
    return {
        'AccessKeyId': 'AKIAIOSFODNN7EXAMPLE',
        'SecretAccessKey': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'SessionToken': 'TOKEN'
    }
```

## Coverage Requirements

### Target Coverage
- Overall: 80%+
- Critical paths (auth, API calls): 95%+
- Utility functions: 90%+

### Running Coverage
```bash
pytest --cov=src/cloud_connectors --cov-report=html --cov-report=term
```

### Coverage Configuration (`pyproject.toml`)
```toml
[tool.coverage.run]
source = ["src/cloud_connectors"]
omit = ["*/tests/*", "*/test_*.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

## Test Organization

### Test Naming
- File: `test_<module_name>.py`
- Class: `Test<ClassName>`
- Method: `test_<what_it_tests>`

### Test Documentation
```python
def test_connector_caching(self, connector):
    """
    Test that connector properly caches sessions.
    
    Given: A connector with a role ARN
    When: get_aws_session is called multiple times
    Then: The same session object is returned (cached)
    """
    # Test implementation
```

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11, 3.12, 3.13]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          pip install -e ".[tests]"
      - name: Run tests
        run: pytest --cov --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Fast**: Unit tests should run in milliseconds
3. **Deterministic**: Same input = same output
4. **Descriptive**: Test names should explain what they test
5. **Arrange-Act-Assert**: Structure tests clearly
6. **Mock External**: Never hit real APIs in tests
7. **Clean Up**: Use fixtures for setup/teardown
8. **Parameterize**: Use `pytest.mark.parametrize` for similar tests

## Example: Complete Test File
```python
# tests/unit/test_github_connector.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from cloud_connectors.github import GithubConnector

class TestGithubConnector:
    @pytest.fixture
    def mock_github(self):
        with patch('cloud_connectors.github.Github') as mock:
            yield mock
    
    @pytest.fixture
    def connector(self, mock_github):
        return GithubConnector(
            github_owner="testorg",
            github_repo="testrepo",
            github_token="ghp_test"
        )
    
    def test_init(self, connector):
        """Test connector initializes with correct values."""
        assert connector.GITHUB_OWNER == "testorg"
        assert connector.GITHUB_REPO == "testrepo"
    
    def test_get_repository_file(self, connector):
        """Test file retrieval from repository."""
        # Setup
        mock_content = Mock()
        mock_content.decoded_content = b"test content"
        mock_content.sha = "abc123"
        connector.repo.get_contents.return_value = mock_content
        
        # Execute
        result = connector.get_repository_file("test.txt", decode=False)
        
        # Assert
        assert result == "test content"
        connector.repo.get_contents.assert_called_once_with("test.txt", ref=connector.GITHUB_BRANCH)
```
