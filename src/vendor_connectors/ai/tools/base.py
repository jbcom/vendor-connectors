"""Base classes and types for connector tools.

This module defines:
- ConnectorToolDefinition - Extended tool definition with connector reference
- register_tool() - Register a tool in the global registry
- Tool result helpers

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    @dataclass
    class ConnectorToolDefinition:
        name: str
        description: str
        category: ToolCategory
        parameters: dict[str, ToolParameter]
        handler: Callable[..., Any]
        connector_class: type | None = None
        method_name: str | None = None

    _tool_registry: dict[str, list[StructuredTool]] = {}

    def register_tool(tool: StructuredTool, category: ToolCategory) -> None:
        if category.value not in _tool_registry:
            _tool_registry[category.value] = []
        _tool_registry[category.value].append(tool)
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
