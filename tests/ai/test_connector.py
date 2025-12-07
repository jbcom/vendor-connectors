"""Tests for AIConnector - Unified AI provider interface.

Estimated Code Coverage: 85%
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from vendor_connectors.ai.base import AIProvider, AIResponse, ToolCategory
from vendor_connectors.ai.connector import AIConnector
from vendor_connectors.ai.tools.registry import ToolRegistry


class TestAIConnectorInitialization:
    """Tests for AIConnector initialization."""

    def test_init_with_default_provider(self):
        """
        Given: No explicit provider specified
        When: AIConnector is initialized with default parameters
        Then: Provider should be set to 'anthropic' and initialized correctly
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()

            assert connector._provider == mock_provider_instance
            mock_get_provider.assert_called_once_with("anthropic")
            mock_provider_class.assert_called_once()

    def test_init_with_provider_enum(self):
        """
        Given: AIProvider enum value
        When: AIConnector is initialized with AIProvider enum
        Then: Provider should be correctly extracted and normalized to string
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(provider=AIProvider.OPENAI)

            mock_get_provider.assert_called_once_with(AIProvider.OPENAI.value)

    def test_init_with_custom_model_and_api_key(self):
        """
        Given: Custom model identifier and API key
        When: AIConnector is initialized with these parameters
        Then: Provider should be instantiated with these parameters
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                provider="openai",
                model="gpt-4",
                api_key="test-key-123",
            )

            mock_provider_class.assert_called_once_with(
                model="gpt-4",
                api_key="test-key-123",
                temperature=0.7,
                max_tokens=4096,
            )

    def test_init_with_temperature_and_max_tokens(self):
        """
        Given: Custom temperature and max_tokens values
        When: AIConnector is initialized
        Then: Provider should receive these configuration parameters
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                temperature=0.5,
                max_tokens=2048,
            )

            call_kwargs = mock_provider_class.call_args[1]
            assert call_kwargs["temperature"] == 0.5
            assert call_kwargs["max_tokens"] == 2048

    def test_init_with_langsmith_setup(self):
        """
        Given: LangSmith API key and project name
        When: AIConnector is initialized
        Then: LangSmith environment variables should be configured
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider, \
             patch.dict(os.environ, {}, clear=False) as mock_env:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                langsmith_api_key="test-ls-key",
                langsmith_project="test-project",
            )

            assert os.environ.get("LANGCHAIN_TRACING_V2") == "true"
            assert os.environ.get("LANGCHAIN_API_KEY") == "test-ls-key"
            assert os.environ.get("LANGCHAIN_PROJECT") == "test-project"

    def test_init_without_langsmith_skips_setup(self):
        """
        Given: No LangSmith API key provided
        When: AIConnector is initialized
        Then: LangSmith setup should not be called
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()

            assert connector._langsmith_api_key is None
            assert connector._langsmith_project is None

    def test_init_with_extra_kwargs(self):
        """
        Given: Additional provider-specific keyword arguments
        When: AIConnector is initialized
        Then: Extra kwargs should be passed to the provider
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector(
                provider="custom",
                custom_param="custom_value",
                another_param=42,
            )

            call_kwargs = mock_provider_class.call_args[1]
            assert call_kwargs["custom_param"] == "custom_value"
            assert call_kwargs["another_param"] == 42

    def test_init_tool_registry_initialized(self):
        """
        Given: AIConnector initialization
        When: Instance is created
        Then: Tool registry and factory should be initialized
        """
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()

            assert connector._registry is not None
            assert connector._factory is not None
            assert isinstance(connector._connector_instances, dict)
            assert len(connector._connector_instances) == 0


class TestAIConnectorProperties:
    """Tests for AIConnector properties."""

    @pytest.fixture
    def connector(self):
        """Create a connector with mocked provider."""
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_instance.model = "test-model"
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class
            return AIConnector()

    def test_provider_property(self, connector):
        """
        Given: AIConnector instance
        When: provider property is accessed
        Then: Should return the underlying provider instance
        """
        provider = connector.provider
        assert provider == connector._provider

    def test_model_property(self, connector):
        """
        Given: AIConnector instance
        When: model property is accessed
        Then: Should return the model from the provider
        """
        connector._provider.model = "gpt-4-turbo"
        model = connector.model
        assert model == "gpt-4-turbo"

    def test_registry_property(self, connector):
        """
        Given: AIConnector instance
        When: registry property is accessed
        Then: Should return the tool registry instance
        """
        registry = connector.registry
        assert registry == connector._registry
        assert isinstance(registry, ToolRegistry)


