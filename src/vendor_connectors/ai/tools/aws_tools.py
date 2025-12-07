"""AWS operations as AI-callable tools.

This module exposes AWSConnector methods as LangChain tools:
- get_secret / list_secrets / create_secret / update_secret / delete_secret
- get_aws_client / get_aws_resource / get_aws_session
- get_caller_account_id
- Plus methods from mixins (Organizations, SSO, S3)

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    AWS_TOOL_METHODS = [
        "get_secret",
        "list_secrets",
        "create_secret",
        "update_secret",
        "delete_secret",
        "get_caller_account_id",
    ]

    def get_aws_tools() -> list[StructuredTool]:
        tools = []
        for method_name in AWS_TOOL_METHODS:
            tool = create_tool_from_method(
                AWSConnector,
                method_name,
                exclude_params=["secretsmanager"],  # Internal
            )
            register_tool(tool, category=ToolCategory.AWS)
            tools.append(tool)
        return tools
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
