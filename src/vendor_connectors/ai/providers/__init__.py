"""AI Framework Providers for vendor connector tools.

This package contains integrations with various AI agent frameworks:
- crewai: CrewAI tool provider  
- mcp: Model Context Protocol server

These providers convert tool definitions into framework-specific formats.

Example:
    from vendor_connectors.ai.providers.crewai import get_tools
    
    tools = get_tools()  # Returns CrewAI BaseTool instances
"""

from __future__ import annotations

__all__ = ["crewai", "mcp"]
