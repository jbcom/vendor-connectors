# Meshy AI Tools Integration Design

## Status

**Current**: Meshy tools are defined and exported through the unified `vendor_connectors.ai` package.
**Alignment**: Types and categories match PR #20's AI interfaces (`ToolParameter`, `ToolDefinition`).
**Compatibility**: Either PR can merge first—structures are already aligned.

## Current Meshy Structure (Aligned)

```
src/vendor_connectors/
├── meshy/
│   ├── __init__.py           # MeshyConnector class
│   ├── connector.py          # Main connector implementation
│   ├── text3d.py             # Text-to-3D operations
│   ├── rigging.py            # Model rigging
│   ├── animate.py            # Animation application
│   ├── retexture.py          # Texture modification
│   └── ...                   # Additional helpers
└── ai/
    ├── base.py               # ToolParameter, ToolDefinition (PR #20-compatible)
    ├── tools/
    │   ├── __init__.py
    │   └── meshy_tools.py    # Meshy tool definitions and handlers
    └── providers/
        ├── crewai/           # CrewAI integration
        └── mcp/              # MCP server
```

## Integration with PR #20 AI Sub-Package

### Tool Mapping

The unified `ai/tools/meshy_tools.py` exposes Meshy operations through PR #20's `ToolDefinition` interface:

| Meshy Tool | AI Tool Name | Description |
|------------|--------------|-------------|
| `text3d_generate` | `meshy_text_to_3d` | Generate 3D model from text |
| `rig_model` | `meshy_rig_model` | Add skeleton to model |
| `apply_animation` | `meshy_apply_animation` | Apply animation to rigged model |
| `retexture_model` | `meshy_retexture` | Change model textures |
| `list_animations` | `meshy_list_animations` | List available animations |
| `check_task_status` | `meshy_get_task` | Check task status |
| `get_animation` | `meshy_get_animation` | Get animation details |

## Usage Examples

### Using Meshy Tools with CrewAI
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

### Using Meshy MCP Server
```bash
# Start the server
meshy-mcp

# Or programmatically
python -m vendor_connectors.ai.providers.mcp
```

### Using with AIConnector
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
