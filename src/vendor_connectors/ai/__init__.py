"""AI Sub-Package for vendor-connectors.

This package provides a unified interface for AI provider interactions
with automatic tool generation from vendor connectors.

Features:
- Multi-provider support (Anthropic, OpenAI, Google, xAI, Ollama)
- Auto-generated tools from connector methods
- LangGraph workflow support
- Optional LangSmith tracing

Example:
    >>> from vendor_connectors.ai import AIConnector, AIProvider, ToolCategory
    >>>
    >>> # Create connector with Anthropic
    >>> connector = AIConnector(provider="anthropic", api_key="...")
    >>>
    >>> # Simple chat
    >>> response = connector.chat("Hello!")
    >>> print(response.content)
    >>>
    >>> # With tools from a GitHub connector
    >>> from vendor_connectors.github import GitHubConnector
    >>> gh = GitHubConnector(token="...")
    >>> connector.register_connector_tools(gh, ToolCategory.GITHUB)
    >>>
    >>> # Invoke with tool use
    >>> response = connector.invoke("List my repositories")
    >>> print(response.content)

Installation:
    # Core AI support
    pip install vendor-connectors[ai]

    # Specific provider
    pip install vendor-connectors[ai-anthropic]

    # All providers
    pip install vendor-connectors[ai-all]

    # With observability
    pip install vendor-connectors[ai-observability]
"""

from vendor_connectors.ai.base import (
    AIMessage,
    AIProvider,
    AIResponse,
    AIRole,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
)
from vendor_connectors.ai.connector import AIConnector
from vendor_connectors.ai.tools import ToolFactory, ToolRegistry

__all__ = [
    # Main connector
    "AIConnector",
    # Enums
    "AIProvider",
    "AIRole",
    "ToolCategory",
    # Types
    "AIMessage",
    "AIResponse",
    "ToolParameter",
    "ToolDefinition",
    # Tools
    "ToolFactory",
    "ToolRegistry",
]
