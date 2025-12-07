"""Ollama (local models) provider using langchain-ollama.

This module provides local model access through Ollama.
"""

from __future__ import annotations

from typing import Any

from vendor_connectors.ai.base import AIProvider
from vendor_connectors.ai.providers.base import BaseLLMProvider

__all__ = ["OllamaProvider"]


class OllamaProvider(BaseLLMProvider):
    """Ollama local model provider via LangChain.

    Uses langchain-ollama for local model access. Requires
    Ollama to be running locally.

    Example:
        >>> provider = OllamaProvider(model="llama3.2")
        >>> response = provider.chat("Hello!")
        >>> print(response.content)
    """

    def __init__(
        self,
        model: str | None = None,
        base_url: str = "http://localhost:11434",
        temperature: float = 0.7,
        **kwargs,
    ):
        """Initialize Ollama provider.

        Args:
            model: Model name (e.g., "llama3.2", "mistral").
            base_url: Ollama server URL.
            temperature: Sampling temperature.
            **kwargs: Additional arguments.
        """
        self.base_url = base_url
        # Ollama doesn't use max_tokens the same way
        super().__init__(model=model, temperature=temperature, max_tokens=4096, **kwargs)

    @property
    def provider_name(self) -> AIProvider:
        """Get provider identifier."""
        return AIProvider.OLLAMA

    @property
    def default_model(self) -> str:
        """Get default Ollama model."""
        return "llama3.2"

    def _create_llm(self) -> Any:
        """Create LangChain ChatOllama instance."""
        try:
            from langchain_ollama import ChatOllama
        except ImportError as e:
            raise ImportError(
                "langchain-ollama is required for Ollama provider. "
                "Install with: pip install vendor-connectors[ai-ollama]"
            ) from e

        return ChatOllama(
            model=self.model,
            base_url=self.base_url,
            temperature=self.temperature,
            **self._kwargs,
        )
