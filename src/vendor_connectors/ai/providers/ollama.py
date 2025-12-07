"""Ollama (local models) provider using langchain-ollama.

This module provides local model access through Ollama.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    from langchain_ollama import ChatOllama
    from vendor_connectors.ai.providers.base import BaseLLMProvider

    class OllamaProvider(BaseLLMProvider):
        def __init__(
            self,
            model: Optional[str] = None,
            base_url: str = "http://localhost:11434",
            **kwargs,
        ):
            self.base_url = base_url
            super().__init__(model=model, **kwargs)

        @property
        def provider_name(self) -> str:
            return "ollama"

        @property
        def default_model(self) -> str:
            return "llama3.2"

        def _create_llm(self, **kwargs) -> ChatOllama:
            return ChatOllama(
                model=self.model,
                base_url=self.base_url,
                temperature=self.temperature,
                **kwargs,
            )
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
