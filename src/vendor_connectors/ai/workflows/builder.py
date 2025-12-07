"""Workflow builder for LangGraph integration.

This module provides a DSL for building LangGraph workflows
with vendor connector tools.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional

if TYPE_CHECKING:
    pass

__all__ = ["WorkflowBuilder"]


class WorkflowBuilder:
    """Builder for LangGraph workflows.

    Provides a fluent interface for constructing workflows with
    vendor connector tools.

    Example:
        >>> builder = WorkflowBuilder()
        >>> workflow = (
        ...     builder
        ...     .add_node("fetch", fetch_data)
        ...     .add_node("process", process_data)
        ...     .add_edge("fetch", "process")
        ...     .set_entry("fetch")
        ...     .build()
        ... )
    """

    def __init__(self):
        """Initialize builder."""
        self._nodes: dict[str, Callable] = {}
        self._edges: list[tuple[str, str]] = []
        self._conditional_edges: list[tuple[str, Callable, dict]] = []
        self._entry_point: Optional[str] = None
        self._state_schema: Optional[type] = None

    def set_state_schema(self, schema: type) -> WorkflowBuilder:
        """Set the state schema for the workflow.

        Args:
            schema: TypedDict or Pydantic model for state.

        Returns:
            Self for chaining.
        """
        self._state_schema = schema
        return self

    def add_node(self, name: str, func: Callable) -> WorkflowBuilder:
        """Add a node to the workflow.

        Args:
            name: Node identifier.
            func: Function to execute at this node.

        Returns:
            Self for chaining.
        """
        self._nodes[name] = func
        return self

    def add_edge(self, from_node: str, to_node: str) -> WorkflowBuilder:
        """Add a direct edge between nodes.

        Args:
            from_node: Source node name.
            to_node: Target node name.

        Returns:
            Self for chaining.
        """
        self._edges.append((from_node, to_node))
        return self

    def add_conditional_edge(
        self,
        from_node: str,
        condition: Callable,
        path_map: dict[str, str],
    ) -> WorkflowBuilder:
        """Add a conditional edge.

        Args:
            from_node: Source node name.
            condition: Function that returns a key from path_map.
            path_map: Mapping from condition results to target nodes.

        Returns:
            Self for chaining.
        """
        self._conditional_edges.append((from_node, condition, path_map))
        return self

    def set_entry(self, node: str) -> WorkflowBuilder:
        """Set the entry point node.

        Args:
            node: Entry node name.

        Returns:
            Self for chaining.
        """
        self._entry_point = node
        return self

    def build(self) -> Any:
        """Build and compile the LangGraph workflow.

        Returns:
            Compiled LangGraph StateGraph.

        Raises:
            ImportError: If LangGraph is not installed.
            ValueError: If workflow is incomplete.
        """
        try:
            from langgraph.graph import END, StateGraph
        except ImportError as e:
            raise ImportError(
                "LangGraph is required for workflows. Install with: pip install vendor-connectors[ai]"
            ) from e

        if not self._entry_point:
            raise ValueError("Entry point must be set with set_entry()")

        if not self._state_schema:
            # Use a simple dict state if no schema provided
            from typing import TypedDict

            class State(TypedDict):
                messages: list
                data: dict

            self._state_schema = State

        graph = StateGraph(self._state_schema)

        # Add all nodes
        for name, func in self._nodes.items():
            graph.add_node(name, func)

        # Add direct edges
        for from_node, to_node in self._edges:
            if to_node == "END":
                graph.add_edge(from_node, END)
            else:
                graph.add_edge(from_node, to_node)

        # Add conditional edges
        for from_node, condition, path_map in self._conditional_edges:
            # Replace "END" string with actual END
            resolved_map = {k: END if v == "END" else v for k, v in path_map.items()}
            graph.add_conditional_edges(from_node, condition, resolved_map)

        # Set entry point
        graph.set_entry_point(self._entry_point)

        return graph.compile()
