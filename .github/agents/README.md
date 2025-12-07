# Custom Copilot Agents for vendor-connectors

This directory contains custom agent profiles that provide specialized expertise for common tasks in this repository.

## Available Agents

### 1. Test Coverage Agent (`test-coverage-agent.yml`)
**Purpose:** Improve test coverage and create high-quality tests

**Use when:**
- Adding tests for new features
- Improving coverage for existing code
- Working on Issue #21 (75% coverage goal)
- Creating test fixtures and mocks

**Expertise:**
- pytest patterns and fixtures
- unittest.mock and pytest-mock
- Coverage analysis
- Async testing with pytest-asyncio

### 2. Connector Builder Agent (`connector-builder-agent.yml`)
**Purpose:** Create new vendor connectors following jbcom patterns

**Use when:**
- Adding a new vendor integration
- Implementing DirectedInputsClass patterns
- Creating mixin-based architectures
- Building three-interface connectors (API + tools + MCP)

**Expertise:**
- DirectedInputsClass architecture
- Mixin patterns
- OAuth and API authentication
- LangChain tool creation
- MCP server implementation

### 3. AI Refactor Agent (`ai-refactor-agent.yml`)
**Purpose:** Execute the AI tooling refactor (Issue #33, PR #34)

**Use when:**
- Migrating tools from central ai/ package to connectors
- Creating LangChain StructuredTools
- Implementing MCP servers
- Cleaning up deprecated AI package code

**Expertise:**
- Current refactor status and goals
- LangChain StructuredTool patterns
- MCP (Model Context Protocol)
- Import path migrations
- Breaking change management

## How to Use Custom Agents

### Via GitHub Issues
When creating an issue, you can assign it to a specific agent by mentioning the agent profile in the issue description:

```markdown
@copilot use agent:test-coverage-agent

I need tests for the new ZoomConnector class covering all public methods.
```

### Via Copilot Chat
In Copilot chat, reference the agent:

```
@workspace /agent test-coverage-agent
Analyze coverage for src/vendor_connectors/slack/ and suggest test cases
```

### Via PR Comments
Tag the agent in PR review comments:

```
@copilot use agent:ai-refactor-agent
Help migrate AWS connector tools from ai/tools/aws_tools.py to aws/tools.py
```

## Agent Context

All agents have access to:
- `.github/copilot-instructions.md` - Repository patterns and build instructions
- `memory-bank/activeContext.md` - Current development context
- `pyproject.toml` - Configuration and dependencies
- Relevant example files based on their expertise

## Creating New Agents

To create a new specialized agent:

1. Create `<name>-agent.yml` in this directory
2. Define expertise, context, and guidelines
3. Add examples and anti-patterns
4. Update this README

See [GitHub Docs on Custom Agents](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/coding-agent/create-custom-agents) for the full specification.

## Best Practices

1. **Use the right agent for the task** - Each agent has deep context about its domain
2. **Provide specific details** - The more context you give, the better the agent can help
3. **Reference issues/PRs** - Agents understand the current state better with issue numbers
4. **Review agent suggestions** - Agents are experts but not infallible - always review their work
5. **Update agents** - As patterns evolve, update agent guidelines to match

## Related Documentation

- Main onboarding: [../.github/copilot-instructions.md](../copilot-instructions.md)
- Copilot Space config: [../.github/copilot-space.yml](../copilot-space.yml)
- Memory bank: [../../memory-bank/activeContext.md](../../memory-bank/activeContext.md)
