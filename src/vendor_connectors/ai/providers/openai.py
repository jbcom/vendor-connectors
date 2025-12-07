"""OpenAI (GPT) provider using langchain-openai.

This module provides GPT model access through LangChain.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    from langchain_openai import ChatOpenAI
    from vendor_connectors.ai.providers.base import BaseLLMProvider

    class OpenAIProvider(BaseLLMProvider):
        @property
        def provider_name(self) -> str:
            return "openai"

        @property
        def default_model(self) -> str:
            return "gpt-4o"

        def _create_llm(self, **kwargs) -> ChatOpenAI:
            return ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
