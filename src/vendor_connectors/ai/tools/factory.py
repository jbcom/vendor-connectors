"""Tool factory for auto-generating LangChain tools from connector methods.

This module provides utilities to:
- Inspect connector class methods
- Generate Pydantic input models from method signatures
- Create LangChain StructuredTool instances

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Key functions (after implementation):

    def create_tool_from_method(
        connector_class: Type,
        method_name: str,
        description: Optional[str] = None,
        include_params: Optional[list[str]] = None,
        exclude_params: Optional[list[str]] = None,
    ) -> StructuredTool:
        '''Create a LangChain tool from a connector method.'''
        ...

    def discover_connector_tools(
        connector_class: Type,
        include_methods: Optional[list[str]] = None,
        exclude_methods: Optional[list[str]] = None,
    ) -> list[StructuredTool]:
        '''Auto-discover all public methods and create tools.'''
        ...
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
