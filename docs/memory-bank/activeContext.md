# Active Context - vendor-connectors

## Current State (December 2024)

### Architectural Decision: Decoupled AI Orchestration

**Key Decision**: `vendor-connectors` is a **pure HTTP connector library**. AI crew orchestration lives in [agentic-crew](https://github.com/jbcom/agentic-crew).

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    vendor-connectors                             │
│                                                                  │
│  HTTP Connectors: AWS, GitHub, Meshy, Slack, Vault, Zoom, etc.  │
│                                                                  │
│  Each connector exports:                                         │
│  - Direct Python API ({connector}/__init__.py)                  │
│  - Framework tools ({connector}/tools.py) - optional            │
│  - MCP server ({connector}/mcp.py) - optional                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Uses tools from
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    agentic-crew                                  │
│                                                                  │
│  Framework-agnostic AI crew orchestration                        │
│  - Declare crews in YAML once                                   │
│  - Run on CrewAI, LangGraph, or Strands                         │
│  - Auto-detects available frameworks                            │
└─────────────────────────────────────────────────────────────────┘
```

### Tool Export Pattern (Implemented in Meshy)

```python
# vendor_connectors/meshy/tools.py
def get_tools(framework: str = "auto") -> list:
    """Auto-detect framework and return native tools."""

def get_langchain_tools() -> list:
    """LangChain StructuredTools."""

def get_crewai_tools() -> list:
    """CrewAI-native tools via @tool decorator."""

def get_strands_tools() -> list:
    """Plain Python functions for Strands."""
```

### Active Work

#### In vendor-connectors
- Issue #36: Integration with agentic-crew
- Issue #33: AI tooling restructure (partially complete - Meshy done)
- Issue #17: AI sub-package (superseded by agentic-crew)

#### In agentic-crew
- PR #1: Framework decomposition architecture
- Issue #2: Epic - Framework decomposition
- Issue #5: connector_builder crew
- Issue #8: vendor-connectors integration

### Next Steps

1. **agentic-crew**: Merge PR #1, add tests for decomposer and runners
2. **agentic-crew**: Implement connector_builder crew
3. **vendor-connectors**: Apply Meshy tool pattern to other connectors as needed
4. **vendor-connectors**: Add `.crewai/` directory for dev workflows

### Related Repositories

| Repository | Purpose | Status |
|------------|---------|--------|
| [agentic-crew](https://github.com/jbcom/agentic-crew) | AI crew orchestration | PR #1 open |
| [vendor-connectors](https://github.com/jbcom/vendor-connectors) | HTTP connectors | Active |
| [directed-inputs-class](https://github.com/jbcom/directed-inputs-class) | Credential management | Stable |

### GitHub Project

All planning is tracked in: [jbcom Ecosystem Integration](https://github.com/users/jbcom/projects/2)

---

## Session History

### Session: 2024-12-07
- Created agentic-crew repository framework decomposition architecture
- Implemented runners for CrewAI, LangGraph, Strands
- Created comprehensive documentation (AGENTS.md, .cursor/rules, .github/agents)
- Set up CI/CD, CodeQL, Cursor environment
- Created issues for planned work in both repositories
- Updated vendor-connectors issues with architectural decision
- Added items to GitHub project
