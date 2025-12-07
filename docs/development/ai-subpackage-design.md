# AI Sub-Package Design Document

## Overview

This document outlines the design for the `vendor_connectors.ai` sub-package, which provides a unified AI interface leveraging LangChain/LangGraph for multi-provider AI access and tool abstraction.

**Status**: Pre-implementation design (blocked by PR #16)
**Epic**: jbcom/jbcom-control-center#340
**Blocks**: PR #18 (Meshy), jbcom/jbcom-control-center#342 (agentic-crew)

## Design Goals

1. **Unified AI Interface**: Single API for multiple AI providers (Anthropic, OpenAI, Google, xAI, Ollama)
2. **Tool Abstraction**: Auto-generate LangChain tools from existing vendor connectors
3. **Framework Agnostic**: Support CrewAI, MCP, and LangGraph workflows
4. **Observability**: Optional LangSmith tracing integration
5. **Backwards Compatibility**: Existing connectors remain unchanged

## Architecture

### Module Structure

```
vendor_connectors/
└── ai/                              # NEW: AI sub-package
    ├── __init__.py                  # Public API exports
    ├── base.py                      # Abstract AI interface and types
    ├── connector.py                 # AIConnector - main unified interface
    │
    ├── providers/                   # LangChain-based AI providers
    │   ├── __init__.py              # Provider registry
    │   ├── base.py                  # BaseLLMProvider abstract class
    │   ├── anthropic.py             # Claude via langchain-anthropic
    │   ├── openai.py                # GPT via langchain-openai
    │   ├── google.py                # Gemini via langchain-google-genai
    │   ├── xai.py                   # Grok via langchain-xai
    │   └── ollama.py                # Local models via langchain-ollama
    │
    ├── tools/                       # Vendor connectors as AI tools
    │   ├── __init__.py              # Tool registry and discovery
    │   ├── base.py                  # ConnectorTool base class
    │   ├── factory.py               # Auto-generation of tools from connectors
    │   ├── aws_tools.py             # AWS operations as tools
    │   ├── github_tools.py          # GitHub operations as tools
    │   ├── slack_tools.py           # Slack operations as tools
    │   ├── vault_tools.py           # Vault operations as tools
    │   ├── google_tools.py          # Google Cloud operations as tools
    │   └── zoom_tools.py            # Zoom operations as tools
    │
    └── workflows/                   # LangGraph workflow support
        ├── __init__.py
        ├── builder.py               # Workflow builder DSL
        └── nodes.py                 # Pre-built workflow nodes
```

### Key Design Patterns

Following the existing `meshy.agent_tools` pattern:

1. **Tool Definition** (framework-agnostic)
2. **Provider Interface** (adapts to specific frameworks)
3. **Registry Pattern** (lazy loading, thread-safe)

## Core Components

### 1. Base Types (`ai/base.py`)

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
from abc import ABC, abstractmethod


class AIProvider(str, Enum):
    """Supported AI providers."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    XAI = "xai"
    OLLAMA = "ollama"


class ToolCategory(str, Enum):
    """Categories for vendor connector tools."""
    AWS = "aws"
    GITHUB = "github"
    SLACK = "slack"
    VAULT = "vault"
    GOOGLE_CLOUD = "google_cloud"
    ZOOM = "zoom"
    MESHY = "meshy"


@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    description: str
    type: type
    required: bool = True
    default: Any = None
    enum_values: Optional[list[str]] = None


@dataclass
class ToolDefinition:
    """Framework-agnostic tool definition."""
    name: str
    description: str
    category: ToolCategory
    parameters: dict[str, ToolParameter]
    handler: Callable[..., Any]
    connector_class: Optional[type] = None  # Reference to connector class
    method_name: Optional[str] = None  # Method this tool wraps


@dataclass
class AIMessage:
    """Unified message format."""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[list[dict]] = None
    tool_results: Optional[list[dict]] = None


@dataclass
class AIResponse:
    """Response from AI provider."""
    content: str
    model: str
    provider: AIProvider
    usage: dict[str, int] = field(default_factory=dict)
    tool_calls: Optional[list[dict]] = None
    raw_response: Optional[Any] = None
```

### 2. AI Connector (`ai/connector.py`)

```python
from typing import Optional, Any
from vendor_connectors.ai.base import AIProvider, AIResponse, AIMessage
from vendor_connectors.ai.providers import get_provider


class AIConnector:
    """Unified AI connector supporting multiple providers.
    
    Usage:
        ai = AIConnector(provider="anthropic")
        response = ai.chat("Explain this code")
        
        # With tools
        from vendor_connectors.ai.tools import get_all_tools
        ai = AIConnector(provider="openai", tools=get_all_tools())
        response = ai.chat("Create a GitHub issue for this bug")
    """
    
    def __init__(
        self,
        provider: str | AIProvider = AIProvider.ANTHROPIC,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        tools: Optional[list] = None,
        langsmith_api_key: Optional[str] = None,
        **provider_kwargs,
    ):
        self.provider_name = AIProvider(provider)
        self._llm_provider = get_provider(
            self.provider_name,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **provider_kwargs,
        )
        self.tools = tools or []
        self._setup_langsmith(langsmith_api_key)
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list[AIMessage]] = None,
    ) -> AIResponse:
        """Send a chat message and get a response."""
        return self._llm_provider.chat(
            message=message,
            system_prompt=system_prompt,
            history=history,
            tools=self.tools,
        )
    
    def invoke_with_tools(
        self,
        message: str,
        max_iterations: int = 10,
    ) -> AIResponse:
        """Chat with automatic tool execution (agentic mode)."""
        return self._llm_provider.invoke_with_tools(
            message=message,
            tools=self.tools,
            max_iterations=max_iterations,
        )
    
    def _setup_langsmith(self, api_key: Optional[str]) -> None:
        """Configure LangSmith tracing if API key provided."""
        if api_key:
            import os
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = api_key
```

### 3. Provider Base (`ai/providers/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Any, Optional
from vendor_connectors.ai.base import AIResponse, AIMessage


class BaseLLMProvider(ABC):
    """Abstract base for LLM providers."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ):
        self.model = model or self.default_model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._llm = self._create_llm(**kwargs)
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier."""
        ...
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Default model for this provider."""
        ...
    
    @abstractmethod
    def _create_llm(self, **kwargs) -> Any:
        """Create the LangChain LLM instance."""
        ...
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list[AIMessage]] = None,
        tools: Optional[list] = None,
    ) -> AIResponse:
        """Execute a chat completion."""
        from langchain_core.messages import HumanMessage, SystemMessage
        
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        if history:
            messages.extend(self._convert_history(history))
        messages.append(HumanMessage(content=message))
        
        llm = self._llm
        if tools:
            llm = llm.bind_tools(tools)
        
        response = llm.invoke(messages)
        return self._convert_response(response)
    
    def invoke_with_tools(
        self,
        message: str,
        tools: list,
        max_iterations: int = 10,
    ) -> AIResponse:
        """Execute chat with tool calling loop."""
        from langgraph.prebuilt import create_react_agent
        
        agent = create_react_agent(self._llm, tools)
        result = agent.invoke({"messages": [("user", message)]})
        
        return self._convert_agent_response(result)
