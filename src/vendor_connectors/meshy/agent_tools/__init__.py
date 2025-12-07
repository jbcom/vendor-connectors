"""Agent tools for mesh-toolkit - MOVED to vendor_connectors.ai

This module now provides backwards compatibility by re-exporting from
the new vendor_connectors.ai package.

DEPRECATION NOTICE:
The agent_tools subpackage has been refactored and moved to vendor_connectors.ai.
This compatibility layer will be removed in a future version.

Old import:
    from vendor_connectors.meshy.agent_tools import get_provider

New import:
    from vendor_connectors.ai.providers import crewai, mcp

Architecture now:
    vendor_connectors/
    └── ai/                      # NEW top-level AI package
        ├── base.py              # ToolParameter, ToolDefinition, ToolCategory
        ├── tools/
        │   └── meshy_tools.py   # Meshy-specific tools
        └── providers/
            ├── crewai/          # CrewAI integration
            └── mcp/             # MCP server

Usage:
    # For Meshy tools
    from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools
    tools = get_meshy_tools()

    # For CrewAI integration
    from vendor_connectors.ai.providers.crewai import get_tools
    crewai_tools = get_tools()

    # For MCP server
    from vendor_connectors.ai.providers.mcp import create_server
    server = create_server()
"""

from __future__ import annotations

# Re-export from new location for backwards compatibility
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

# Conditional deprecation warning to avoid breaking applications
# that treat warnings as errors. Enable with environment variable.
import os
import warnings

if os.getenv("VENDOR_CONNECTORS_SHOW_DEPRECATION_WARNINGS", "false").lower() in (
    "true",
    "1",
    "yes",
):
    warnings.warn(
        "vendor_connectors.meshy.agent_tools is deprecated. "
        "Use vendor_connectors.ai instead. "
        "This compatibility layer will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2,
    )
