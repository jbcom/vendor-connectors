"""Base class for LLM providers.

This module defines the abstract BaseLLMProvider interface that all
provider implementations must follow.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    class BaseLLMProvider(ABC):
        def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
            temperature: float = 0.7,
            max_tokens: int = 4096,
            **kwargs,
        ):
            self.model = model or self.default_model
            self._llm = self._create_llm(**kwargs)

        @property
        @abstractmethod
        def provider_name(self) -> str:
            ...

        @property
        @abstractmethod
        def default_model(self) -> str:
            ...

        @abstractmethod
        def _create_llm(self, **kwargs) -> Any:
            ...

        def chat(
            self,
            message: str,
            system_prompt: Optional[str] = None,
            history: Optional[list[AIMessage]] = None,
            tools: Optional[list] = None,
        ) -> AIResponse:
            ...

        def invoke_with_tools(
            self,
            message: str,
            tools: list,
            max_iterations: int = 10,
        ) -> AIResponse:
            ...
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
