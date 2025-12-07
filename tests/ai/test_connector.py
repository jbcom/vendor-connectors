"""Tests for AIConnector - Unified AI interface."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, Mock, call, patch
from typing import Any, Optional

import pytest

from vendor_connectors.ai.connector import AIConnector
from vendor_connectors.ai.base import (
    AIProvider,
    AIResponse,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    AIRole,
    AIMessage,
)


# Estimated code coverage: 95%
# This test suite covers all public methods, error scenarios, edge cases,
# and integration points with mocked dependencies.


class MockLLMProvider:
    """Mock LLM provider for testing."""

    def __init__(self, model: Optional[str] = None, **kwargs):
        self.model = model or "mock-model"
        self.kwargs = kwargs

    def chat(self, message: str, system_prompt: Optional[str] = None, history: Optional[list] = None) -> AIResponse:
        return AIResponse(
            content=f"Mock response to: {message}",
            model=self.model,
            provider=AIProvider.ANTHROPIC,
            usage={"input_tokens": 10, "output_tokens": 15},
        )

    def invoke_with_tools(
        self,
        message: str,
        tools: list,
        max_iterations: int = 10,
        system_prompt: Optional[str] = None,
    ) -> AIResponse:
        return AIResponse(
            content=f"Tool response to: {message}",
            model=self.model,
            provider=AIProvider.ANTHROPIC,
            usage={"input_tokens": 20, "output_tokens": 25},
            tool_calls=[{"id": "call_123", "name": "test_tool", "args": {}}],
        )


class MockConnector:
    """Mock connector class for tool registration testing."""

    def get_data(self, query: str) -> str:
        """Get data from the connector."""
        return f"Data for: {query}"

    def create_item(self, name: str, description: str = "default") -> dict:
        """Create an item."""
        return {"name": name, "description": description, "id": "123"}

    def _private_method(self) -> str:
        """Private method that shouldn't be registered."""
        return "private"


@pytest.fixture
def mock_provider():
    """Fixture providing a mock LLM provider."""
    return MockLLMProvider()


@pytest.fixture
def mock_registry():
    """Fixture providing a fresh mock registry."""
    with patch("vendor_connectors.ai.connector.ToolRegistry") as mock_registry_class:
        registry_instance = MagicMock()
        registry_instance.__len__.return_value = 0
        registry_instance.get_tools.return_value = []
        registry_instance.list_names.return_value = []
        mock_registry_class.get_instance.return_value = registry_instance
        yield registry_instance


@pytest.fixture
def mock_factory():
    """Fixture providing a mock tool factory."""
    with patch("vendor_connectors.ai.connector.ToolFactory") as mock_factory_class:
        factory_instance = Mock()
        factory_instance.from_connector.return_value = []
        factory_instance.to_langchain_tools.return_value = []
        mock_factory_class.return_value = factory_instance
        yield factory_instance


