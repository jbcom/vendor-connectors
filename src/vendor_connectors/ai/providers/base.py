"""Base class for LLM providers.

This module defines the abstract BaseLLMProvider interface that all
provider implementations must follow.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from vendor_connectors.ai.base import AIMessage, AIProvider, AIResponse

if TYPE_CHECKING:
    pass

__all__ = ["BaseLLMProvider"]


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    Each provider (Anthropic, OpenAI, etc.) implements this interface
    to provide a consistent API across different LLM backends.

    Attributes:
        model: The model identifier being used.
        api_key: API key for authentication.
        temperature: Sampling temperature (0-1).
        max_tokens: Maximum tokens to generate.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ):
        """Initialize the provider.

        Args:
            model: Model identifier. Uses default_model if not specified.
            api_key: API key for authentication.
            temperature: Sampling temperature (0-1).
            max_tokens: Maximum tokens to generate.
            **kwargs: Additional provider-specific arguments.
        """
        self.model = model or self.default_model
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._llm: Any = None
        self._kwargs = kwargs

    @property
    @abstractmethod
    def provider_name(self) -> AIProvider:
        """Get the provider identifier."""
        ...

    @property
    @abstractmethod
    def default_model(self) -> str:
        """Get the default model for this provider."""
        ...

    @abstractmethod
    def _create_llm(self) -> Any:
        """Create the LangChain LLM instance.

        Returns:
            LangChain chat model instance.
        """
        ...

    @property
    def llm(self) -> Any:
        """Get or create the LangChain LLM instance."""
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        history: Optional[list[AIMessage]] = None,
        tools: Optional[list] = None,
    ) -> AIResponse:
        """Send a chat message and get a response.

        Args:
            message: The user message to send.
            system_prompt: Optional system prompt.
            history: Optional conversation history.
            tools: Optional list of tools to make available.

        Returns:
            AIResponse with the model's response.
        """
        try:
            from langchain_core.messages import AIMessage as LCAIMessage
            from langchain_core.messages import HumanMessage, SystemMessage
        except ImportError as e:
            raise ImportError(
                "LangChain is required for AI providers. "
                "Install with: pip install vendor-connectors[ai]"
            ) from e

        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        if history:
            for msg in history:
                if msg.role.value == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role.value == "assistant":
                    messages.append(LCAIMessage(content=msg.content))
                elif msg.role.value == "system":
                    messages.append(SystemMessage(content=msg.content))

        messages.append(HumanMessage(content=message))

        llm = self.llm
        if tools:
            llm = llm.bind_tools(tools)

        response = llm.invoke(messages)

        return self._convert_response(response)

    def _convert_response(self, response: Any) -> AIResponse:
        """Convert LangChain response to AIResponse.

        Args:
            response: LangChain AIMessage response.

        Returns:
            Unified AIResponse object.
        """
        content = response.content if hasattr(response, "content") else str(response)

        # Extract usage if available
        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = {
                "input_tokens": response.usage_metadata.get("input_tokens", 0),
                "output_tokens": response.usage_metadata.get("output_tokens", 0),
            }
        elif hasattr(response, "response_metadata"):
            meta = response.response_metadata
            if "usage" in meta:
                usage = {
                    "input_tokens": meta["usage"].get("input_tokens", 0),
                    "output_tokens": meta["usage"].get("output_tokens", 0),
                }

        # Extract tool calls if present
        tool_calls = None
        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_calls = [
                {
                    "id": tc.get("id", ""),
                    "name": tc.get("name", ""),
                    "args": tc.get("args", {}),
                }
                for tc in response.tool_calls
            ]

        # Get stop reason
        stop_reason = None
        if hasattr(response, "response_metadata"):
            stop_reason = response.response_metadata.get("stop_reason")

        return AIResponse(
            content=content,
            model=self.model,
            provider=self.provider_name,
            usage=usage,
            tool_calls=tool_calls,
            stop_reason=stop_reason,
            raw_response=response,
        )

    def invoke_with_tools(
        self,
        message: str,
        tools: list,
        max_iterations: int = 10,
        system_prompt: Optional[str] = None,
    ) -> AIResponse:
        """Execute chat with automatic tool calling loop.

        This creates a ReAct-style agent that can call tools and
        iterate until the task is complete.

        Args:
            message: The user message/task.
            tools: List of tools available to the agent.
            max_iterations: Maximum tool-calling iterations.
            system_prompt: Optional system prompt.

        Returns:
            AIResponse with the final result.
        """
        try:
            from langgraph.prebuilt import create_react_agent
        except ImportError as e:
            raise ImportError(
                "LangGraph is required for tool execution. "
                "Install with: pip install vendor-connectors[ai]"
            ) from e

        agent = create_react_agent(self.llm, tools)

        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("user", message))

        result = agent.invoke(
            {"messages": messages},
            {"recursion_limit": max_iterations},
        )

        # Get the last AI message from the result
        final_messages = result.get("messages", [])
        if final_messages:
            last_msg = final_messages[-1]
            return self._convert_response(last_msg)

        return AIResponse(
            content="",
            model=self.model,
            provider=self.provider_name,
        )
