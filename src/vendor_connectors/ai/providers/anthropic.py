"""Anthropic (Claude) provider using langchain-anthropic.

This module provides Claude model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["AnthropicProvider"]


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider via LangChain.

    Uses langchain-anthropic for Claude API access with full
    tool calling and streaming support.

    Example:
        >>> provider = AnthropicProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.ANTHROPIC

    @property
    def default_model(self) -> str:
        """Get default Claude model."""
        return "claude-sonnet-4-20250514"

    def _create_llm(self) -> Any:
        """Create LangChain ChatAnthropic instance."""
        try:
            from langchain_anthropic import ChatAnthropic
        except ImportError as e:
            raise ImportError(
                "langchain-anthropic is required for Anthropic provider. "
                "Install with: pip install vendor-connectors[ai-anthropic]"
            ) from e

        api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key is required. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key parameter."
            )

        return ChatAnthropic(
            model=self.model,
            api_key=api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **self._kwargs,
        )
