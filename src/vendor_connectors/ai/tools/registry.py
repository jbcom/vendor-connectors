"""Tool registry for managing available AI tools.

This module provides a central registry for all tools generated from
vendor connectors, allowing easy discovery and filtering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from vendor_connectors.ai.base import ToolCategory, ToolDefinition

if TYPE_CHECKING:
    pass

__all__ = ["ToolRegistry"]


class ToolRegistry:
    """Central registry for AI tools.

    Tools are registered by name and can be filtered by category.
    The registry also stores connector instances to enable proper method binding
    when tools are invoked from workflow nodes.

    Example:
        >>> registry = ToolRegistry()
        >>> registry.register(my_tool_definition)
        >>> tools = registry.get_tools(categories=[ToolCategory.AWS])
    """

    _instance: ToolRegistry | None = None

    def __init__(self):
        """Initialize empty registry."""
        self._tools: dict[str, ToolDefinition] = {}
        self._categories: dict[ToolCategory, set[str]] = {}
        self._connector_instances: dict[ToolCategory, object] = {}

    @classmethod
    def get_instance(cls) -> ToolRegistry:
        """Get the singleton registry instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool definition.

        Args:
            tool: The tool definition to register.

        Raises:
            ValueError: If a tool with the same name already exists.
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool

        if tool.category not in self._categories:
            self._categories[tool.category] = set()
        self._categories[tool.category].add(tool.name)

    def unregister(self, name: str) -> None:
        """Unregister a tool by name.

        Args:
            name: The tool name to remove.
        """
        if name in self._tools:
            tool = self._tools.pop(name)
            if tool.category in self._categories:
                self._categories[tool.category].discard(name)

    def get(self, name: str) -> ToolDefinition | None:
        """Get a tool by name.

        Args:
            name: The tool name.

        Returns:
            ToolDefinition or None if not found.
        """
        return self._tools.get(name)

    def get_tools(
        self,
        categories: list[ToolCategory | None] = None,
        names: list[str | None] = None,
    ) -> list[ToolDefinition]:
        """Get tools, optionally filtered.

        Args:
            categories: Filter by categories (returns tools in any category).
            names: Filter by specific tool names.

        Returns:
            List of matching tool definitions.
        """
        tools = list(self._tools.values())

        if categories:
            category_names: set[str] = set()
            for cat in categories:
                if cat in self._categories:
                    category_names.update(self._categories[cat])
            tools = [t for t in tools if t.name in category_names]

        if names:
            name_set = set(names)
            tools = [t for t in tools if t.name in name_set]

        return tools

    def list_names(self, category: ToolCategory | None = None) -> list[str]:
        """List all registered tool names.

        Args:
            category: Optional category filter.

        Returns:
            List of tool names.
        """
        if category:
            return list(self._categories.get(category, set()))
        return list(self._tools.keys())

    def list_categories(self) -> list[ToolCategory]:
        """List all categories with registered tools.

        Returns:
            List of categories.
        """
        return list(self._categories.keys())

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()
        self._categories.clear()

    def register_instance(self, category: ToolCategory, instance: object) -> None:
        """Register a connector instance for method binding.

        Args:
            category: The tool category.
            instance: The connector instance.
        """
        self._connector_instances[category] = instance

    def get_connector_instance(self, category: ToolCategory) -> object | None:
        """Get a connector instance by category.

        Args:
            category: The tool category.

        Returns:
            Connector instance or None if not registered.
        """
        return self._connector_instances.get(category)

    def __len__(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools
