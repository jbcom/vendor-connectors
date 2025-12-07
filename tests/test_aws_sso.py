"""Tests for AWS SSO/Identity Center operations."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from vendor_connectors.aws import AWSConnectorFull


@pytest.fixture
def aws_connector():
    """Create AWS connector with mocked clients."""
    with patch("vendor_connectors.aws.boto3"):
        connector = AWSConnectorFull()
        connector.logger = MagicMock()
        return connector


class TestSSOIdentityStore:
    """Tests for SSO identity store operations."""

    def test_get_identity_store_id(self, aws_connector):
        """Test getting identity store ID."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.list_instances.return_value = {
            "Instances": [
                {
                    "IdentityStoreId": "d-1234567890",
                    "InstanceArn": "arn:aws:sso:::instance/ssoins-1234567890",
                }
            ]
        }
        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        result = aws_connector.get_identity_store_id()

        assert result == "d-1234567890"
        aws_connector.get_aws_client.assert_called_once_with(
            client_name="sso-admin", execution_role_arn=None
        )

    def test_get_identity_store_id_no_instance(self, aws_connector):
        """Test getting identity store ID with no instances."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.list_instances.return_value = {"Instances": []}
        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        with pytest.raises(RuntimeError, match="No SSO instances found"):
            aws_connector.get_identity_store_id()

    def test_get_sso_instance_arn(self, aws_connector):
        """Test getting SSO instance ARN."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.list_instances.return_value = {
            "Instances": [
                {
                    "InstanceArn": "arn:aws:sso:::instance/ssoins-1234567890",
                    "IdentityStoreId": "d-1234567890",
                }
            ]
        }
        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        result = aws_connector.get_sso_instance_arn()

        assert result == "arn:aws:sso:::instance/ssoins-1234567890"

    def test_get_sso_instance_arn_no_instance(self, aws_connector):
        """Test getting SSO instance ARN with no instances."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.list_instances.return_value = {"Instances": []}
        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        with pytest.raises(RuntimeError, match="No SSO instances found"):
            aws_connector.get_sso_instance_arn()


class TestSSOUsers:
    """Tests for SSO user operations."""

    def test_list_sso_users(self, aws_connector):
        """Test listing SSO users."""
        mock_identitystore = MagicMock()
        mock_identitystore.list_users.return_value = {
            "Users": [
                {
                    "UserId": "user-1",
                    "UserName": "john.doe",
                    "Name": {"GivenName": "John", "FamilyName": "Doe"},
                },
                {
                    "UserId": "user-2",
                    "UserName": "jane.smith",
                    "Name": {"GivenName": "Jane", "FamilyName": "Smith"},
                },
            ]
        }

        def get_client(client_name, **kwargs):
            if client_name == "identitystore":
                return mock_identitystore
            mock_sso_admin = MagicMock()
            mock_sso_admin.list_instances.return_value = {
                "Instances": [{"IdentityStoreId": "d-1234567890"}]
            }
            return mock_sso_admin

        aws_connector.get_aws_client = MagicMock(side_effect=get_client)

        result = aws_connector.list_sso_users(unhump_users=False, flatten_name=False)

        assert len(result) == 2
        assert "user-1" in result
        assert "user-2" in result
        assert result["user-1"]["UserName"] == "john.doe"

    def test_list_sso_users_with_flatten_name(self, aws_connector):
        """Test listing SSO users with flattened names."""
        mock_identitystore = MagicMock()
        mock_identitystore.list_users.return_value = {
            "Users": [
                {
                    "UserId": "user-1",
                    "UserName": "john.doe",
                    "Name": {"GivenName": "John", "FamilyName": "Doe"},
                }
            ]
        }

        def get_client(client_name, **kwargs):
            if client_name == "identitystore":
                return mock_identitystore
            mock_sso_admin = MagicMock()
            mock_sso_admin.list_instances.return_value = {
                "Instances": [{"IdentityStoreId": "d-1234567890"}]
            }
            return mock_sso_admin

        aws_connector.get_aws_client = MagicMock(side_effect=get_client)

        result = aws_connector.list_sso_users(
            unhump_users=False, flatten_name=True, identity_store_id="d-1234567890"
        )

        assert len(result) == 1
        assert result["user-1"]["GivenName"] == "John"
        assert result["user-1"]["FamilyName"] == "Doe"

    def test_list_sso_users_pagination(self, aws_connector):
        """Test listing SSO users with pagination."""
        mock_identitystore = MagicMock()
        mock_identitystore.list_users.side_effect = [
            {
                "Users": [{"UserId": "user-1", "UserName": "user1"}],
                "NextToken": "token123",
            },
            {"Users": [{"UserId": "user-2", "UserName": "user2"}]},
        ]

        aws_connector.get_aws_client = MagicMock(return_value=mock_identitystore)

        result = aws_connector.list_sso_users(
            identity_store_id="d-1234567890", unhump_users=False, flatten_name=False
        )

        assert len(result) == 2
        assert mock_identitystore.list_users.call_count == 2

    def test_list_sso_users_sort_by_name(self, aws_connector):
        """Test listing SSO users sorted by name."""
        mock_identitystore = MagicMock()
        mock_identitystore.list_users.return_value = {
            "Users": [
                {"UserId": "user-1", "UserName": "zoe"},
                {"UserId": "user-2", "UserName": "alice"},
                {"UserId": "user-3", "UserName": "mike"},
            ]
        }

        aws_connector.get_aws_client = MagicMock(return_value=mock_identitystore)

        result = aws_connector.list_sso_users(
            identity_store_id="d-1234567890",
            unhump_users=False,
            flatten_name=False,
            sort_by_name=True,
        )

        user_ids = list(result.keys())
        assert user_ids == ["user-2", "user-3", "user-1"]  # alice, mike, zoe

    def test_get_sso_user(self, aws_connector):
        """Test getting a specific SSO user."""
        mock_identitystore = MagicMock()
        mock_identitystore.describe_user.return_value = {
            "UserId": "user-1",
            "UserName": "john.doe",
            "Name": {"GivenName": "John"},
        }

        aws_connector.get_aws_client = MagicMock(return_value=mock_identitystore)

        result = aws_connector.get_sso_user("user-1", identity_store_id="d-1234567890")

        assert result["UserId"] == "user-1"
        assert result["UserName"] == "john.doe"

    def test_get_sso_user_not_found(self, aws_connector):
        """Test getting a non-existent SSO user."""
        mock_identitystore = MagicMock()
        error = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "DescribeUser"
        )
        mock_identitystore.describe_user.side_effect = error

        aws_connector.get_aws_client = MagicMock(return_value=mock_identitystore)

        result = aws_connector.get_sso_user("missing-user", identity_store_id="d-1234567890")

        assert result is None

    def test_get_sso_user_other_error(self, aws_connector):
        """Test getting SSO user with other error."""
        mock_identitystore = MagicMock()
        error = ClientError({"Error": {"Code": "AccessDenied"}}, "DescribeUser")
        mock_identitystore.describe_user.side_effect = error

        aws_connector.get_aws_client = MagicMock(return_value=mock_identitystore)

        with pytest.raises(ClientError):
            aws_connector.get_sso_user("user-1", identity_store_id="d-1234567890")


class TestSSOGroups:
    """Tests for SSO group operations."""

    def test_list_sso_groups(self, aws_connector):
        """Test listing SSO groups."""
        mock_identitystore = MagicMock()
        mock_identitystore.list_groups.return_value = {
            "Groups": [
                {"GroupId": "group-1", "DisplayName": "Admins"},
                {"GroupId": "group-2", "DisplayName": "Users"},
            ]
        }
        # Mock list_group_memberships to prevent infinite loops
        mock_identitystore.list_group_memberships.return_value = {
            "GroupMemberships": []
        }

        def get_client(client_name, **kwargs):
            if client_name == "identitystore":
                return mock_identitystore
            mock_sso_admin = MagicMock()
            mock_sso_admin.list_instances.return_value = {
                "Instances": [{"IdentityStoreId": "d-1234567890"}]
            }
            return mock_sso_admin

        aws_connector.get_aws_client = MagicMock(side_effect=get_client)

        result = aws_connector.list_sso_groups(unhump_groups=False)

        assert len(result) == 2
        assert "group-1" in result
        assert result["group-1"]["DisplayName"] == "Admins"

    def test_get_sso_group(self, aws_connector):
        """Test getting a specific SSO group."""
        mock_identitystore = MagicMock()
        mock_identitystore.describe_group.return_value = {
            "GroupId": "group-1",
            "DisplayName": "Admins",
        }

        aws_connector.get_aws_client = MagicMock(return_value=mock_identitystore)

        result = aws_connector.get_sso_group("group-1", identity_store_id="d-1234567890")

        assert result["GroupId"] == "group-1"
        assert result["DisplayName"] == "Admins"

    def test_get_sso_group_not_found(self, aws_connector):
        """Test getting a non-existent SSO group."""
        mock_identitystore = MagicMock()
        error = ClientError(
            {"Error": {"Code": "ResourceNotFoundException"}}, "DescribeGroup"
        )
        mock_identitystore.describe_group.side_effect = error

        aws_connector.get_aws_client = MagicMock(return_value=mock_identitystore)

        result = aws_connector.get_sso_group("missing-group", identity_store_id="d-1234567890")

        assert result is None


class TestSSOPermissionSets:
    """Tests for SSO permission set operations."""

    def test_list_permission_sets(self, aws_connector):
        """Test listing permission sets."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.list_instances.return_value = {
            "Instances": [{"InstanceArn": "arn:aws:sso:::instance/ssoins-1234567890"}]
        }
        mock_sso_admin.list_permission_sets.return_value = {
            "PermissionSets": [
                "arn:aws:sso:::permissionSet/ssoins-1234567890/ps-1",
                "arn:aws:sso:::permissionSet/ssoins-1234567890/ps-2",
            ]
        }
        mock_sso_admin.describe_permission_set.side_effect = [
            {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/ssoins-1234567890/ps-1",
                    "Name": "AdminAccess",
                }
            },
            {
                "PermissionSet": {
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/ssoins-1234567890/ps-2",
                    "Name": "ReadOnlyAccess",
                }
            },
        ]

        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        result = aws_connector.list_permission_sets(unhump_permission_sets=False)

        assert len(result) == 2
        assert "ps-1" in result
        assert result["ps-1"]["Name"] == "AdminAccess"

    def test_get_permission_set(self, aws_connector):
        """Test getting a specific permission set."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.describe_permission_set.return_value = {
            "PermissionSet": {
                "PermissionSetArn": "arn:aws:sso:::permissionSet/ssoins-1234567890/ps-1",
                "Name": "AdminAccess",
            }
        }

        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        result = aws_connector.get_permission_set(
            "arn:aws:sso:::permissionSet/ssoins-1234567890/ps-1",
            instance_arn="arn:aws:sso:::instance/ssoins-1234567890",
        )

        assert result["Name"] == "AdminAccess"


class TestSSOAccountAssignments:
    """Tests for SSO account assignment operations."""

    def test_list_account_assignments(self, aws_connector):
        """Test listing account assignments."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.list_account_assignments.return_value = {
            "AccountAssignments": [
                {
                    "AccountId": "123456789012",
                    "PermissionSetArn": "arn:aws:sso:::permissionSet/ssoins-1234567890/ps-1",
                    "PrincipalType": "USER",
                    "PrincipalId": "user-1",
                }
            ]
        }

        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        result = aws_connector.list_account_assignments(
            instance_arn="arn:aws:sso:::instance/ssoins-1234567890",
            account_id="123456789012",
            permission_set_arn="arn:aws:sso:::permissionSet/ssoins-1234567890/ps-1",
            unhump_assignments=False,
        )

        assert len(result) == 1
        assert result[0]["AccountId"] == "123456789012"
        assert result[0]["PrincipalType"] == "USER"

    def test_list_accounts_for_provisioned_permission_set(self, aws_connector):
        """Test listing accounts for a provisioned permission set."""
        mock_sso_admin = MagicMock()
        mock_sso_admin.list_accounts_for_provisioned_permission_set.return_value = {
            "AccountIds": ["123456789012", "210987654321"]
        }

        aws_connector.get_aws_client = MagicMock(return_value=mock_sso_admin)

        result = aws_connector.list_accounts_for_provisioned_permission_set(
            instance_arn="arn:aws:sso:::instance/ssoins-1234567890",
            permission_set_arn="arn:aws:sso:::permissionSet/ssoins-1234567890/ps-1",
        )

        assert len(result) == 2
        assert "123456789012" in result
        assert "210987654321" in result
