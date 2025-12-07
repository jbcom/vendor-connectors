"""Pre-built workflow nodes.

This module provides common node implementations for LangGraph workflows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    pass

__all__ = ["ToolNode", "ConditionalNode", "create_tool_node"]


@dataclass
class ToolNode:
    """Node that executes a tool.

    Attributes:
        name: Node name.
        tool_name: Name of the tool to execute.
        input_key: State key to read input from.
        output_key: State key to write output to.
    """

    name: str
    tool_name: str
    input_key: str = "input"
    output_key: str = "output"

    def __call__(self, state: dict) -> dict:
        """Execute the tool node.

        Args:
            state: Current workflow state.

        Returns:
            Updated state with tool output.
        """
        from vendor_connectors.ai.tools.registry import ToolRegistry

        registry = ToolRegistry.get_instance()
        tool = registry.get(self.tool_name)

        if not tool:
            raise ValueError(f"Tool '{self.tool_name}' not found in registry")

        input_data = state.get(self.input_key, {})

        # Handle both dict and direct value inputs
        if isinstance(input_data, dict):
            result = tool.handler(**input_data)
        else:
            result = tool.handler(input_data)

        return {**state, self.output_key: result}


@dataclass
class ConditionalNode:
    """Node that routes based on a condition.

    Attributes:
        name: Node name.
        condition: Function that takes state and returns a route key.
        routes: Mapping from condition results to next node names.
    """

    name: str
    condition: Callable[[dict], str]
    routes: dict[str, str]

    def get_next(self, state: dict) -> str:
        """Determine next node based on state.

        Args:
            state: Current workflow state.

        Returns:
            Name of next node.
        """
        result = self.condition(state)
        return self.routes.get(result, self.routes.get("default", "END"))


def create_tool_node(
    tool_name: str,
    input_key: str = "input",
    output_key: str = "output",
) -> Callable[[dict], dict]:
    """Create a tool execution function for use in workflows.

    Args:
        tool_name: Name of the registered tool.
        input_key: State key to read input from.
        output_key: State key to write output to.

    Returns:
        Function suitable for use as a LangGraph node.
    """
    from vendor_connectors.ai.tools.registry import ToolRegistry

    def node_func(state: dict) -> dict:
        registry = ToolRegistry.get_instance()
        tool = registry.get(tool_name)

        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found in registry")

        input_data = state.get(input_key, {})

        if isinstance(input_data, dict):
            result = tool.handler(**input_data)
        else:
            result = tool.handler(input_data)

        return {**state, output_key: result}

    return node_func
