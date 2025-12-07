"""Tests for VendorConnectors main class."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from vendor_connectors.connectors import VendorConnectors


class TestVendorConnectors:
    """Tests for VendorConnectors class."""

    def test_init(self):
        """Test VendorConnectors initialization."""
        vc = VendorConnectors()
        assert vc.logger is not None
        assert vc._client_cache is not None

    def test_init_with_logger(self):
        """Test VendorConnectors initialization with custom logger."""
        mock_logger = MagicMock()
        vc = VendorConnectors(logger=mock_logger)
        assert vc.logging == mock_logger
        assert vc.logger is not None  # Logger is extracted from logging

    def test_get_cache_key(self):
        """Test cache key generation."""
        vc = VendorConnectors()
        key1 = vc._get_cache_key(param1="value1", param2="value2")
        key2 = vc._get_cache_key(param1="value1", param2="value2")
        key3 = vc._get_cache_key(param1="value1", param2="different")

        assert key1 == key2
        assert key1 != key3

    def test_cache_client(self):
        """Test caching and retrieving clients."""
        vc = VendorConnectors()
        mock_client = MagicMock()

        # Set cache
        vc._set_cached_client("test_type", mock_client, param="value")

        # Get from cache
        cached = vc._get_cached_client("test_type", param="value")
        assert cached == mock_client

        # Different params should return None
        cached = vc._get_cached_client("test_type", param="different")
        assert cached is None

    @patch("vendor_connectors.connectors.AWSConnector")
    def test_get_aws_connector(self, mock_aws):
        """Test getting AWS connector."""
        vc = VendorConnectors()
        mock_connector = MagicMock()
        mock_aws.return_value = mock_connector

        result = vc.get_aws_connector(execution_role_arn="arn:aws:iam::123456789012:role/TestRole")

        assert result == mock_connector
        mock_aws.assert_called_once()

    @patch("vendor_connectors.connectors.AWSConnector")
    def test_get_aws_connector_caching(self, mock_aws):
        """Test AWS connector caching."""
        vc = VendorConnectors()
        mock_connector = MagicMock()
        mock_aws.return_value = mock_connector

        # First call
        result1 = vc.get_aws_connector(execution_role_arn="arn:aws:iam::123456789012:role/TestRole")
        # Second call with same params
        result2 = vc.get_aws_connector(execution_role_arn="arn:aws:iam::123456789012:role/TestRole")

        assert result1 == result2
        # Should only create connector once
        mock_aws.assert_called_once()

    @patch("vendor_connectors.connectors.AWSConnector")
    def test_get_aws_client(self, mock_aws):
        """Test getting AWS client."""
        vc = VendorConnectors()
        mock_connector = MagicMock()
        mock_client = MagicMock()
        mock_connector.get_aws_client.return_value = mock_client
        mock_aws.return_value = mock_connector

        result = vc.get_aws_client("s3")

        assert result == mock_client
        mock_connector.get_aws_client.assert_called_once()

    @patch("vendor_connectors.connectors.AWSConnector")
    def test_get_aws_resource(self, mock_aws):
        """Test getting AWS resource."""
        vc = VendorConnectors()
        mock_connector = MagicMock()
        mock_resource = MagicMock()
        mock_connector.get_aws_resource.return_value = mock_resource
        mock_aws.return_value = mock_connector

        result = vc.get_aws_resource("s3")

        assert result == mock_resource
        mock_connector.get_aws_resource.assert_called_once()

    @patch("vendor_connectors.connectors.GoogleConnector")
    def test_get_google_client(self, mock_google):
        """Test getting Google client."""
        vc = VendorConnectors(inputs={
            "GOOGLE_SERVICE_ACCOUNT": '{"type": "service_account"}',
            "GOOGLE_PROJECT_ID": "test-project"
        })
        mock_connector = MagicMock()
        mock_client = MagicMock()
        mock_connector.get_service.return_value = mock_client
        mock_google.return_value = mock_connector

        result = vc.get_google_client()

        assert result == mock_connector

    @patch("vendor_connectors.connectors.GithubConnector")
    def test_get_github_client(self, mock_github):
        """Test getting GitHub client."""
        vc = VendorConnectors(inputs={
            "GITHUB_OWNER": "test-org",
            "GITHUB_TOKEN": "ghp_test123"
        })
        mock_connector = MagicMock()
        mock_github.return_value = mock_connector

        result = vc.get_github_client()

        assert result == mock_connector

    @patch("vendor_connectors.connectors.SlackConnector")
    def test_get_slack_client(self, mock_slack):
        """Test getting Slack client."""
        vc = VendorConnectors(inputs={
            "SLACK_TOKEN": "xoxp-test123",
            "SLACK_BOT_TOKEN": "xoxb-test123"
        })
        mock_connector = MagicMock()
        mock_slack.return_value = mock_connector

        result = vc.get_slack_client()

        assert result == mock_connector

    @patch("vendor_connectors.connectors.VaultConnector")
    def test_get_vault_connector(self, mock_vault):
        """Test getting Vault connector."""
        vc = VendorConnectors()
        mock_connector = MagicMock()
        mock_vault.return_value = mock_connector

        result = vc.get_vault_connector(vault_token="hvs.test123")

        assert result == mock_connector

    @patch("vendor_connectors.connectors.ZoomConnector")
    def test_get_zoom_client(self, mock_zoom):
        """Test getting Zoom client."""
        vc = VendorConnectors(inputs={
            "ZOOM_CLIENT_ID": "test-client-id",
            "ZOOM_CLIENT_SECRET": "test-secret",
            "ZOOM_ACCOUNT_ID": "test-account"
        })
        mock_connector = MagicMock()
        mock_zoom.return_value = mock_connector

        result = vc.get_zoom_client()

        assert result == mock_connector

    @patch("vendor_connectors.connectors.VaultConnector")
    def test_get_vault_client(self, mock_vault):
        """Test getting Vault client."""
        vc = VendorConnectors()
        mock_connector = MagicMock()
        mock_client = MagicMock()
        mock_connector.vault_client = mock_client
        mock_vault.return_value = mock_connector

        result = vc.get_vault_client(vault_token="hvs.test123")

        assert result == mock_client

    def test_multiple_connector_types_cached_separately(self):
        """Test that different connector types are cached separately."""
        with patch("vendor_connectors.connectors.AWSConnector") as mock_aws, \
             patch("vendor_connectors.connectors.SlackConnector") as mock_slack:
            vc = VendorConnectors(inputs={
                "SLACK_TOKEN": "xoxp-test123",
                "SLACK_BOT_TOKEN": "xoxb-test123"
            })
            mock_aws_connector = MagicMock()
            mock_slack_connector = MagicMock()
            mock_aws.return_value = mock_aws_connector
            mock_slack.return_value = mock_slack_connector

            aws1 = vc.get_aws_connector()
            slack1 = vc.get_slack_client()
            vc.get_aws_connector()
            vc.get_slack_client()

            # Each connector type should only be created once
            mock_aws.assert_called_once()
            mock_slack.assert_called_once()

            # But they should be different objects
            assert aws1 != slack1
