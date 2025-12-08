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
- `meshy-crewai`: CrewAI tools for Meshy
- `meshy-mcp`: MCP server for Meshy
- `meshy-ai`: All Meshy AI integrations
- `vector`: Vector store for RAG
- `all`: Everything

**Note**: `langchain-core` is a required dependency. We provide TOOLS, you choose your LLM provider.

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
# Base installation includes langchain-core (required for tools)
pip install vendor-connectors

# CrewAI tools
pip install vendor-connectors[meshy-crewai]

# MCP server
pip install vendor-connectors[meshy-mcp]

# All AI integrations
pip install vendor-connectors[meshy-ai]
```

**Important**: This package provides TOOLS only. You choose and install your LLM provider separately:
```bash
# Choose your LLM provider (not included)
pip install langchain-anthropic  # For Claude
pip install langchain-openai     # For GPT
pip install langchain-google-genai  # For Gemini
# etc.
```

---

## Session: 2025-12-07 (E2E Testing & Documentation)

### Completed
- **VendorConnectorBase created** (`src/vendor_connectors/base.py`)
  - Proper base class for ALL connectors
  - Extends DirectedInputsClass
  - HTTP client with retries, rate limiting
  - MCP/LangChain tool helpers

- **Meshy base.py updated** to use DirectedInputsClass for credential loading

- **ArtStyle enum fixed** per Meshy API docs
  - Changed from invalid values (cartoon, low-poly, sculpt, pbr)
  - To correct values: `realistic`, `sculpture`

- **E2E tests created** (`tests/e2e/meshy/`)
  - `test_langchain.py` - LangGraph ReAct agent tests
  - `test_crewai.py` - CrewAI agent tests
  - `test_strands.py` - AWS Strands agent tests
  - Tests generate REAL 3D models and save GLB files

- **Real artifacts saved**
  - `tests/e2e/fixtures/models/langchain_sword_*.glb` (720KB)
  - VCR cassettes for API replay

- **Documentation created**
  - `AGENTS.md` - Comprehensive agent instructions
  - `.cursor/rules/agents/` - Agent profiles
    - `connector-builder.mdc`
    - `e2e-testing.mdc`
    - `ai-refactor.mdc`
  - Updated `CLAUDE.md` with GITHUB_JBCOM_TOKEN pattern

### Key Patterns Established
1. **GITHUB_JBCOM_TOKEN**: Always use `GH_TOKEN="$GITHUB_JBCOM_TOKEN" gh <command>`
2. **VendorConnectorBase**: All new connectors extend this
3. **Three-Interface Pattern**: API + tools.py + mcp.py
4. **E2E Tests**: Must save real artifacts to prove functionality

### Next Steps
- [ ] Run CrewAI and Strands E2E tests
- [ ] Create sub-issues for other connector AI tooling
- [ ] Update GitHub Projects

---
*Last updated: 2025-12-07*