```

### 4. Tool Factory (`ai/tools/factory.py`)

Auto-generate LangChain tools from connector methods:

```python
import inspect
from typing import Any, Callable, Type
from langchain_core.tools import tool, StructuredTool
from pydantic import BaseModel, Field, create_model
from vendor_connectors.ai.tools.base import ConnectorToolDefinition


def create_tool_from_method(
    connector_class: Type,
    method_name: str,
    description: Optional[str] = None,
    include_params: Optional[list[str]] = None,
    exclude_params: Optional[list[str]] = None,
) -> StructuredTool:
    """Create a LangChain tool from a connector method.
    
    Args:
        connector_class: The connector class (e.g., GithubConnector)
        method_name: Name of the method to wrap
        description: Override description (default: method docstring)
        include_params: Only include these parameters
        exclude_params: Exclude these parameters
    
    Returns:
        LangChain StructuredTool
    """
    method = getattr(connector_class, method_name)
    sig = inspect.signature(method)
    docstring = inspect.getdoc(method) or ""
    
    # Build Pydantic model from signature
    fields = {}
    for param_name, param in sig.parameters.items():
        if param_name in ("self", "cls"):
            continue
        if include_params and param_name not in include_params:
            continue
        if exclude_params and param_name in exclude_params:
            continue
        
        # Determine type and default
        annotation = param.annotation if param.annotation != inspect.Parameter.empty else str
        default = ... if param.default == inspect.Parameter.empty else param.default
        
        # Extract param description from docstring
        param_desc = _extract_param_description(docstring, param_name)
        
        fields[param_name] = (annotation, Field(default=default, description=param_desc))
    
    # Create dynamic Pydantic model
    InputModel = create_model(
        f"{connector_class.__name__}_{method_name}_Input",
        **fields,
    )
    
    # Create tool function that instantiates connector and calls method
    def tool_func(**kwargs) -> str:
        connector = connector_class()  # Uses environment defaults
        result = getattr(connector, method_name)(**kwargs)
        return _serialize_result(result)
    
    return StructuredTool.from_function(
        func=tool_func,
        name=f"{connector_class.__name__.lower()}_{method_name}",
        description=description or _extract_method_description(docstring),
        args_schema=InputModel,
    )