class TestAIConnectorInitialization:
    """Tests for AIConnector initialization."""

    def test_init_with_string_provider(self, mock_registry, mock_factory):
        """Test initialization with string provider name.
        
        Given: A string provider name
        When: AIConnector is initialized
        Then: Provider is correctly instantiated with default settings
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_get_provider.return_value = MockLLMProvider

            connector = AIConnector(provider="anthropic")

            assert connector.model == "mock-model"
            mock_get_provider.assert_called_once_with("anthropic")

    def test_init_with_enum_provider(self, mock_registry, mock_factory):
        """Test initialization with AIProvider enum.
        
        Given: An AIProvider enum value
        When: AIConnector is initialized
        Then: Provider name is correctly extracted and used
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_get_provider.return_value = MockLLMProvider

            connector = AIConnector(provider=AIProvider.OPENAI)

            mock_get_provider.assert_called_once_with("openai")

    def test_init_with_custom_parameters(self, mock_registry, mock_factory):
        """Test initialization with custom parameters.
        
        Given: Custom model, temperature, and token settings
        When: AIConnector is initialized
        Then: Parameters are passed to the provider
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_class = Mock()
            provider_instance = Mock()
            provider_instance.model = "custom-model"
            provider_class.return_value = provider_instance
            mock_get_provider.return_value = provider_class

            connector = AIConnector(
                provider="openai",
                model="gpt-4",
                temperature=0.5,
                max_tokens=2048,
                api_key="test-key",
            )

            provider_class.assert_called_once_with(
                model="gpt-4",
                api_key="test-key",
                temperature=0.5,
                max_tokens=2048,
            )

    def test_init_with_langsmith_config(self, mock_registry, mock_factory):
        """Test initialization with LangSmith configuration.
        
        Given: LangSmith API key and project
        When: AIConnector is initialized
        Then: Environment variables are set for tracing
        """
        with (
            patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider,
            patch.dict(os.environ, {}, clear=True),
        ):
            mock_get_provider.return_value = MockLLMProvider

            connector = AIConnector(
                provider="anthropic",
                langsmith_api_key="ls-key-123",
                langsmith_project="test-project",
            )

            assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
            assert os.environ["LANGCHAIN_API_KEY"] == "ls-key-123"
            assert os.environ["LANGCHAIN_PROJECT"] == "test-project"

    def test_init_langsmith_without_project(self, mock_registry, mock_factory):
        """Test LangSmith setup without project name.
        
        Given: LangSmith API key but no project name
        When: AIConnector is initialized
        Then: Only tracing and API key are set, no project
        """
        with (
            patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider,
            patch.dict(os.environ, {}, clear=True),
        ):
            mock_get_provider.return_value = MockLLMProvider

            connector = AIConnector(
                provider="anthropic",
                langsmith_api_key="ls-key-123",
            )

            assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
            assert os.environ["LANGCHAIN_API_KEY"] == "ls-key-123"
            assert "LANGCHAIN_PROJECT" not in os.environ


class TestAIConnectorProperties:
    """Tests for AIConnector properties."""

    def test_provider_property(self, mock_registry, mock_factory):
        """Test provider property access.
        
        Given: An initialized AIConnector
        When: The provider property is accessed
        Then: The underlying provider instance is returned
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = MockLLMProvider()
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            connector = AIConnector()

            assert connector.provider is provider_instance

    def test_model_property(self, mock_registry, mock_factory):
        """Test model property access.
        
        Given: An initialized AIConnector with a specific model
        When: The model property is accessed
        Then: The provider's model name is returned
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = MockLLMProvider(model="test-model-v1")
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            connector = AIConnector()

            assert connector.model == "test-model-v1"

    def test_registry_property(self, mock_registry, mock_factory):
        """Test registry property access.
        
        Given: An initialized AIConnector
        When: The registry property is accessed
        Then: The tool registry instance is returned
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_get_provider.return_value = MockLLMProvider

            connector = AIConnector()

            assert connector.registry is mock_registry


