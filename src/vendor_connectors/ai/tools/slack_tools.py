"""Slack operations as AI-callable tools.

This module exposes SlackConnector methods as LangChain tools:
- send_message - Send messages to channels
- get_bot_channels - List channels bot is in
- list_users - List workspace users
- list_usergroups - List user groups
- list_conversations - List channels/conversations

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    SLACK_TOOL_METHODS = [
        "send_message",
        "get_bot_channels",
        "list_users",
        "list_usergroups",
        "list_conversations",
    ]

    def get_slack_tools() -> list[StructuredTool]:
        tools = []
        for method_name in SLACK_TOOL_METHODS:
            tool = create_tool_from_method(
                SlackConnector,
                method_name,
                exclude_params=["logger", "inputs"],
            )
            register_tool(tool, category=ToolCategory.SLACK)
            tools.append(tool)
        return tools
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
