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
- `ai`: LangChain-based AI sub-package (NEW - blocked by PR #16)
- `ai-anthropic`, `ai-openai`, `ai-google`, `ai-xai`, `ai-ollama`: Provider-specific extras

### Development
```bash
uv sync --extra tests
uv run pytest tests/ -v
```

---

## AI Sub-Package (PR #17 - Blocked by PR #16)

### Status
- **Design Complete**: `docs/development/ai-subpackage-design.md`
- **Dependencies Drafted**: `docs/development/ai-dependencies-draft.toml`
- **Module Structure**: Placeholder stubs created in `src/vendor_connectors/ai/`
- **Blocked By**: PR #16 (Cursor/Anthropic connectors)
- **Blocks**: PR #18 (Meshy), jbcom/jbcom-control-center#342 (agentic-crew)

### Module Structure
```
vendor_connectors/ai/
├── __init__.py          # Public API (AIConnector)
├── base.py              # Types: AIProvider, AIResponse, ToolCategory
├── connector.py         # AIConnector - unified interface
├── providers/           # LangChain providers
│   ├── anthropic.py     # Claude via langchain-anthropic
│   ├── openai.py        # GPT via langchain-openai
│   ├── google.py        # Gemini via langchain-google-genai
│   ├── xai.py           # Grok via langchain-xai
│   └── ollama.py        # Local models via langchain-ollama
├── tools/               # Vendor connectors as AI tools
│   ├── factory.py       # Auto-generate tools from connector methods
│   ├── aws_tools.py     # AWS operations
│   ├── github_tools.py  # GitHub operations
│   ├── slack_tools.py   # Slack operations
│   ├── vault_tools.py   # Vault operations
│   └── ...
└── workflows/           # LangGraph support
    ├── builder.py       # Workflow builder DSL
    └── nodes.py         # Pre-built nodes
```

### Key Design Decisions
1. **LangChain-based**: Uses LangChain for provider abstraction, not raw API
2. **Tool Auto-generation**: Factory pattern to create tools from connector methods
3. **Provider-agnostic Interface**: Same API regardless of AI provider
4. **Optional LangSmith**: Tracing via langsmith_api_key parameter
5. **Following meshy.agent_tools Pattern**: Registry, base definitions, provider adapters

### Implementation Order (After PR #16)
1. Core types and interfaces (`ai/base.py`)
2. AIConnector class (`ai/connector.py`)
3. Anthropic provider (wraps existing connector)
4. Tool factory and GitHub tools
5. Additional providers
6. LangGraph workflows

---
*Last updated: 2025-12-07*
