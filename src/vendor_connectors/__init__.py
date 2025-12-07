"""Vendor Connectors - Universal vendor connectors for the jbcom ecosystem.

This package provides modular connectors for various cloud providers and services:
- Anthropic: Claude AI API and Agent SDK (NEW)
- AWS: Organizations, SSO/Identity Center, S3, Secrets Manager
- Cursor: Background Agent API for AI coding agents (NEW)
- Google Cloud: Workspace, Cloud Platform, Billing, Services (GKE, Compute, etc.)
- GitHub: Repository operations, PR management
- Meshy: 3D asset generation
- Slack: Channel and message operations
- Vault: HashiCorp Vault secret management
- Zoom: User and meeting management
- Meshy: AI 3D asset generation

Usage:
    # Basic connector (session management + secrets)
    from vendor_connectors import AWSConnector
    connector = AWSConnector()

    # Full connector with all operations
    from vendor_connectors.aws import AWSConnectorFull
    connector = AWSConnectorFull()
    accounts = connector.get_accounts()

    # Cursor AI agents
    from vendor_connectors.cursor import CursorConnector
    cursor = CursorConnector()
    agents = cursor.list_agents()

    # Anthropic Claude AI
    from vendor_connectors.anthropic import AnthropicConnector
    anthropic = AnthropicConnector()
    response = anthropic.create_message(...)

    # Mixin approach for custom connectors
    from vendor_connectors.aws import AWSConnector, AWSOrganizationsMixin

    class MyConnector(AWSConnector, AWSOrganizationsMixin):
        pass

    # Meshy AI 3D generation (functional interface)
    from vendor_connectors.meshy import text3d, image3d, rigging, animate

    model = text3d.generate("a medieval sword")
    rigged = rigging.rig(model.id)
    animated = animate.apply(rigged.id, animation_id=0)

    # AI tools for agents
    from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools
    from vendor_connectors.ai.providers.crewai import get_tools
"""

from __future__ import annotations

__version__ = "0.2.0"

# Sub-packages
from vendor_connectors import ai, meshy

# AI/Agent connectors
from vendor_connectors.anthropic import AnthropicConnector
from vendor_connectors.aws import (
    AWSConnector,
    AWSConnectorFull,
    AWSOrganizationsMixin,
    AWSS3Mixin,
    AWSSSOmixin,
)
from vendor_connectors.cloud_params import (
    get_aws_call_params,
    get_cloud_call_params,
    get_google_call_params,
)
from vendor_connectors.connectors import VendorConnectors
from vendor_connectors.cursor import CursorConnector
from vendor_connectors.github import GithubConnector
from vendor_connectors.google import (
    GoogleBillingMixin,
    GoogleCloudMixin,
    GoogleConnector,
    GoogleConnectorFull,
    GoogleServicesMixin,
    GoogleWorkspaceMixin,
)
from vendor_connectors.slack import SlackConnector
from vendor_connectors.vault import VaultConnector
from vendor_connectors.zoom import ZoomConnector

__all__ = [
    # AI/Agent connectors
    "AnthropicConnector",
    "CursorConnector",
    # AWS
    "AWSConnector",
    "AWSConnectorFull",
    "AWSOrganizationsMixin",
    "AWSSSOmixin",
    "AWSS3Mixin",
    # Google
    "GoogleConnector",
    "GoogleConnectorFull",
    "GoogleWorkspaceMixin",
    "GoogleCloudMixin",
    "GoogleBillingMixin",
    "GoogleServicesMixin",
    # Other connectors
    "GithubConnector",
    "SlackConnector",
    "VaultConnector",
    "ZoomConnector",
    "VendorConnectors",
    # Cloud param utilities
    "get_cloud_call_params",
    "get_aws_call_params",
    "get_google_call_params",
    # Meshy AI (3D asset generation) - functional interface
    "meshy",
    # AI tools sub-package
    "ai",
]