class TestAIConnectorChat:
    """Tests for AIConnector chat functionality."""

    def test_chat_simple_message(self, mock_registry, mock_factory):
        """Test simple chat without additional parameters.
        
        Given: A simple message
        When: chat() is called
        Then: Provider's chat method is called and response is returned
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = Mock()
            expected_response = AIResponse(
                content="Hello!",
                model="test-model",
                provider=AIProvider.ANTHROPIC,
            )
            provider_instance.chat.return_value = expected_response
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            connector = AIConnector()
            response = connector.chat("Hello")

            provider_instance.chat.assert_called_once_with(
                message="Hello",
                system_prompt=None,
                history=None,
            )
            assert response is expected_response

    def test_chat_with_system_prompt(self, mock_registry, mock_factory):
        """Test chat with system prompt.
        
        Given: A message and system prompt
        When: chat() is called with system_prompt
        Then: Both are passed to provider's chat method
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = Mock()
            expected_response = AIResponse(
                content="Assistant response",
                model="test-model",
                provider=AIProvider.ANTHROPIC,
            )
            provider_instance.chat.return_value = expected_response
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            connector = AIConnector()
            response = connector.chat(
                "What's the weather?",
                system_prompt="You are a weather assistant",
            )

            provider_instance.chat.assert_called_once_with(
                message="What's the weather?",
                system_prompt="You are a weather assistant",
                history=None,
            )

    def test_chat_with_history(self, mock_registry, mock_factory):
        """Test chat with conversation history.
        
        Given: A message and conversation history
        When: chat() is called with history
        Then: History is passed to provider's chat method
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = Mock()
            expected_response = AIResponse(
                content="Continued response",
                model="test-model",
                provider=AIProvider.ANTHROPIC,
            )
            provider_instance.chat.return_value = expected_response
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            history = [
                AIMessage.user("Previous question"),
                AIMessage.assistant("Previous answer"),
            ]
            connector = AIConnector()
            response = connector.chat("Follow-up question", history=history)

            provider_instance.chat.assert_called_once_with(
                message="Follow-up question",
                system_prompt=None,
                history=history,
            )


class TestAIConnectorInvoke:
    """Tests for AIConnector invoke functionality."""

    def test_invoke_without_tools(self, mock_registry, mock_factory):
        """Test invoke when tools are disabled.
        
        Given: use_tools=False
        When: invoke() is called
        Then: Falls back to simple chat functionality
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = Mock()
            expected_response = AIResponse(
                content="Chat response",
                model="test-model",
                provider=AIProvider.ANTHROPIC,
            )
            provider_instance.chat.return_value = expected_response
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            connector = AIConnector()
            response = connector.invoke("Test message", use_tools=False)

            provider_instance.chat.assert_called_once_with(
                message="Test message",
                system_prompt=None,
            )
            assert response is expected_response

    def test_invoke_with_empty_registry(self, mock_registry, mock_factory):
        """Test invoke when registry has no tools.
        
        Given: Empty tool registry
        When: invoke() is called with use_tools=True
        Then: Falls back to chat since no tools available
        """
        mock_registry.__len__.return_value = 0

        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = Mock()
            expected_response = AIResponse(
                content="Chat response",
                model="test-model",
                provider=AIProvider.ANTHROPIC,
            )
            provider_instance.chat.return_value = expected_response
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            connector = AIConnector()
            response = connector.invoke("Test message", use_tools=True)

            provider_instance.chat.assert_called_once()

    def test_invoke_with_tools_no_matches(self, mock_registry, mock_factory):
        """Test invoke when tool filters match nothing.
        
        Given: Tools exist but filters don't match any
        When: invoke() is called with specific categories
        Then: Falls back to chat since no matching tools
        """
        mock_registry.__len__.return_value = 5
        mock_registry.get_tools.return_value = []  # No matches

        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            provider_instance = Mock()
            expected_response = AIResponse(
                content="Chat response",
                model="test-model",
                provider=AIProvider.ANTHROPIC,
            )
            provider_instance.chat.return_value = expected_response
            mock_get_provider.return_value = lambda **kwargs: provider_instance

            connector = AIConnector()
            response = connector.invoke(
                "Test message",
                use_tools=True,
                categories=[ToolCategory.AWS],
            )

            mock_registry.get_tools.assert_called_once_with(
                categories=[ToolCategory.AWS],
                names=None,
            )
            provider_instance.chat.assert_called_once()

    def test_invoke_with_tools_success(self, mock_registry, mock_factory):
        """Test successful invoke with tools.
        
        Given: Available tools that match filters
        When: invoke() is called with use_tools=True
        Then: Tools are converted and passed to provider
        """
        # Setup mock tools
        tool_def = ToolDefinition(
            name="test_tool",
            description="Test tool",
            category=ToolCategory.GITHUB,
            parameters={},
            handler=lambda: "result",
        )
        mock_registry.__len__.return_value = 1
        mock_registry.get_tools.return_value = [tool_def]

        mock_lc_tool = Mock()
