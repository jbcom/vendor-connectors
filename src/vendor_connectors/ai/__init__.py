"""AI Tools Sub-Package for vendor-connectors.

This package provides AI framework integrations for vendor connectors,
enabling them to be used as tools in LangChain, CrewAI, MCP, and other
AI agent frameworks.

Originated from meshy/agent_tools, now generalized for all connectors.
Compatible with PR #20's AI sub-package design.

Example:
    from vendor_connectors.ai.base import ToolParameter, ToolDefinition, ToolCategory
    from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

    tools = get_meshy_tools()
    for tool in tools:
        print(f"{tool.name}: {tool.description}")
"""

from vendor_connectors.ai.base import (
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolResult,
)

__all__ = [
    "ToolCategory",
    "ToolDefinition",
    "ToolParameter",
    "ToolResult",
]
