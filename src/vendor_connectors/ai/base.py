"""Base types and interfaces for AI sub-package.

This module defines the core types used across the AI sub-package:
- AIProvider enum - Supported AI providers
- ToolCategory enum - Categories for vendor connector tools
- ToolParameter/ToolDefinition - Framework-agnostic tool definitions
- AIMessage/AIResponse - Unified message formats
- ToolResult - Structured result from tool execution
- ToolRegistry - Thread-safe tool registry
"""

from __future__ import annotations

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    "AIProvider",
    "ToolCategory",
    "ToolParameter",
    "ToolDefinition",
    "AIMessage",
    "AIResponse",
    "AIRole",
    "ToolResult",
    "BaseToolProvider",
    "ToolRegistry",
    "register_tool",
    "get_tool_definitions",
    "get_tool_definition",
]


class AIProvider(str, Enum):
    """Supported AI providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    XAI = "xai"
    OLLAMA = "ollama"


class AIRole(str, Enum):
    """Message roles in conversations."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ToolCategory(str, Enum):
    """Categories for vendor connector tools."""

    # Vendor connectors
    AWS = "aws"
    GITHUB = "github"
    SLACK = "slack"
    VAULT = "vault"
    GOOGLE_CLOUD = "google_cloud"
    ZOOM = "zoom"
    MESHY = "meshy"
    CURSOR = "cursor"
    ANTHROPIC = "anthropic"

    # Meshy-specific subcategories (for internal use)
    GENERATION = "generation"  # Create new 3D assets
    RIGGING = "rigging"  # Add skeletons/rigs
    ANIMATION = "animation"  # Apply/manage animations
    TEXTURING = "texturing"  # Texture/retexture models
    UTILITY = "utility"  # Status checks, listings, etc.


@dataclass
class ToolParameter:
    """Definition of a tool parameter.

    Attributes:
        name: Parameter name.
        description: Human-readable description for AI agents.
        type: Python type (str, int, bool, etc.).
        required: Whether the parameter is required.
        default: Default value if not required.
        enum_values: Optional list of allowed values.
    """

    name: str
    description: str
    type: type = str
    required: bool = True
    default: Any = None
    enum_values: list[str] | None = None

    def to_json_schema(self) -> dict[str, Any]:
        """Convert to JSON Schema format for LangChain tools."""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
        }

        schema: dict[str, Any] = {
            "type": type_map.get(self.type, "string"),
            "description": self.description,
        }

        if self.default is not None:
            schema["default"] = self.default

        if self.enum_values:
            schema["enum"] = self.enum_values

        return schema


# Backwards compatibility alias
ParameterDefinition = ToolParameter


@dataclass
class ToolDefinition:
    """Framework-agnostic tool definition.

    This is converted to LangChain StructuredTool or other framework-specific
    tool formats by the respective providers.

    Attributes:
        name: Unique tool identifier (snake_case).
        description: Human-readable description for AI agents.
        category: Tool category for organization.
        parameters: Dict of parameter name -> ToolParameter.
        handler: The actual function that implements the tool.
        requires_api_key: Whether an API key is required (e.g., MESHY_API_KEY).
        connector_class: Optional reference to the connector class.
        method_name: Optional method name this tool wraps.
    """

    name: str
    description: str
    category: ToolCategory
    parameters: dict[str, ToolParameter]
    handler: Callable[..., Any]
    requires_api_key: bool = True
    connector_class: type | None = None
    method_name: str | None = None

    def get_required_params(self) -> list[str]:
        """Get list of required parameter names."""
        return [name for name, param in self.parameters.items() if param.required]

    def to_json_schema(self) -> dict[str, Any]:
        """Convert parameters to JSON Schema format."""
        properties = {}
        required = []

        for name, param in self.parameters.items():
            properties[name] = param.to_json_schema()
            if param.required:
                required.append(name)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
        }


@dataclass
class ToolResult:
    """Result from executing a tool.

    Attributes:
        success: Whether the tool executed successfully
        data: The result data (JSON-serializable)
        error: Error message if success is False
        task_id: Meshy task ID if applicable
    """

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    task_id: str | None = None

    def to_json(self) -> str:
        """Serialize to JSON string."""
        import json

        return json.dumps(
            {
                "success": self.success,
                "data": self.data,
                "error": self.error,
                "task_id": self.task_id,
            },
            indent=2,
        )