def discover_connector_tools(
    connector_class: Type,
    include_methods: Optional[list[str]] = None,
    exclude_methods: Optional[list[str]] = None,
) -> list[StructuredTool]:
    """Auto-discover all public methods and create tools.
    
    Args:
        connector_class: Connector class to scan
        include_methods: Only include these methods
        exclude_methods: Exclude these methods (default: dunder, private)
    
    Returns:
        List of LangChain tools
    """
    tools = []
    exclude_methods = exclude_methods or []
    exclude_methods.extend(["__init__", "__repr__", "__str__"])
    
    for name, method in inspect.getmembers(connector_class, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        if name in exclude_methods:
            continue
        if include_methods and name not in include_methods:
            continue
        
        try:
            tool = create_tool_from_method(connector_class, name)
            tools.append(tool)
        except Exception as e:
            # Log but don't fail on individual methods
            pass
    
    return tools
```

### 5. Connector-Specific Tools

Example: `ai/tools/github_tools.py`

```python
from vendor_connectors.github import GithubConnector
from vendor_connectors.ai.tools.factory import create_tool_from_method, discover_connector_tools
from vendor_connectors.ai.tools.base import register_tool, ToolCategory


# Curated list of methods to expose as tools
GITHUB_TOOL_METHODS = [
    "list_repositories",
    "get_repository",
    "list_org_members",
    "get_org_member",
    "list_teams",
    "get_team",
    "get_repository_file",
    "update_repository_file",
    "create_repository_branch",
]


def get_github_tools():
    """Get all GitHub connector tools.
    
    Returns:
        List of LangChain tools for GitHub operations
    """
    tools = []
    
    for method_name in GITHUB_TOOL_METHODS:
        tool = create_tool_from_method(
            GithubConnector,
            method_name,
            exclude_params=["logger", "inputs"],  # Internal params
        )
        register_tool(tool, category=ToolCategory.GITHUB)
        tools.append(tool)
    
    return tools


# Pre-register on import
_github_tools = None

def get_tools():
    """Get GitHub tools (singleton pattern)."""
    global _github_tools
    if _github_tools is None:
        _github_tools = get_github_tools()
    return _github_tools
```

### 6. Tool Registry (`ai/tools/__init__.py`)

```python
from typing import Optional
from vendor_connectors.ai.base import ToolCategory


_tool_registry: dict[str, list] = {}


def register_tool(tool, category: ToolCategory) -> None:
    """Register a tool under a category."""
    if category.value not in _tool_registry:
        _tool_registry[category.value] = []
    _tool_registry[category.value].append(tool)


def get_tools_by_category(category: ToolCategory) -> list:
    """Get all tools in a category."""
    return _tool_registry.get(category.value, [])


def get_all_tools(
    categories: Optional[list[ToolCategory]] = None,
    include_meshy: bool = False,
) -> list:
    """Get all registered tools, optionally filtered by category.
    
    Args:
        categories: Filter to specific categories (default: all)
        include_meshy: Include Meshy tools (requires separate import)
    
    Returns:
        List of LangChain tools
    """
    # Lazy load all tool modules
    from vendor_connectors.ai.tools import (
        aws_tools,
        github_tools,
        slack_tools,
        vault_tools,
        google_tools,
        zoom_tools,
    )
    
    tools = []
    target_categories = [c.value for c in categories] if categories else list(_tool_registry.keys())
    
    for cat in target_categories:
        tools.extend(_tool_registry.get(cat, []))
    
    if include_meshy:
        from vendor_connectors.meshy.agent_tools import get_tool_definitions
        # Convert meshy tools to LangChain format
        tools.extend(_convert_meshy_tools(get_tool_definitions()))
    
    return tools
```

## Dependencies

### pyproject.toml additions

```toml
[project.optional-dependencies]
# AI sub-package - LangChain providers
ai = [
    "langchain>=0.3.0",
    "langchain-core>=0.3.0",
    "langgraph>=0.2.0",
]

# Individual AI provider extras
ai-anthropic = [
    "vendor-connectors[ai]",
    "langchain-anthropic>=0.3.0",
]

ai-openai = [
    "vendor-connectors[ai]",
    "langchain-openai>=0.3.0",
]

ai-google = [
    "vendor-connectors[ai]",
    "langchain-google-genai>=2.0.0",
]

ai-xai = [
    "vendor-connectors[ai]",
    "langchain-xai>=0.2.0",
]

ai-ollama = [
    "vendor-connectors[ai]",
    "langchain-ollama>=0.2.0",
]

# All AI providers
ai-all = [
    "vendor-connectors[ai-anthropic]",
    "vendor-connectors[ai-openai]",
    "vendor-connectors[ai-google]",
    "vendor-connectors[ai-xai]",
    "vendor-connectors[ai-ollama]",
]

# AI observability
ai-observability = [
    "langsmith>=0.2.0",
]

# Full AI installation
ai-full = [
    "vendor-connectors[ai-all]",
    "vendor-connectors[ai-observability]",
]
```

## Usage Examples

### Basic Chat

```python
from vendor_connectors.ai import AIConnector

ai = AIConnector(provider="anthropic")
response = ai.chat("Explain quantum computing in simple terms")
print(response.content)
```

### Chat with Tools

```python
from vendor_connectors.ai import AIConnector
from vendor_connectors.ai.tools import get_all_tools

ai = AIConnector(
    provider="openai",
    model="gpt-4o",
    tools=get_all_tools(include_meshy=True),
)

# AI can now call GitHub, Slack, AWS, etc. as needed
response = ai.invoke_with_tools(
    "Check the CI status for the vendor-connectors repo and post a summary to #dev-updates"
)
```

### LangGraph Workflow

```python
from vendor_connectors.ai.workflows import WorkflowBuilder

workflow = (
    WorkflowBuilder()
    .add_step("analyze", "Review this PR for security issues: {pr_url}")
    .add_step("report", "Summarize findings as a Slack message")
    .add_conditional(
        "is_critical",
        true_step="create_issue",
        false_step="done",
    )
    .add_step("create_issue", "Create a GitHub issue for critical findings")
    .build()
)

result = workflow.invoke({"pr_url": "https://github.com/org/repo/pull/123"})
```

### Specific Provider

```python
from vendor_connectors.ai.providers.ollama import OllamaProvider

# Use local Ollama model
provider = OllamaProvider(model="llama2")
response = provider.chat("Explain this error message: ...")
```

## Migration Strategy

### Phase 1: Foundation (Current)
- Design document (this file)
- Module structure stubs
- Dependency specifications

### Phase 2: Core Implementation (After PR #16 merges)
- `ai/base.py` - Types and interfaces
- `ai/connector.py` - Main connector class
- `ai/providers/base.py` - Provider base class
- `ai/providers/anthropic.py` - First provider (wraps existing)

### Phase 3: Tool Abstraction
- `ai/tools/base.py` - Tool definitions
- `ai/tools/factory.py` - Auto-generation
- Tool modules for each connector

### Phase 4: Additional Providers
- OpenAI, Google, xAI, Ollama providers
- Provider registry and lazy loading

### Phase 5: Workflows
- LangGraph integration
- Workflow builder DSL
- Pre-built workflow templates

## Testing Strategy

Following existing patterns from `tests/`:

```python
# tests/ai/test_connector.py
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_llm():
    """Mock LangChain LLM."""
    llm = MagicMock()
    llm.invoke.return_value = MagicMock(content="Test response")
    return llm


class TestAIConnector:
    def test_init_default_provider(self, mock_llm):
        with patch("vendor_connectors.ai.providers.anthropic.ChatAnthropic", return_value=mock_llm):
            from vendor_connectors.ai import AIConnector
            ai = AIConnector()
            assert ai.provider_name.value == "anthropic"
    
    def test_chat_basic(self, mock_llm):
        with patch("vendor_connectors.ai.providers.anthropic.ChatAnthropic", return_value=mock_llm):
            from vendor_connectors.ai import AIConnector
            ai = AIConnector()
            response = ai.chat("Hello")
            assert response.content == "Test response"
```

## Related Documentation

- [LangChain Custom Tools](https://python.langchain.com/docs/how_to/custom_tools/)
- [LangGraph Quickstart](https://langchain-ai.github.io/langgraph/)
- [LangSmith Tracing](https://docs.smith.langchain.com/)

## Changelog

- 2025-12-07: Initial design document created
