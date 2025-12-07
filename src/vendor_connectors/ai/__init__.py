"""AI Sub-Package for vendor-connectors.

This package provides a unified AI interface leveraging LangChain/LangGraph for:
- Multi-provider AI access (Anthropic, OpenAI, Google, xAI, Ollama)
- Tool abstraction - expose existing vendor connectors as AI-callable tools
- Tracing/observability via LangSmith

Status: PLACEHOLDER - Implementation blocked by PR #16
Design Document: docs/development/ai-subpackage-design.md

Usage (after implementation):
    from vendor_connectors.ai import AIConnector

    # Same interface, different providers
    ai = AIConnector(provider="anthropic")  # or "openai", "google", "ollama"
    response = ai.chat("Explain this code")

    # With tools for agentic workflows
    from vendor_connectors.ai.tools import get_all_tools

    ai = AIConnector(
        provider="openai",
        tools=get_all_tools(),
    )
    response = ai.invoke_with_tools("Create a GitHub issue for this bug")

Related:
    - Epic: jbcom/jbcom-control-center#340
    - Blocks: PR #18 (Meshy), jbcom/jbcom-control-center#342 (agentic-crew)
"""

from __future__ import annotations

__all__ = [
    # Will export:
    # "AIConnector",
    # "AIProvider",
    # "AIResponse",
    # "AIMessage",
]

# Placeholder - actual imports will be added after PR #16 merges
# from vendor_connectors.ai.base import AIProvider, AIResponse, AIMessage
# from vendor_connectors.ai.connector import AIConnector
