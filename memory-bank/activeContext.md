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
- **Meshy**: Meshy AI 3D asset generation with AI agent tools

### Package Status
- **Registry**: PyPI
- **Python**: 3.10+ (crewai requires 3.10+)
- **Dependencies**: extended-data-types, lifecyclelogging, directed-inputs-class

### Optional Extras
- `webhooks`: Meshy webhooks support
- `meshy-langchain`: LangChain tools for Meshy
- `meshy-crewai`: CrewAI tools for Meshy
- `meshy-mcp`: MCP server for Meshy
- `meshy-ai`: All Meshy AI integrations
- `vector`: Vector store for RAG
- `all`: Everything

### Development
```bash
uv sync --extra tests
uv run pytest tests/ -v
```

---

## Meshy AI Tools - NEW ARCHITECTURE

### Status
- **REFACTORED**: AI tools now live with their connectors, not in a central AI package
- **Each connector owns its tools**: `meshy/tools.py`, `meshy/mcp.py`
- **No wrappers**: Use LangChain, CrewAI, and MCP directly

### Structure
```
vendor_connectors/meshy/
├── __init__.py       # API client (existing)
├── tools.py          # LangChain StructuredTools
└── mcp.py            # MCP server
```

### Usage Examples

#### LangChain
```python
from vendor_connectors.meshy.tools import get_tools
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
tools = get_tools()
agent = create_react_agent(llm, tools)

result = agent.invoke({"messages": [("user", "Generate a 3D sword")]})
```

#### CrewAI
```python
from vendor_connectors.meshy.tools import get_crewai_tools
from crewai import Agent

tools = get_crewai_tools()
agent = Agent(role="3D Artist", tools=tools)
```

#### MCP Server
```python
from vendor_connectors.meshy.mcp import create_server, run_server

server = create_server()
run_server(server)

# Or via command line:
# meshy-mcp
```

### Installation
```bash
# LangChain tools
pip install vendor-connectors[meshy-langchain]

# CrewAI tools
pip install vendor-connectors[meshy-crewai]

# MCP server
pip install vendor-connectors[meshy-mcp]

# All AI integrations
pip install vendor-connectors[meshy-ai]
```

---
*Last updated: 2025-12-07*
