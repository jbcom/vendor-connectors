"""Vendor connectors as AI-callable tools.

This package provides:
- Tool registry for managing connector-based tools
- Auto-generation of LangChain tools from connector methods
- Pre-built tools for AWS, GitHub, Slack, Vault, Google, Zoom

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Usage (after implementation):
    from vendor_connectors.ai.tools import get_all_tools, get_tools_by_category
    from vendor_connectors.ai.base import ToolCategory

    # Get all tools
    all_tools = get_all_tools()

    # Get tools for specific categories
    github_tools = get_tools_by_category(ToolCategory.GITHUB)
    aws_tools = get_tools_by_category(ToolCategory.AWS)

    # Use with AIConnector
    from vendor_connectors.ai import AIConnector

    ai = AIConnector(provider="anthropic", tools=all_tools)
    response = ai.invoke_with_tools("List all GitHub repos in jbcom org")
"""

from __future__ import annotations

__all__ = [
    # Will export:
    # "get_all_tools",
    # "get_tools_by_category",
    # "register_tool",
    # "ConnectorToolDefinition",
]

# Placeholder - actual imports will be added after PR #16 merges
# from vendor_connectors.ai.tools.base import ConnectorToolDefinition, register_tool
# from vendor_connectors.ai.tools.registry import get_all_tools, get_tools_by_category
