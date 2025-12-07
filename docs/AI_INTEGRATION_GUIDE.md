# AI Package Integration Guide

## ✅ Refactoring Complete

Meshy tools now live directly under the unified top-level `ai/` package. The deprecated `agent_tools/` shim has been removed in favor of the consolidated AI tool stack.

## Current Structure

```
vendor_connectors/
├── ai/                          # NEW - Top-level AI package
│   ├── __init__.py             # Exports ToolParameter, ToolDefinition, ToolCategory, ToolResult
│   ├── base.py                 # Core types (compatible with PR #20)
│   ├── tools/
│   │   ├── __init__.py
│   │   └── meshy_tools.py      # Meshy 3D generation tools
│   └── providers/
│       ├── __init__.py
│       ├── crewai/             # CrewAI framework provider
│       └── mcp/                # MCP server provider
├── meshy/
│   ├── __init__.py
│   ├── connector.py            # MeshyConnector class
│   ├── text3d.py, rigging.py, etc.
│   └── (deprecated shim removed)
└── ... (aws, github, slack, etc.)
```

## What's in This PR

### ai/base.py
Core types that both PRs need:
- `ToolParameter` - Parameter definitions
- `ToolDefinition` - Framework-agnostic tool definition
- `ToolCategory` - Categories for all connectors (AWS, GitHub, Slack, Meshy, etc.)
- `ToolResult` - Structured result format
- `BaseToolProvider` - Abstract provider interface

### ai/tools/meshy_tools.py
Meshy-specific tool handlers:
- `text3d_generate` - Generate 3D from text
- `rig_model` - Add skeleton/rig
- `apply_animation` - Apply animation
- `retexture_model` - Change textures
- `list_animations` - List animation catalog
- `check_task_status` - Check task status
- `get_animation` - Get animation details

### ai/providers/crewai/
CrewAI framework integration:
- Converts ToolDefinitions to CrewAI BaseTool
- Provides `get_tools()` for use in CrewAI agents

### ai/providers/mcp/
Model Context Protocol server:
- MCP server implementation for Meshy tools
- Entry point: `meshy-mcp` command

## What PR #20 Provides

When PR #20 merges, it will add:

### ai/connector.py
```python
class AIConnector:
    """Unified interface for AI providers (Anthropic, OpenAI, etc.)"""
    def __init__(self, provider="anthropic", ...)
    def chat(self, message, ...)
    def invoke(self, message, use_tools=True, ...)
    def register_connector_tools(self, connector, category, ...)
```

### ai/providers/anthropic.py, openai.py, google.py, xai.py, ollama.py
LangChain-based AI provider implementations

### ai/tools/factory.py
```python
class ToolFactory:
    """Auto-generate tools from connector methods"""
    def from_connector(self, connector_class, category, ...)
    def to_langchain_tools(self, tools, ...)
```

### ai/tools/registry.py
```python
class ToolRegistry:
    """Central registry for tools"""
    def register(self, tool)
    def get_tools(self, categories=None, names=None)
```

### ai/workflows/
LangGraph workflow builders

## Integration When Both Merge

### Scenario 1: This PR Merges First

PR #20 will:
1. Add its files to the existing `ai/` structure
2. Use existing `ai/base.py` types
3. Import Meshy tools: `from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools`
4. No conflicts!

### Scenario 2: PR #20 Merges First

This PR will:
1. Keep the existing `ai/` from PR #20
2. Add `ai/tools/meshy_tools.py`
3. Add `ai/providers/crewai/` and `ai/providers/mcp/`
4. Meshy tools slot right in!

### Scenario 3: Both Already Merged

Just works! Structure is aligned:
```python
from vendor_connectors.ai import ToolCategory, ToolDefinition
from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools
from vendor_connectors.ai.connector import AIConnector

# Meshy tools work with AIConnector
ai = AIConnector(provider="anthropic")
meshy = MeshyConnector()
ai.register_connector_tools(meshy, ToolCategory.MESHY)
```

## Usage Examples

### Using Meshy Tools with CrewAI (Works Now)
```python
from vendor_connectors.ai.providers.crewai import get_tools
from crewai import Agent, Crew

tools = get_tools()  # Gets Meshy tools as CrewAI tools

agent = Agent(
    role="3D Asset Creator",
    goal="Generate game-ready 3D assets",
    tools=tools,
)

crew = Crew(agents=[agent])
```

### Using Meshy MCP Server (Works Now)
```bash
# Start the server
meshy-mcp

# Or programmatically
python -m vendor_connectors.ai.providers.mcp
```

### Using with AIConnector (After PR #20 Merges)
```python
from vendor_connectors.ai import AIConnector, ToolCategory
from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

# Register Meshy tools
connector = AIConnector(provider="anthropic")
for tool in get_meshy_tools():
    connector.registry.register(tool)

# Use with AI
response = connector.invoke(
    "Generate a 3D model of a medieval sword with ornate details",
    use_tools=True,
    categories=[ToolCategory.MESHY]
)
```

## Benefits

1. **Same Structure**: Both PRs have `ai/` with same layout
2. **Compatible Types**: Both use ToolParameter, ToolDefinition, ToolCategory
3. **No Conflicts**: Files don't overlap
4. **Easy Integration**: Just combine the implementations
5. **Framework Ready**: CrewAI and MCP work now, LangChain ready when PR #20 merges

## Summary

| Component | This PR | PR #20 | Result |
|-----------|---------|--------|--------|
| ai/base.py | ✓ | ✓ | Same types, compatible |
| ai/tools/meshy_tools.py | ✓ | - | Slots in |
| ai/tools/factory.py | - | ✓ | Slots in |
| ai/tools/registry.py | - | ✓ | Slots in |
| ai/connector.py | - | ✓ | Slots in |
| ai/providers/crewai/ | ✓ | - | Slots in |
| ai/providers/mcp/ | ✓ | - | Slots in |
| ai/providers/anthropic.py | - | ✓ | Slots in |
| ai/workflows/ | - | ✓ | Slots in |

**Result**: Perfect puzzle piece fit! 🧩
