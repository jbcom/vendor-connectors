# Custom Cursor Agent Profiles

This directory contains specialized agent profiles for common tasks in this repository.

## Available Agents

### 1. Connector Builder (`connector-builder.mdc`)
**Purpose:** Create new vendor connectors following jbcom patterns

**Use when:**
- Adding a new vendor integration
- Implementing VendorConnectorBase patterns
- Creating mixin-based architectures
- Building three-interface connectors (API + tools + MCP)

### 2. E2E Testing (`e2e-testing.mdc`)
**Purpose:** Create end-to-end tests that prove complete AI agent workflows

**Use when:**
- Adding E2E tests for a connector
- Recording VCR cassettes
- Validating AI agent integrations
- Saving artifacts to prove functionality

### 3. AI Refactor (`ai-refactor.mdc`)
**Purpose:** Add LangChain tools and MCP servers to connectors

**Use when:**
- Adding LangChain StructuredTools to a connector
- Implementing MCP servers
- Following the three-interface pattern
- Migrating tools from central ai/ package

## How to Use

In Cursor, these rules are automatically applied based on file glob patterns:

- `connector-builder.mdc` applies to `src/vendor_connectors/**/*.py`
- `e2e-testing.mdc` applies to `tests/e2e/**/*.py`
- `ai-refactor.mdc` applies to `**/tools.py` and `**/mcp.py`

## Agent Context

All agents have access to:
- `AGENTS.md` - Repository patterns and instructions
- `CLAUDE.md` - Claude-specific guidance
- `memory-bank/activeContext.md` - Current development context
- `.cursor/rules/` - All rule files

## Creating New Agents

To create a new specialized agent:

1. Create `<name>.mdc` in this directory
2. Add frontmatter with description and globs
3. Define expertise, patterns, and examples
4. Include anti-patterns to avoid

Example structure:
```markdown
---
description: Agent profile for X
globs: "pattern/**/*.py"
---

# X Agent

Expert at...

## When to Use

## Required Patterns

## Anti-Patterns
```

## Best Practices

1. **Use the right agent for the task** - Each agent has deep context
2. **Check memory bank first** - `cat memory-bank/activeContext.md`
3. **Follow the patterns** - Don't deviate without good reason
4. **Save artifacts** - E2E tests must save real files
5. **Update context** - Document what you did in memory bank
