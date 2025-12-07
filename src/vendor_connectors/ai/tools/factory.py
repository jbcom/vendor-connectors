"""Tool factory for auto-generating LangChain tools from connectors.

This module provides utilities to automatically create LangChain-compatible
tools from vendor connector methods.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Callable, Optional, get_type_hints

from vendor_connectors.ai.base import ToolCategory, ToolDefinition, ToolParameter

if TYPE_CHECKING:
    pass

__all__ = ["ToolFactory", "create_tool", "tool_from_method"]


def _python_type_to_json_type(py_type: type) -> str:
    """Convert Python type to JSON Schema type string."""
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }
    # Handle Optional, Union, etc.
    origin = getattr(py_type, "__origin__", None)
    if origin is not None:
        # For Optional[X], get the inner type
        args = getattr(py_type, "__args__", ())
        if args:
            return _python_type_to_json_type(args[0])
    return type_map.get(py_type, "string")


def tool_from_method(
    method: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
    category: ToolCategory = ToolCategory.AWS,
    connector_class: Optional[type] = None,
) -> ToolDefinition:
    """Create a ToolDefinition from a method.

    Inspects the method signature and docstring to auto-generate
    parameter definitions.

    Args:
        method: The method to wrap as a tool.
        name: Tool name (defaults to method name).
        description: Tool description (defaults to docstring).
        category: Tool category for organization.
        connector_class: Optional connector class reference.

    Returns:
        ToolDefinition for the method.
    """
    tool_name = name or method.__name__

    # Get description from docstring
    tool_desc = description
    if not tool_desc and method.__doc__:
        # Use first line/paragraph of docstring
        lines = method.__doc__.strip().split("\n\n")[0].split("\n")
        tool_desc = " ".join(line.strip() for line in lines)
    tool_desc = tool_desc or f"Execute {tool_name}"

    # Inspect signature for parameters
    sig = inspect.signature(method)
    hints = {}
    try:
        hints = get_type_hints(method)
    except Exception:
        pass

    parameters: dict[str, ToolParameter] = {}

    for param_name, param in sig.parameters.items():
        # Skip self, cls, and **kwargs
        if param_name in ("self", "cls") or param.kind == inspect.Parameter.VAR_KEYWORD:
            continue

        param_type = hints.get(param_name, str)
        # Handle Optional types
        if hasattr(param_type, "__origin__"):
            origin = getattr(param_type, "__origin__", None)
            # Check for Union (Optional is Union[X, None])
            if origin is type(None) or str(origin) == "typing.Union":
                args = getattr(param_type, "__args__", ())
                if args:
                    param_type = args[0]

        is_required = param.default == inspect.Parameter.empty

        parameters[param_name] = ToolParameter(
            name=param_name,
            description=f"Parameter: {param_name}",
            type=param_type if isinstance(param_type, type) else str,
            required=is_required,
            default=None if param.default == inspect.Parameter.empty else param.default,
        )

    return ToolDefinition(
        name=tool_name,
        description=tool_desc,
        category=category,
        parameters=parameters,
        handler=method,
        connector_class=connector_class,
        method_name=method.__name__,
    )


def create_tool(
    name: str,
    description: str,
    handler: Callable,
    category: ToolCategory,
    parameters: Optional[dict[str, ToolParameter]] = None,
) -> ToolDefinition:
    """Create a ToolDefinition manually.

    Args:
        name: Unique tool name.
        description: Human-readable description.
        handler: Function that implements the tool.
        category: Tool category.
        parameters: Optional parameter definitions.

    Returns:
        ToolDefinition.
    """
    return ToolDefinition(
        name=name,
        description=description,
        category=category,
        parameters=parameters or {},
        handler=handler,
    )


class ToolFactory:
    """Factory for auto-generating tools from connector classes.

    Scans connector classes and generates tool definitions for their
    public methods.

    Example:
        >>> factory = ToolFactory()
        >>> tools = factory.from_connector(AWSConnector, ToolCategory.AWS)
    """

    # Methods to skip when generating tools
    SKIP_METHODS = {
        "__init__",
        "__str__",
        "__repr__",
        "__enter__",
        "__exit__",
        "close",
        "connect",
        "disconnect",
    }

    def __init__(self):
        """Initialize factory."""
        self._generated: dict[str, ToolDefinition] = {}

    def from_connector(
        self,
        connector_class: type,
        category: ToolCategory,
        include_private: bool = False,
        method_filter: Optional[Callable[[str], bool]] = None,
    ) -> list[ToolDefinition]:
        """Generate tools from a connector class.

        Args:
            connector_class: The connector class to scan.
            category: Category for generated tools.
            include_private: Include methods starting with _.
            method_filter: Optional filter function for method names.

        Returns:
            List of generated ToolDefinitions.
        """
        tools = []

        for name, method in inspect.getmembers(connector_class, predicate=inspect.isfunction):
            # Skip private methods unless requested
            if not include_private and name.startswith("_"):
                continue

            # Skip common utility methods
            if name in self.SKIP_METHODS:
                continue

            # Apply custom filter
            if method_filter and not method_filter(name):
                continue

            tool = tool_from_method(
                method,
                name=f"{category.value}_{name}",
                category=category,
                connector_class=connector_class,
            )
            tools.append(tool)
            self._generated[tool.name] = tool

        return tools

    def to_langchain_tools(
        self,
        tools: list[ToolDefinition],
        connector_instance: Optional[Any] = None,
    ) -> list:
        """Convert ToolDefinitions to LangChain StructuredTools.

        Args:
            tools: List of tool definitions.
            connector_instance: Optional connector instance to bind methods to.

        Returns:
            List of LangChain StructuredTool instances.
        """
        try:
            from langchain_core.tools import StructuredTool
        except ImportError as e:
            raise ImportError(
                "LangChain is required for tool conversion. Install with: pip install vendor-connectors[ai]"
            ) from e

        lc_tools = []

        for tool in tools:
            handler = tool.handler

            # If we have a connector instance, bind the method
            if connector_instance and tool.method_name:
                bound_method = getattr(connector_instance, tool.method_name, None)
                if bound_method:
                    handler = bound_method

            lc_tool = StructuredTool.from_function(
                func=handler,
                name=tool.name,
                description=tool.description,
                args_schema=None,  # Let LangChain infer from function
            )
            lc_tools.append(lc_tool)

        return lc_tools
