"""Vault operations as AI-callable tools.

This module exposes VaultConnector methods as LangChain tools:
- read_secret / get_secret / write_secret
- list_secrets
- AWS IAM: list_aws_iam_roles, get_aws_iam_role, generate_aws_credentials

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    VAULT_TOOL_METHODS = [
        "read_secret",
        "get_secret",
        "write_secret",
        "list_secrets",
        "list_aws_iam_roles",
        "get_aws_iam_role",
        "generate_aws_credentials",
    ]

    def get_vault_tools() -> list[StructuredTool]:
        tools = []
        for method_name in VAULT_TOOL_METHODS:
            tool = create_tool_from_method(
                VaultConnector,
                method_name,
                exclude_params=["logger", "inputs"],
            )
            register_tool(tool, category=ToolCategory.VAULT)
            tools.append(tool)
        return tools
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
