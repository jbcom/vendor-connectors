# Vendor Connectors

Universal vendor connectors for the jbcom ecosystem, providing standardized access to cloud providers, third-party services, and AI APIs.

## Overview

Each connector provides **three interfaces**:

1. **Direct Python API** - Use the connector directly in your Python code
2. **LangChain Tools** - Standard StructuredTools for AI agents (works with LangChain, CrewAI, LangGraph, etc.)
3. **MCP Server** - Model Context Protocol server for Claude Desktop, Cline, and other MCP clients

This consistent pattern makes it easy to use vendor connectors however you need them.

## Features

### AI/Agent Connectors
- **Anthropic Connector**: Claude AI API wrapper with message generation, token counting, and model management
- **Cursor Connector**: Cursor Background Agent API for AI coding agent management

### Cloud Providers
- **AWS Connector**: Boto3-based client with role assumption and retry logic
- **Google Cloud Connector**: Workspace and Cloud Platform APIs with lazy credential loading

### Services
- **GitHub Connector**: Repository management, GraphQL queries, and file operations
- **Slack Connector**: Bot and app integrations with rate limiting
- **Vault Connector**: HashiCorp Vault with Token and AppRole auth
- **Zoom Connector**: Meeting and user management
- **Meshy Connector**: Meshy AI 3D asset generation (text-to-3D, rigging, animation, retexture)

### Unified Interface
- **VendorConnectors**: Cached public API with `get_*_client()` getters for all connectors

## Installation

```bash
pip install vendor-connectors
```

**Includes**: `langchain-core` for standard tool definitions. You choose your LLM provider separately.

### Optional Extras

```bash
# For Meshy webhooks
pip install vendor-connectors[webhooks]

# For Meshy AI tools (CrewAI-specific features)
pip install vendor-connectors[meshy-crewai]

# For Meshy MCP server
pip install vendor-connectors[meshy-mcp]

# All Meshy AI integrations
pip install vendor-connectors[meshy-ai]

# For Meshy vector store/RAG
pip install vendor-connectors[vector]

# Everything
pip install vendor-connectors[all]
```

### Choose Your LLM Provider

This package provides **tools**, not LLM wrappers. Install your preferred LLM provider separately:

```bash
pip install langchain-anthropic    # For Claude
pip install langchain-openai       # For GPT
pip install langchain-google-genai # For Gemini
# ... any LangChain-compatible provider
```

## Usage

### Using VendorConnectors (Recommended)

The `VendorConnectors` class provides cached access to all connectors:

```python
from vendor_connectors import VendorConnectors

# Initialize once - reads credentials from environment
vc = VendorConnectors()

# AI/Agent connectors
cursor = vc.get_cursor_client()       # Cursor Background Agent API
anthropic = vc.get_anthropic_client() # Claude AI

# Cloud providers
s3 = vc.get_aws_client("s3")
google = vc.get_google_client()

# Services
github = vc.get_github_client(github_owner="myorg")
slack = vc.get_slack_client()
vault = vc.get_vault_client()
zoom = vc.get_zoom_client()
```

### Using Individual Connectors

```python
from vendor_connectors import AWSConnector, GithubConnector, SlackConnector

# AWS with role assumption
aws = AWSConnector(execution_role_arn="arn:aws:iam::123456789012:role/MyRole")
s3 = aws.get_aws_client("s3")

# GitHub operations
github = GithubConnector(
    github_owner="myorg",
    github_repo="myrepo",
    github_token=os.getenv("GITHUB_TOKEN")
)

# Slack messaging
slack = SlackConnector(
    token=os.getenv("SLACK_TOKEN"),
    bot_token=os.getenv("SLACK_BOT_TOKEN")
)
slack.send_message("general", "Hello from vendor-connectors!")
```

### Anthropic Claude AI

```python
from vendor_connectors import AnthropicConnector

# Initialize with API key (or set ANTHROPIC_API_KEY env var)
claude = AnthropicConnector(api_key="...")

# Create a message
response = claude.create_message(
    model="claude-sonnet-4-5-20250929",  # Claude Sonnet 4.5
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain quantum computing in simple terms"}]
)
print(response.text)

# Count tokens before sending
tokens = claude.count_tokens(
    model="claude-sonnet-4-5-20250929",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Get recommended model for use case
model = claude.get_recommended_model("coding")  # Returns claude-sonnet-4-5-20250929
```

**Source of truth for models:** https://docs.anthropic.com/en/docs/about-claude/models

### Cursor Background Agents

```python
from vendor_connectors import CursorConnector

# Initialize with API key (or set CURSOR_API_KEY env var)
cursor = CursorConnector(api_key="...")

# List all agents
agents = cursor.list_agents()
for agent in agents:
    print(f"{agent.id}: {agent.state}")

# Launch a new agent
agent = cursor.launch_agent(
    prompt_text="Implement user authentication with OAuth2",
    repository="myorg/myrepo",
    ref="main",
    auto_create_pr=True
)
print(f"Launched agent: {agent.id}")

# Get agent status
status = cursor.get_agent_status(agent.id)
print(f"State: {status.state}")

# Send follow-up
cursor.add_followup(agent.id, "Also add rate limiting")

# List available repositories
repos = cursor.list_repositories()
```

**API Reference:** https://docs.cursor.com/account/api

### Meshy AI - Three Ways to Use

Meshy provides 3D asset generation with three interfaces:

#### 1. Direct Python API

