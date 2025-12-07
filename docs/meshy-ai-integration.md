# Meshy AI Tools Integration Design

## Status

**Current**: Meshy connector is implemented in `src/vendor_connectors/meshy/`  
**Blocked by**: PR #20 (AI sub-package)  
**Next Step**: Create `vendor_connectors/ai/tools/meshy_tools.py` after PR #20 merges

## Overview

This document describes how the existing Meshy connector will integrate with the `vendor_connectors.ai` sub-package once PR #20 is merged.

## Current Meshy Structure

The Meshy connector already has a complete agent tools system:

```
src/vendor_connectors/meshy/
├── __init__.py           # MeshyConnector class
├── connector.py          # Main connector implementation
├── text3d.py            # Text-to-3D operations
├── rigging.py           # Model rigging
├── animate.py           # Animation application
├── retexture.py         # Texture modification
└── agent_tools/         # Existing AI framework integrations
    ├── base.py          # Tool definitions
    ├── tools.py         # Tool handlers
    ├── registry.py      # Provider registry
    ├── crewai/          # CrewAI integration
    └── mcp/             # MCP server
```

## Integration with PR #20 AI Sub-Package

### Tool Mapping

The existing `meshy/agent_tools/tools.py` defines these tools that will be exposed via PR #20's AI system:

| Meshy Tool | PR #20 Tool Name | Description |
|------------|------------------|-------------|
| `text3d_generate` | `meshy_text_to_3d` | Generate 3D model from text |
| `rig_model` | `meshy_rig_model` | Add skeleton to model |
| `apply_animation` | `meshy_apply_animation` | Apply animation to rigged model |
| `retexture_model` | `meshy_retexture` | Change model textures |
| `list_animations` | `meshy_list_animations` | List available animations |
| `check_task_status` | `meshy_get_task` | Check task status |
| `get_animation` | `meshy_get_animation` | Get animation details |

### Future Implementation: `ai/tools/meshy_tools.py`

When PR #20 merges, create `src/vendor_connectors/ai/tools/meshy_tools.py`:

```python
"""Meshy 3D generation operations as AI-callable tools.

Bridges the existing meshy.agent_tools system to the vendor_connectors.ai
tool abstraction layer.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vendor_connectors.ai.base import ToolDefinition

__all__ = ["get_meshy_tools"]


def get_meshy_tools() -> list[ToolDefinition]:
    """Get Meshy tools in PR #20's ToolDefinition format.
    
    Converts existing meshy.agent_tools definitions to the unified
    AI sub-package format.
    
    Returns:
        List of ToolDefinition objects for Meshy operations.
    """
    from vendor_connectors.ai.base import ToolCategory, ToolDefinition, ToolParameter
    from vendor_connectors.meshy.agent_tools.base import get_tool_definitions
    
    # Get existing Meshy tool definitions
    meshy_tools = get_tool_definitions()
    
    # Convert to PR #20 format
    ai_tools = []
    for tool in meshy_tools:
        # Map Meshy's ParameterDefinition to PR #20's ToolParameter
        parameters = {
            name: ToolParameter(
                name=param.name,
                description=param.description,
                type=param.type,
                required=param.required,
                default=param.default,
                enum_values=param.enum_values,
            )
            for name, param in tool.parameters.items()
        }
        
        # Create unified ToolDefinition
        ai_tool = ToolDefinition(
            name=f"meshy_{tool.name}",
            description=tool.description,
            category=ToolCategory.MESHY,
            parameters=parameters,
            handler=tool.handler,
            connector_class=None,  # Handlers are standalone functions
            method_name=None,
        )
        ai_tools.append(ai_tool)
    
    return ai_tools
```

### Usage After PR #20 Merges

Once both PR #20 (AI sub-package) and this PR (Meshy connector) are merged:

```python
from vendor_connectors.ai import AIConnector, ToolCategory
from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

# Initialize AI connector
ai = AIConnector(provider="anthropic", api_key="...")

# Register Meshy tools
for tool in get_meshy_tools():
    ai.registry.register(tool)

# Use Meshy tools via AI
response = ai.invoke(
    "Generate a 3D model of a medieval sword with ornate details",
    use_tools=True,
    categories=[ToolCategory.MESHY]
)
print(response.content)
```

### Alternative: Direct MeshyConnector Integration

For more direct integration with the MeshyConnector class:

```python
from vendor_connectors.ai import AIConnector, ToolCategory
from vendor_connectors.meshy import MeshyConnector

# Create connectors
ai = AIConnector(provider="anthropic")
meshy = MeshyConnector()

# Auto-generate tools from MeshyConnector methods
ai.register_connector_tools(
    meshy,
    category=ToolCategory.MESHY,
    method_filter=lambda name: name in [
        "text_to_3d",
        "image_to_3d", 
        "get_task",
        "download_model",
        "rig_model",
        "apply_animation",
        "retexture_model"
    ]
)

# Now AI can call Meshy operations
response = ai.invoke(
    "Create a 3D otter character, rig it, and apply an idle animation",
    use_tools=True
)
```

## Otterfall Integration

For the `jbcom/otterfall` asset_pipeline crew:

```yaml
# From otterfall/.crewai/crews/asset_pipeline/agents.yaml
prompt_engineer:
  role: Meshy Prompt Engineer
  goal: Craft prompts for high-quality 3D models from Meshy
  tools:
    - meshy_text_to_3d
    - meshy_get_task
    - meshy_rig_model
    - meshy_apply_animation
```

```python
# In otterfall asset pipeline
from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools
from crewai import Agent

tools = get_meshy_tools()

prompt_engineer = Agent(
    role="Meshy Prompt Engineer",
    goal="Craft prompts that produce high-quality, game-ready 3D models",
    tools=[t for t in tools if t.name in [
        "meshy_text_to_3d",
        "meshy_get_task",
        "meshy_rig_model",
        "meshy_apply_animation"
    ]],
    verbose=True
)
```

## Benefits of This Integration

1. **Unified API**: All vendor connectors (AWS, GitHub, Slack, Meshy) use the same tool interface
2. **Multi-Framework**: Works with LangChain, CrewAI, MCP, and custom agents
3. **Type Safety**: Strong typing via ToolDefinition and ToolParameter
4. **Discovery**: Tools can be listed, filtered by category, and introspected
5. **Flexibility**: Use either pre-built tool handlers or auto-generated from connector methods

## Migration Path

1. **Now**: This PR adds MeshyConnector (done ✓)
2. **PR #20**: Adds `vendor_connectors/ai` sub-package
3. **After Both Merge**: Create `ai/tools/meshy_tools.py` as bridge
4. **Otterfall**: Update asset_pipeline crew to use new tools

## Related

- Issue: jbcom/vendor-connectors#18 (this issue)
- PR #20: AI sub-package implementation
- Epic: jbcom/jbcom-control-center#340
- Consumer: jbcom/otterfall asset_pipeline crew
