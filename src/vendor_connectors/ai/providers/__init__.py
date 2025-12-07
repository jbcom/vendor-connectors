"""LangChain-based AI providers.

This package contains provider implementations for:
- Anthropic (Claude) - langchain-anthropic
- OpenAI (GPT) - langchain-openai
- Google (Gemini) - langchain-google-genai
- xAI (Grok) - langchain-xai
- Ollama (local models) - langchain-ollama

Each provider implements the BaseLLMProvider interface and handles
the conversion between our unified API and the specific LangChain integration.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Usage (after implementation):
    from vendor_connectors.ai.providers import get_provider

    # Get a specific provider
    anthropic = get_provider("anthropic", model="claude-3-5-sonnet-latest")
    response = anthropic.chat("Hello!")

    # Or use via AIConnector (preferred)
    from vendor_connectors.ai import AIConnector
    ai = AIConnector(provider="openai", model="gpt-4o")
"""

from __future__ import annotations

__all__ = [
    # Will export:
    # "get_provider",
    # "list_providers",
    # "BaseLLMProvider",
]

# Placeholder - actual imports will be added after PR #16 merges
# from vendor_connectors.ai.providers.base import BaseLLMProvider
# from vendor_connectors.ai.providers.registry import get_provider, list_providers