```python
from vendor_connectors import meshy

# Generate a 3D model
model = meshy.text3d.generate("a medieval sword with ornate handle")
print(model.model_urls.glb)

# Rig it for animation
rigged = meshy.rigging.rig(model.id)

# Apply an animation (678 available)
animated = meshy.animate.apply(rigged.id, animation_id=0)  # Idle

# Or retexture it
gold = meshy.retexture.apply(model.id, "golden with embedded gems")
```

#### 2. LangChain Tools (Works with Any Framework)

The tools use LangChain's standard `StructuredTool` format, which works with:
- **LangChain** / **LangGraph**
- **CrewAI** (can use LangChain tools directly)
- Any framework that accepts LangChain tools

**With LangChain/LangGraph:**

```python
from vendor_connectors.meshy.tools import get_tools
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

# Create a LangChain agent with Meshy tools
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
tools = get_tools()  # Returns standard LangChain StructuredTools
agent = create_react_agent(llm, tools)

# Use the agent
result = agent.invoke({
    "messages": [("user", "Generate a 3D model of a futuristic spaceship")]
})
```

**With CrewAI (using LangChain tools):**

```python
from vendor_connectors.meshy.tools import get_tools
from crewai import Agent, Task, Crew

# CrewAI can use LangChain tools directly
tools = get_tools()  # Standard LangChain StructuredTools work in CrewAI
artist = Agent(
    role="3D Artist",
    goal="Create 3D assets as requested",
    tools=tools,  # Pass LangChain tools directly
    backstory="Expert 3D modeler specializing in game assets"
)

task = Task(
    description="Create a medieval sword and make it ready for animation",
    agent=artist
)

crew = Crew(agents=[artist], tasks=[task])
result = crew.kickoff()
```

**CrewAI-specific wrapper (optional):**

If you need CrewAI-specific features, use the wrapper:

```python
from vendor_connectors.meshy.tools import get_crewai_tools  # Optional CrewAI wrapper

tools = get_crewai_tools()
artist = Agent(role="3D Artist", tools=tools)
```

#### 3. MCP Server (for Claude Desktop, Cline, etc.)

```python
# Run the MCP server
from vendor_connectors.meshy.mcp import run_server
run_server()

# Or via command line:
# meshy-mcp
```

Configure in Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "meshy": {
      "command": "meshy-mcp",
      "env": {
        "MESHY_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Pattern: Three Interfaces Per Connector

Every connector follows the same pattern:

```python
# 1. Direct Python API
from vendor_connectors.{connector} import {functionality}

# 2. LangChain Tools (standard, works everywhere)
from vendor_connectors.{connector}.tools import get_tools

# 3. MCP Server
from vendor_connectors.{connector}.mcp import run_server
# or: {connector}-mcp  (command line)
```

This makes it easy to:
- **Test**: Each interface is independent
- **Document**: Consistent patterns across all connectors
- **Use**: Choose the interface that fits your needs

## Architecture

All connectors extend `DirectedInputsClass` from the jbcom ecosystem, providing:

### Transparent Secret Management

Every connector automatically loads credentials from multiple sources (in priority order):
1. **Direct parameters** - Pass to constructor
2. **Environment variables** - Standard naming conventions
3. **Configuration files** - YAML, JSON, or INI
4. **stdin** - Interactive prompts when needed

This works across **all three interfaces** (Python API, LangChain tools, MCP):

```python
# Option 1: Environment variable
export MESHY_API_KEY="your-key"
from vendor_connectors.meshy.tools import get_tools
tools = get_tools()  # Automatically uses MESHY_API_KEY

# Option 2: Direct parameter
from vendor_connectors import meshy
model = meshy.text3d.generate("sword", api_key="your-key")

# Option 3: Config file
# meshy_config.yaml:
# meshy_api_key: your-key
```

### Additional Benefits from jbcom Ecosystem

- **directed-inputs-class**: Flexible input handling from environment, stdin, config
- **lifecyclelogging**: Structured logging with verbosity control
- **extended-data-types**: Utilities like `is_nothing`, `strtobool`, `wrap_raw_data_for_export`

The `VendorConnectors` class provides:
- Client caching (same parameters = same instance)
- Automatic credential loading from environment
- Consistent interface across all providers

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API key |
| `CURSOR_API_KEY` | Cursor Background Agent API key |
| `AWS_*` | Standard AWS credentials |
| `EXECUTION_ROLE_ARN` | AWS role to assume |
| `GITHUB_TOKEN` | GitHub personal access token |
| `GITHUB_OWNER` | GitHub organization/user |
| `GOOGLE_SERVICE_ACCOUNT` | Google service account JSON |
| `SLACK_TOKEN` | Slack user token |
| `SLACK_BOT_TOKEN` | Slack bot token |
| `VAULT_ADDR` | Vault server URL |
| `VAULT_TOKEN` | Vault authentication token |
| `VAULT_ROLE_ID` / `VAULT_SECRET_ID` | AppRole credentials |
| `ZOOM_CLIENT_ID` / `ZOOM_CLIENT_SECRET` / `ZOOM_ACCOUNT_ID` | Zoom OAuth |
| `MESHY_API_KEY` | Meshy AI API key |

## Part of jbcom Ecosystem

This package is part of the jbcom Python library ecosystem:
- [extended-data-types](https://pypi.org/project/extended-data-types/) - Foundation utilities
- [lifecyclelogging](https://pypi.org/project/lifecyclelogging/) - Structured logging
- [directed-inputs-class](https://pypi.org/project/directed-inputs-class/) - Input handling
