"""Pytest configuration and shared fixtures for cloud-connectors tests."""

import pytest
from unittest.mock import Mock
from typing import Dict, Any


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    return Mock()


@pytest.fixture
def test_inputs() -> Dict[str, Any]:
    """Provide standard test input dictionary."""
    return {
        "VERBOSE": "false",
        "VERBOSITY": "1",
        "LOG_FILE_NAME": "test.log",
    }


@pytest.fixture
def aws_credentials() -> Dict[str, str]:
    """Provide mock AWS credentials."""
    return {
        "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "SessionToken": "TOKEN_EXAMPLE",
    }


@pytest.fixture
def github_token() -> str:
    """Provide mock GitHub token."""
    return "ghp_test1234567890abcdefghijklmnopqrs"


@pytest.fixture
def google_service_account() -> Dict[str, str]:
    """Provide mock Google service account data."""
    return {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "key123",
        "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    }


@pytest.fixture
def slack_tokens() -> Dict[str, str]:
    """Provide mock Slack tokens."""
    return {
        "token": "xoxp-test-token",
        "bot_token": "xoxb-test-bot-token",
    }


@pytest.fixture
def vault_config() -> Dict[str, str]:
    """Provide mock Vault configuration."""
    return {
        "vault_address": "https://vault.example.com",
        "vault_namespace": "test-namespace",
        "vault_token": "s.test1234567890",
    }


@pytest.fixture
def zoom_credentials() -> Dict[str, str]:
    """Provide mock Zoom credentials."""
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "account_id": "test_account_id",
    }
