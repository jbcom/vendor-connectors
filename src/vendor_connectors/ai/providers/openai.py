"""OpenAI (GPT) provider using langchain-openai.

This module provides GPT model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["OpenAIProvider"]


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider via LangChain.

    Uses langchain-openai for GPT API access with full
    tool calling and streaming support.

    Example:
        >>> provider = OpenAIProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.OPENAI

    @property
    def default_model(self) -> str:
        """Get default GPT model."""
        return "gpt-4o"

    def _create_llm(self) -> Any:
        """Create LangChain ChatOpenAI instance."""
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as e:
            raise ImportError(
                "langchain-openai is required for OpenAI provider. "
                "Install with: pip install vendor-connectors[ai-openai]"
            ) from e

        api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter."
            )

        return ChatOpenAI(
            model=self.model,
            api_key=api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **self._kwargs,
        )
