# Cloud Connectors

[![CI](https://github.com/jbcom/cloud-connectors/actions/workflows/ci.yml/badge.svg)](https://github.com/jbcom/cloud-connectors/actions/workflows/ci.yml)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Universal cloud provider connectors with transparent secret management and standardized interfaces.

## Features

- **AWS Connector**: Boto3-based client with role assumption and retry logic
- **Google Cloud Connector**: Workspace and Cloud Platform APIs with lazy credential loading  
- **GitHub Connector**: Repository management, GraphQL queries, and file operations
- **Slack Connector**: Bot and app integrations with rate limiting
- **Vault Connector**: HashiCorp Vault with Token and AppRole auth
- **Zoom Connector**: Meeting and user management

## Installation

```bash
pip install cloud-connectors
```

## Usage

```python
from cloud_connectors import AWSConnector, GithubConnector

# AWS with role assumption
aws = AWSConnector(execution_role_arn="arn:aws:iam::123456789012:role/MyRole")
s3 = aws.get_aws_client("s3")

# GitHub operations
github = GithubConnector(
    github_owner="myorg",
    github_repo="myrepo", 
    github_token=os.getenv("GITHUB_TOKEN")
)
repo = github.repo
```

## Architecture

All connectors inherit from a base `Utils` class that provides:
- Directed inputs (environment variables, config files, stdin)
- Lifecycle logging with rich formatting
- Caching and memoization
- Standardized error handling

Connectors use lazy initialization and credential caching for optimal performance.

## Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Development Status

**Current Version:** 0.1.0 (Beta)

✅ **Implemented:**
- All advertised connectors (AWS, GitHub, Google, Slack, Vault, Zoom)
- Base Utils class with full feature set
- Type hints throughout codebase
- Error handling infrastructure

🚧 **In Progress:**
- Comprehensive test suite
- CI/CD pipelines
- API documentation
- PyPI publication

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- **Issues:** [GitHub Issues](https://github.com/jbcom/cloud-connectors/issues)
- **Security:** See [SECURITY.md](SECURITY.md) for vulnerability reporting
- **Email:** jon@jonbogaty.com
