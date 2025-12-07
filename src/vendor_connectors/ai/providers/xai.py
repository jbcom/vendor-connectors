"""xAI (Grok) provider using langchain-xai.

This module provides Grok model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["XAIProvider"]


class XAIProvider(BaseLLMProvider):
    """xAI Grok provider via LangChain.

    Uses langchain-xai for Grok API access.

    Example:
        >>> provider = XAIProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.XAI

    @property
    def default_model(self) -> str:
        """Get default Grok model."""
        return "grok-2"

    def _create_llm(self) -> Any:
        """Create LangChain ChatXAI instance."""
        try:
            from langchain_xai import ChatXAI
        except ImportError as e:
            raise ImportError(
                "langchain-xai is required for xAI provider. Install with: pip install vendor-connectors[ai-xai]"
            ) from e

        api_key = self.api_key or os.environ.get("XAI_API_KEY")
        if not api_key:
            raise ValueError("xAI API key is required. Set XAI_API_KEY environment variable or pass api_key parameter.")

        return ChatXAI(
            model=self.model,
            xai_api_key=api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **self._kwargs,
        )
