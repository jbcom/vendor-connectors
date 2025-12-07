"""Anthropic (Claude) provider using langchain-anthropic.

This module provides Claude model access through LangChain.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    from langchain_anthropic import ChatAnthropic
    from vendor_connectors.ai.providers.base import BaseLLMProvider

    class AnthropicProvider(BaseLLMProvider):
        @property
        def provider_name(self) -> str:
            return "anthropic"

        @property
        def default_model(self) -> str:
            return "claude-3-5-sonnet-latest"

        def _create_llm(self, **kwargs) -> ChatAnthropic:
            return ChatAnthropic(
                model=self.model,
                api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs,
            )
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
