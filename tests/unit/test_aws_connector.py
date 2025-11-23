"""Unit tests for AWSConnector."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from cloud_connectors.aws import AWSConnector


class TestAWSConnector:
    """Test suite for AWSConnector."""

    @pytest.fixture
    def connector(self, test_inputs):
        """Provide a test AWSConnector instance."""
        return AWSConnector(
            execution_role_arn="arn:aws:iam::123456789012:role/TestRole",
            inputs=test_inputs,
        )

    def test_init(self, connector):
        """Test connector initializes with correct values."""
        assert connector.execution_role_arn == "arn:aws:iam::123456789012:role/TestRole"
        assert connector.aws_sessions == {}
        assert connector.aws_clients == {}
        assert connector.default_aws_session is not None

    def test_init_without_role(self, test_inputs):
        """Test connector initializes without execution role."""
        connector = AWSConnector(inputs=test_inputs)
        assert connector.execution_role_arn is None
        assert connector.default_aws_session is not None

    @patch("cloud_connectors.aws.boto3.Session")
    def test_assume_role_success(self, mock_session_class, connector, aws_credentials):
        """Test successful role assumption."""
        # Setup mock STS client
        mock_sts = Mock()
        connector.default_aws_session.client = Mock(return_value=mock_sts)

        # Mock assume_role response
        mock_sts.assume_role.return_value = {
            "Credentials": {
                **aws_credentials,
                "Expiration": datetime.now(),
            }
        }

        # Mock the boto3.Session constructor
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Execute
        session = connector.assume_role(
            execution_role_arn="arn:aws:iam::123456789012:role/TestRole",
            role_session_name="test-session",
        )

        # Assert
        assert session == mock_session
        mock_sts.assume_role.assert_called_once_with(
            RoleArn="arn:aws:iam::123456789012:role/TestRole",
            RoleSessionName="test-session",
        )
        mock_session_class.assert_called_once()

    @patch("cloud_connectors.aws.boto3.Session")
    def test_assume_role_failure(self, mock_session_class, connector):
        """Test role assumption failure handling."""
        # Setup mock STS client that raises error
        from botocore.exceptions import ClientError

        mock_sts = Mock()
        connector.default_aws_session.client = Mock(return_value=mock_sts)
        mock_sts.assume_role.side_effect = ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}},
            "AssumeRole",
        )

        # Execute and assert
        with pytest.raises(RuntimeError, match="Failed to assume role"):
            connector.assume_role(
                execution_role_arn="arn:aws:iam::123456789012:role/TestRole",
                role_session_name="test-session",
            )

    def test_get_aws_session_default(self, connector):
        """Test getting default AWS session."""
        session = connector.get_aws_session()
        assert session == connector.default_aws_session

    def test_create_standard_retry_config(self):
        """Test creating standard retry configuration."""
        config = AWSConnector.create_standard_retry_config(max_attempts=5)
        assert config.retries["max_attempts"] == 5
        assert config.retries["mode"] == "standard"

    def test_create_standard_retry_config_custom(self):
        """Test creating retry config with custom attempts."""
        config = AWSConnector.create_standard_retry_config(max_attempts=10)
        assert config.retries["max_attempts"] == 10

    @patch("cloud_connectors.aws.boto3.Session")
    def test_get_aws_client_with_default_config(self, mock_session_class, connector):
        """Test getting AWS client with default retry config."""
        mock_session = Mock()
        connector.get_aws_session = Mock(return_value=mock_session)

        mock_client = Mock()
        mock_session.client = Mock(return_value=mock_client)

        # Execute
        client = connector.get_aws_client("s3")

        # Assert
        assert client == mock_client
        mock_session.client.assert_called_once()
        call_kwargs = mock_session.client.call_args[1]
        assert call_kwargs["config"].retries["max_attempts"] == 5

    def test_session_caching(self, connector):
        """Test that sessions are properly cached."""
        # Mock assume_role to return a fake session
        fake_session = Mock()
        connector.assume_role = Mock(return_value=fake_session)

        # Call get_aws_session twice with same role
        role_arn = "arn:aws:iam::123456789012:role/TestRole"
        session1 = connector.get_aws_session(
            execution_role_arn=role_arn, role_session_name="session1"
        )
        session2 = connector.get_aws_session(
            execution_role_arn=role_arn, role_session_name="session1"
        )

        # Assert session is cached (assume_role called only once)
        assert session1 == session2
        connector.assume_role.assert_called_once()


# TODO: Add more test cases:
# - test_get_aws_client_with_custom_config
# - test_get_aws_resource
# - test_session_caching_multiple_roles
# - test_error_handling_for_invalid_client_name
