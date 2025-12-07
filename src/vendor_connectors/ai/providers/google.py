"""Google (Gemini) provider using langchain-google-genai.

This module provides Gemini model access through LangChain.
"""

from __future__ import annotations

import os
from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["GoogleProvider"]


class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider via LangChain.

    Uses langchain-google-genai for Gemini API access with full
    tool calling and streaming support.

    Example:
        >>> provider = GoogleProvider(api_key="...")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.GOOGLE

    @property
    def default_model(self) -> str:
        """Get default Gemini model."""
        return "gemini-1.5-pro"

    def _create_llm(self) -> Any:
        """Create LangChain ChatGoogleGenerativeAI instance."""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError as e:
            raise ImportError(
                "langchain-google-genai is required for Google provider. "
                "Install with: pip install vendor-connectors[ai-google]"
            ) from e

        api_key = self.api_key or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )

        return ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=api_key,
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            **self._kwargs,
        )
