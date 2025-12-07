"""Google (Gemini) provider using langchain-google-genai.

This module provides Gemini model access through LangChain.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    from langchain_google_genai import ChatGoogleGenerativeAI
    from vendor_connectors.ai.providers.base import BaseLLMProvider

    class GoogleProvider(BaseLLMProvider):
        @property
        def provider_name(self) -> str:
            return "google"

        @property
        def default_model(self) -> str:
            return "gemini-1.5-pro"

        def _create_llm(self, **kwargs) -> ChatGoogleGenerativeAI:
            return ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=self.api_key,
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
                **kwargs,
            )
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
