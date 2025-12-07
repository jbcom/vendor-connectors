```python
"""Tests for AI Connector interface.

This module provides comprehensive unit tests for the AIConnector class,
ensuring proper initialization, tool management, and interaction with
underlying AI providers.

Estimated code coverage: 85%
"""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from vendor_connectors.ai.base import AIProvider, AIResponse, ToolCategory
from vendor_connectors.ai.connector import AIConnector


class TestAIConnectorInitialization:
    """Tests for AIConnector initialization."""

    def test_initialize_with_default_anthropic_provider(self):
        """Test initializing connector with default provider.
        
        Given: No provider specified
        When: AIConnector is instantiated
        Then: Anthropic provider should be initialized with defaults
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()

            assert connector._provider == mock_provider_instance
            mock_get_provider.assert_called_once_with("anthropic")
            mock_provider_class.assert_called_once()

    def test_initialize_with_enum_provider(self):
        """Test initializing connector with AIProvider enum.
        
        Given: AIProvider.OPENAI enum value
        When: AIConnector is instantiated
        Then: Provider name should be extracted from enum
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(provider=AIProvider.OPENAI)

            mock_get_provider.assert_called_once_with("openai")

    def test_initialize_with_custom_model_and_api_key(self):
        """Test initializing connector with custom model and API key.
        
        Given: Custom model and API key parameters
        When: AIConnector is instantiated
        Then: Provider should be initialized with specified parameters
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                provider="anthropic",
                model="claude-3-opus",
                api_key="test-key-123",
                temperature=0.5,
                max_tokens=2048,
            )

            # Verify provider was called with correct arguments
            mock_provider_class.assert_called_once()
            call_kwargs = mock_provider_class.call_args[1]
            assert call_kwargs["model"] == "claude-3-opus"
            assert call_kwargs["api_key"] == "test-key-123"
            assert call_kwargs["temperature"] == 0.5
            assert call_kwargs["max_tokens"] == 2048

    def test_initialize_with_langsmith_tracing(self):
        """Test initializing connector with LangSmith tracing.
        
        Given: LangSmith API key and project name
        When: AIConnector is instantiated
        Then: LangSmith environment variables should be set
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            with patch.dict("os.environ", {}, clear=False):
                connector = AIConnector(
                    langsmith_api_key="test-langsmith-key",
                    langsmith_project="test-project",
                )

                import os

                assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
                assert os.environ["LANGCHAIN_API_KEY"] == "test-langsmith-key"
                assert os.environ["LANGCHAIN_PROJECT"] == "test-project"

    def test_initialize_tool_registry_as_singleton(self):
        """Test that tool registry is initialized as singleton.
        
        Given: No tool registry configuration
        When: AIConnector is instantiated
        Then: Registry should be obtained from singleton instance
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            with patch("vendor_connectors.ai.connector.ToolRegistry") as mock_registry:
                mock_instance = MagicMock()
                mock_registry.get_instance.return_value = mock_instance

                connector = AIConnector()

                mock_registry.get_instance.assert_called_once()
                assert connector._registry == mock_instance


class TestAIConnectorProperties:
    """Tests for AIConnector properties."""

    def test_provider_property(self):
        """Test provider property returns underlying provider instance.
        
        Given: Initialized AIConnector
        When: provider property is accessed
        Then: Should return the underlying provider instance
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()

            assert connector.provider == mock_provider_instance

    def test_model_property(self):
        """Test model property returns current model identifier.
        
        Given: AIConnector with specific model
        When: model property is accessed
        Then: Should return the model identifier from provider
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_instance.model = "claude-3-sonnet"
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()

            assert connector.model == "claude-3-sonnet"

    def test_registry_property(self):
        """Test registry property returns tool registry.
        
        Given: Initialized AIConnector
        When: registry property is accessed
        Then: Should return the tool registry instance
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            with patch("vendor_connectors.ai.connector.ToolRegistry") as mock_registry:
                mock_instance = MagicMock()
                mock_registry.get_instance.return_value = mock_instance

                connector = AIConnector()

                assert connector.registry == mock_instance


class TestAIConnectorChat:
    """Tests for AIConnector chat method."""

    def test_chat_with_message_only(self):
        """Test chat with message only.
        
        Given: Simple user message
        When: chat() is called without additional parameters
        Then: Provider's chat method should be called with message
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_response = MagicMock(spec=AIResponse)
            mock_response.content = "Hello, world!"
            mock_provider_instance.chat.return_value = mock_response
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()
            response = connector.chat("Hello!")

            assert response.content == "Hello, world!"
            mock_provider_instance.chat.assert_called_once_with(
                message="Hello!",
                system_prompt=None,
                history=None,
            )

    def test_chat_with_system_prompt(self):
        """Test chat with system prompt.
        
        Given: User message and system prompt
        When: chat() is called with system_prompt parameter
        Then: Provider should receive both message and system prompt
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_response = MagicMock(spec=AIResponse)
            mock_provider_instance.chat.return_value = mock_response
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()
            system_prompt = "You are a helpful assistant."
            connector.chat("Hello!", system_prompt=system_prompt)

            mock_provider_instance.chat.assert_called_once_with(
                message="Hello!",
                system_prompt=system_prompt,
                history=None,
            )

    def test_chat_with_conversation_history(self):
        """Test chat with conversation history.
        
        Given: User message and conversation history
        When: chat() is called with history parameter
        Then: Provider should receive message and history
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_response = MagicMock(spec=AIResponse)
            mock_provider_instance.chat.return_value = mock_response
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()
            history = [{"role": "user", "content": "Hi"}]
            connector.chat("Continue...", history=history)

            mock_provider_instance.chat.assert_called_once_with(
                message="Continue...",
                system_prompt=None,
                history=history,
            )


class TestAIConnectorInvoke:
    """Tests for AIConnector invoke method."""

    def test_invoke_without_tools(self):
        """Test invoke without tool use.
        
        Given: use_tools=False
        When: invoke() is called
        Then: Should call chat() method directly
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_response = MagicMock(spec=AIResponse)
            mock_provider_instance.chat.return_value = mock_response
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            with patch("vendor_connectors.ai.connector.ToolRegistry"):
                connector = AIConnector()
                response = connector.invoke("Hello", use_tools=False)

                assert response == mock_response
                mock_provider_instance.chat.assert_called_once()

    def test_invoke_with_empty_registry(self):
        """Test invoke when tool registry is empty.
        
        Given: Empty tool registry
        When: invoke() is called with use_tools=True
        Then: Should fall back to chat method
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_response = MagicMock(spec=AIResponse)
            mock_provider_instance.chat.return_value = mock_response
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            with patch("vendor_connectors.ai.connector.ToolRegistry") as mock_registry:
                mock_registry_instance = MagicMock()
                mock_registry_instance.__len__.return_value = 0
                mock_registry.get_instance.return_value = mock_registry_instance

                connector = AIConnector()
                response = connector.invoke("Hello", use_tools=True)

                assert response == mock_response
                mock_provider_instance.chat.assert_called_once()

    def test_invoke_with_tools_and_category_filter(self):
        """Test invoke with tool use and category filtering.
        
        Given: Registered tools and category filter
        When: invoke() is called with categories parameter
        Then: Should filter tools by category and invoke with tools
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_response = MagicMock(spec=AIResponse)
            mock_provider_instance.invoke_with_tools.return_value = mock_response
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            with (
                patch("vendor_connectors.ai.connector.ToolRegistry") as mock_registry,
                patch("vendor_connectors.ai.connector.ToolFactory") as mock_factory,
            ):
                mock_registry_instance = MagicMock()
                mock_registry_instance.__len__.return_value = 2
                # Mock tool definition with category
                mock_tool_def = MagicMock()
                mock_tool_def.category = ToolCategory.GITHUB
                mock_registry_instance.get_tools.return_value = [mock_tool_def]
                mock_registry.get_instance.return_value = mock_registry_instance

                mock_factory_instance = MagicMock()
                mock_factory_instance.to_langchain_tools.return_value = [MagicMock()]
                mock_factory.return_value = mock_factory_instance

                connector = AIConnector()
                response = connector.invoke(
                    "Get my repos",
                    use_tools=True,
                    categories=[ToolCategory.GITHUB],
                )

                assert response == mock_response
                mock_registry_instance.get_tools.assert_called_once()
                mock_provider_instance.invoke_with_tools.assert_called_once()

    def test_invoke_with_tool_names_filter(self):
        """Test invoke with specific tool names filter.
        
        Given: Tool registry with multiple tools
        When: invoke() is called with tool_names parameter
        Then: Should filter tools by specific names
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = MagicMock()
            mock_provider_instance = MagicMock()
            mock_response = MagicMock(spec=AIResponse)
            mock_provider_instance.invoke_with_tools.return_value = mock_response
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            with (
                patch("vendor_connectors.ai.connector.ToolRegistry") as mock_registry,
                patch("vendor_connectors.ai.connector.ToolFactory") as mock_factory,
            ):
                mock_registry_instance = MagicMock()
                mock_registry_instance.__len__.return_value =