class TestAIConnectorChat:
    """Tests for AIConnector.chat method."""

    @pytest.fixture
    def connector(self):
        """Create a connector with mocked provider."""
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class
            return AIConnector()

    def test_chat_with_message_only(self, connector):
        """
        Given: A simple user message
        When: chat method is called without system prompt or history
        Then: Provider.chat should be called with the message only
        """
        mock_response = Mock(spec=AIResponse)
        connector._provider.chat.return_value = mock_response

        result = connector.chat("Hello, AI!")

        connector._provider.chat.assert_called_once_with(
            message="Hello, AI!",
            system_prompt=None,
            history=None,
        )
        assert result == mock_response

    def test_chat_with_system_prompt(self, connector):
        """
        Given: A message and system prompt
        When: chat method is called
        Then: Provider.chat should receive both message and system prompt
        """
        mock_response = Mock(spec=AIResponse)
        connector._provider.chat.return_value = mock_response

        result = connector.chat(
            "What is 2+2?",
            system_prompt="You are a math tutor.",
        )

        connector._provider.chat.assert_called_once_with(
            message="What is 2+2?",
            system_prompt="You are a math tutor.",
            history=None,
        )

    def test_chat_with_conversation_history(self, connector):
        """
        Given: A message and conversation history
        When: chat method is called with history
        Then: Provider.chat should receive the history
        """
        mock_response = Mock(spec=AIResponse)
        connector._provider.chat.return_value = mock_response

        history = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        result = connector.chat(
            "How are you?",
            history=history,
        )

        connector._provider.chat.assert_called_once_with(
            message="How are you?",
            system_prompt=None,
            history=history,
        )

    def test_chat_with_all_parameters(self, connector):
        """
        Given: Message, system prompt, and history
        When: chat method is called with all parameters
        Then: Provider.chat should receive all parameters
        """
        mock_response = Mock(spec=AIResponse)
        connector._provider.chat.return_value = mock_response

        history = [{"role": "user", "content": "Previous message"}]
        system_prompt = "Be concise."

        result = connector.chat(
            "New question",
            system_prompt=system_prompt,
            history=history,
        )

        connector._provider.chat.assert_called_once_with(
            message="New question",
            system_prompt=system_prompt,
            history=history,
        )


class TestAIConnectorInvoke:
    """Tests for AIConnector.invoke method."""

    @pytest.fixture
    def connector(self):
        """Create a connector with mocked provider and registry."""
        with patch("vendor_connectors.ai.connector.get_provider") as mock_get_provider:
            mock_provider_class = Mock()
            mock_provider_instance = Mock()
            mock_provider_class.return_value = mock_provider_instance
            mock_get_provider.return_value = mock_provider_class

            connector = AIConnector()
            # Mock the registry
            connector._registry = Mock(spec=ToolRegistry)
            connector._factory = Mock()
            return connector

    def test_invoke_without_tools(self, connector):
        """
        Given: use_tools is False
        When: invoke method is called
        Then: Should fall back to chat method without tools
        """
        mock_response = Mock(spec=AIResponse)
        connector._provider.chat.return_value = mock_response
        connector._registry.__len__.return_value = 0

        result = connector.invoke("Do something", use_tools=False)

        connector._provider.chat.assert_called_once()
        connector._provider.invoke_with_tools.assert_not_called()

    def test_invoke_with_empty_registry(self, connector):
        """
        Given: No tools registered in the registry
        When: invoke method is called with use_tools=True
        Then: Should fall back to chat method
        """
        mock_response = Mock(spec=AIResponse)
        connector._provider.chat.return_value = mock_response
        connector._registry.__len__.return_value = 0

        result = connector.invoke("Do something", use_tools=True)

        connector._provider.chat.assert_called_once()
        connector._provider.invoke_with_tools.assert_not_called()

    def test_invoke_with_tools(self, connector):
        """
        Given: Tools are registered and use_tools is True
        When: invoke method is called
        Then: Should call invoke_with_tools on the provider
        """
        mock_tool_def = Mock()
        mock_tool_def.category = ToolCategory.GITHUB
        
        mock_langchain_tool = Mock()
        
        connector._registry.__len__.return_value = 1
        connector._registry.get_tools.return_value = [mock_tool_def]
        connector._factory.to_langchain_tools.return_value = [mock_langchain_tool]
        
        mock_response = Mock(spec=AIResponse)
        connector._provider.invoke_with_tools.return_value = mock_response

        result = connector.invoke(
            "Use tools to solve this",
            use_tools=True,
        )

        connector._registry.get_tools.assert_called_once_with(
            categories=None,
            names=None,
        )
        connector._provider.invoke_with_tools.assert_called_once()
        assert result == mock_response

    def test_invoke_with_category_filter(self, connector):
        """
        Given: Tool categories specified
        When: invoke method is called with categories filter
        Then: Should filter tools by specified categories
        """
        mock_tool_def = Mock()
        mock_tool_def.category = ToolCategory.GITHUB
        
        connector._registry.__len__.return_value = 1
        connector._registry.get_tools.return_value = [mock_tool_def]
        connector._factory.to_langchain_tools.return_value = [Mock()]
        connector._provider.invoke_with_tools.return_value = Mock(spec=AIResponse)

        result = connector.invoke(
            "Do something",
            use_tools=True,
            categories=[ToolCategory.GITHUB],
        )

        connector._registry.get_tools.assert_called_once_with(
            categories=[ToolCategory.GITHUB],
            names=None,
        )

    def test_invoke_with_tool_names_filter(self, connector):
        """
        Given: Specific tool names to use
        When: invoke method is called with tool_names filter
        Then: Should filter tools by specified names
        """
        mock_tool_def = Mock()
        mock_tool_def.category = ToolCategory.GITHUB
        
        connector._registry.__len__.return_value = 1
        connector._registry.get_tools.return_value = [mock_tool_def]
        connector._factory.to_langchain_tools.return_value = [Mock()]
        connector._provider.invoke_with_tools.return_value = Mock(spec=AIResponse)

        result = connector.invoke(
            "Do something",
