# Active Context

## vendor-connectors

Universal vendor connectors for cloud providers and third-party services.

### Included Connectors
- **AWS**: Organizations, SSO, S3, Secrets Manager
- **Google Cloud**: Workspace, Cloud Platform, Billing
- **GitHub**: Repository operations, PR management
- **Slack**: Channel and message operations
- **Vault**: HashiCorp Vault secret management
- **Zoom**: User and meeting management
- **Meshy**: Meshy AI 3D asset generation (merged from mesh-toolkit)

### Package Status
- **Registry**: PyPI
- **Python**: 3.10+ (crewai requires 3.10+)
- **Dependencies**: extended-data-types, lifecyclelogging, directed-inputs-class

### Optional Extras
- `webhooks`: Meshy webhooks support
- `crewai`: CrewAI agent integration
- `mcp`: MCP server integration
- `vector`: Vector store for RAG
- `all`: Everything
- `ai`: LangChain-based AI sub-package (PR #20)
- `ai-anthropic`, `ai-openai`, `ai-google`, `ai-xai`, `ai-ollama`: Provider-specific extras

### Development
```bash
uv sync --extra tests
uv run pytest tests/ -v
```

---

## AI Sub-Package - IMPLEMENTED

### Status
- **PR #16 MERGED**: Cursor/Anthropic connectors now available
- **AI Package IMPLEMENTED**: Full implementation in `src/vendor_connectors/ai/`
- **Dependencies Added**: `pyproject.toml` updated with ai extras
- **Test Coverage Issue**: #21 created to increase coverage to 75%

### Implemented Structure
```
vendor_connectors/ai/
├── __init__.py          # Public API (AIConnector, types)
├── base.py              # Types: AIProvider, AIResponse, ToolCategory, etc.
├── connector.py         # AIConnector - unified interface
├── providers/
│   ├── __init__.py      # get_provider() factory
│   ├── base.py          # BaseLLMProvider abstract class
│   ├── anthropic.py     # Claude via langchain-anthropic
│   ├── openai.py        # GPT via langchain-openai
│   ├── google.py        # Gemini via langchain-google-genai
│   ├── xai.py           # Grok via langchain-xai
│   └── ollama.py        # Local models via langchain-ollama
├── tools/
│   ├── __init__.py      # Public exports
│   ├── factory.py       # ToolFactory - auto-generate from connectors
│   └── registry.py      # ToolRegistry - central tool management
└── workflows/
    ├── __init__.py      # Public exports
    ├── builder.py       # WorkflowBuilder DSL for LangGraph
    └── nodes.py         # Pre-built nodes (ToolNode, ConditionalNode)
```

### Optional Dependencies (pyproject.toml)
- `ai`: Core LangChain + LangGraph
- `ai-anthropic`: + langchain-anthropic
- `ai-openai`: + langchain-openai
- `ai-google`: + langchain-google-genai
- `ai-xai`: + langchain-xai
- `ai-ollama`: + langchain-ollama
- `ai-all`: All providers
- `ai-observability`: LangSmith tracing

### Usage Example
```python
from vendor_connectors.ai import AIConnector, ToolCategory
from vendor_connectors.github import GitHubConnector

# Create connector
connector = AIConnector(provider="anthropic", api_key="...")

# Simple chat
response = connector.chat("Hello!")

# With tools
gh = GitHubConnector(token="...")
connector.register_connector_tools(gh, ToolCategory.GITHUB)
response = connector.invoke("List my repositories")
```

### Related Issues
- Issue #21: Increase test coverage to 75%
- Blocks: PR #18 (Meshy), jbcom/jbcom-control-center#342

---
*Last updated: 2025-12-07*