@dataclass
class AIMessage:
    """Unified message format for AI conversations.

    Attributes:
        role: Message role (user, assistant, system, tool).
        content: Message text content.
        name: Optional name for tool messages.
        tool_call_id: Optional ID for tool result messages.
        tool_calls: Optional list of tool calls from assistant.
    """

    role: AIRole
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result: dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            result["name"] = self.name
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        return result

    @classmethod
    def user(cls, content: str) -> AIMessage:
        """Create a user message."""
        return cls(role=AIRole.USER, content=content)

    @classmethod
    def assistant(cls, content: str, tool_calls: list[dict] | None = None) -> AIMessage:
        """Create an assistant message."""
        return cls(role=AIRole.ASSISTANT, content=content, tool_calls=tool_calls)

    @classmethod
    def system(cls, content: str) -> AIMessage:
        """Create a system message."""
        return cls(role=AIRole.SYSTEM, content=content)

    @classmethod
    def tool_result(cls, content: str, tool_call_id: str, name: str) -> AIMessage:
        """Create a tool result message."""
        return cls(role=AIRole.TOOL, content=content, tool_call_id=tool_call_id, name=name)


@dataclass
class AIResponse:
    """Response from an AI provider.

    Attributes:
        content: The text content of the response.
        model: Model identifier used.
        provider: AI provider that generated the response.
        usage: Token usage statistics.
        tool_calls: Optional list of tool calls requested by the model.
        stop_reason: Reason the model stopped generating.
        raw_response: Original response object from the provider.
    """

    content: str
    model: str
    provider: AIProvider
    usage: dict[str, int] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] | None = None
    stop_reason: str | None = None
    raw_response: Any | None = None

    @property
    def has_tool_calls(self) -> bool:
        """Check if response contains tool calls."""
        return bool(self.tool_calls)

    @property
    def input_tokens(self) -> int:
        """Get input token count."""
        return self.usage.get("input_tokens", 0)

    @property
    def output_tokens(self) -> int:
        """Get output token count."""
        return self.usage.get("output_tokens", 0)

    @property
    def total_tokens(self) -> int:
        """Get total token count."""
        return self.input_tokens + self.output_tokens


class BaseToolProvider(ABC):
    """Abstract base class for tool providers.

    Each agent framework (CrewAI, MCP, etc.) implements this interface
    to provide framework-specific tool wrappers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'crewai', 'mcp')."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Provider version."""
        ...

    @abstractmethod
    def get_tools(self) -> list[Any]:
        """Get all tools in the framework's native format.

        Returns:
            List of framework-specific tool objects
        """
        ...

    @abstractmethod
    def get_tool(self, name: str) -> Any | None:
        """Get a specific tool by name.

        Args:
            name: Tool name

        Returns:
            Framework-specific tool object, or None if not found
        """
        ...

    def list_tools(self) -> list[str]:
        """List available tool names.

        Returns:
            List of tool names
        """
        return [t.name if hasattr(t, "name") else str(t) for t in self.get_tools()]


class ToolRegistry:
    """Thread-safe registry for tool definitions.

    Addresses thread safety concerns with global mutable state.
    """

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}
        self._lock = threading.RLock()

    def register(self, definition: ToolDefinition) -> None:
        """Register a tool definition."""
        with self._lock:
            self._tools[definition.name] = definition

    def get_all(self) -> list[ToolDefinition]:
        """Get all registered tool definitions."""
        with self._lock:
            return list(self._tools.values())

    def get(self, name: str) -> ToolDefinition | None:
        """Get a specific tool definition by name."""
        with self._lock:
            return self._tools.get(name)


# Global registry instance
_registry = ToolRegistry()


def register_tool(definition: ToolDefinition) -> None:
    """Register a tool definition."""
    _registry.register(definition)


def get_tool_definitions() -> list[ToolDefinition]:
    """Get all registered tool definitions."""
    return _registry.get_all()


def get_tool_definition(name: str) -> ToolDefinition | None:
    """Get a specific tool definition by name."""
    return _registry.get(name)
