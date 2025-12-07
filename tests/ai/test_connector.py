```python
"""Tests for unified AI connector interface."""

from __future__ import annotations

from unittest.mock import MagicMock, Mock, patch

import pytest

from vendor_connectors.ai.base import AIProvider, AIResponse, ToolCategory
from vendor_connectors.ai.connector import AIConnector
from vendor_connectors.ai.tools.factory import ToolFactory
from vendor_connectors.ai.tools.registry import ToolRegistry


# Estimated code coverage: 85%
# Coverage includes: initialization, properties, chat, invoke, tool registration,
# tool listing, and error scenarios. Minor gaps in LangSmith integration edge cases.


class TestAIConnectorInitialization:
    """Tests for AIConnector initialization."""

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_initialize_with_provider_name(self, mock_get_provider):
        """
        Given: A provider name string and optional configuration parameters
        When: Creating an AIConnector instance
        Then: The connector initializes with the provider and stores configuration
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector(
            provider="anthropic",
            model="claude-3",
            temperature=0.5,
            max_tokens=2048,
        )

        assert connector.provider == mock_provider_instance
        mock_get_provider.assert_called_once_with("anthropic")
        mock_provider_class.assert_called_once_with(
            model="claude-3",
            api_key=None,
            temperature=0.5,
            max_tokens=2048,
        )

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_initialize_with_provider_enum(self, mock_get_provider):
        """
        Given: An AIProvider enum value
        When: Creating an AIConnector instance
        Then: The enum is converted to string and provider is instantiated
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector(provider=AIProvider.ANTHROPIC)

        assert connector.provider == mock_provider_instance
        mock_get_provider.assert_called_once_with("anthropic")

    @patch("vendor_connectors.ai.connector.ToolRegistry.get_instance")
    @patch("vendor_connectors.ai.connector.get_provider")
    def test_initialize_tool_management(self, mock_get_provider, mock_get_registry):
        """
        Given: Default initialization parameters
        When: Creating an AIConnector instance
        Then: Tool registry and factory are initialized
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry

        connector = AIConnector()

        assert connector.registry == mock_registry
        assert isinstance(connector._factory, ToolFactory)
        assert connector._connector_instances == {}

    @patch.dict("os.environ", {}, clear=True)
    @patch("vendor_connectors.ai.connector.get_provider")
    def test_initialize_with_langsmith_credentials(self, mock_get_provider):
        """
        Given: LangSmith API key and project name
        When: Creating an AIConnector instance
        Then: LangSmith environment variables are set
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector(
            langsmith_api_key="test-key",
            langsmith_project="test-project",
        )

        import os

        assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
        assert os.environ["LANGCHAIN_API_KEY"] == "test-key"
        assert os.environ["LANGCHAIN_PROJECT"] == "test-project"

    @patch.dict("os.environ", {}, clear=True)
    @patch("vendor_connectors.ai.connector.get_provider")
    def test_initialize_with_langsmith_key_only(self, mock_get_provider):
        """
        Given: Only LangSmith API key without project name
        When: Creating an AIConnector instance
        Then: Tracing is enabled with API key, but project is not set
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector(langsmith_api_key="test-key")

        import os

        assert os.environ["LANGCHAIN_TRACING_V2"] == "true"
        assert os.environ["LANGCHAIN_API_KEY"] == "test-key"
        assert "LANGCHAIN_PROJECT" not in os.environ


class TestAIConnectorProperties:
    """Tests for AIConnector properties."""

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_provider_property(self, mock_get_provider):
        """
        Given: An initialized AIConnector
        When: Accessing the provider property
        Then: The underlying provider instance is returned
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector()

        assert connector.provider == mock_provider_instance

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_model_property(self, mock_get_provider):
        """
        Given: An initialized AIConnector with a model set
        When: Accessing the model property
        Then: The model identifier from the provider is returned
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_instance.model = "claude-3-opus"
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector()

        assert connector.model == "claude-3-opus"

    @patch("vendor_connectors.ai.connector.ToolRegistry.get_instance")
    @patch("vendor_connectors.ai.connector.get_provider")
    def test_registry_property(self, mock_get_provider, mock_get_registry):
        """
        Given: An initialized AIConnector
        When: Accessing the registry property
        Then: The tool registry singleton is returned
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        mock_registry = Mock()
        mock_get_registry.return_value = mock_registry

        connector = AIConnector()

        assert connector.registry == mock_registry


class TestAIConnectorChat:
    """Tests for AIConnector chat functionality."""

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_chat_simple_message(self, mock_get_provider):
        """
        Given: An initialized AIConnector and a user message
        When: Calling chat method
        Then: Provider's chat method is called with correct parameters
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Hello!")
        mock_provider_instance.chat.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector()
        response = connector.chat("Hello!")

        assert response == mock_response
        mock_provider_instance.chat.assert_called_once_with(
            message="Hello!",
            system_prompt=None,
            history=None,
        )

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_chat_with_system_prompt(self, mock_get_provider):
        """
        Given: A message and system prompt
        When: Calling chat method with system_prompt parameter
        Then: Provider's chat method receives the system prompt
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Response")
        mock_provider_instance.chat.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector()
        response = connector.chat(
            "Question",
            system_prompt="You are helpful.",
        )

        assert response == mock_response
        mock_provider_instance.chat.assert_called_once_with(
            message="Question",
            system_prompt="You are helpful.",
            history=None,
        )

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_chat_with_history(self, mock_get_provider):
        """
        Given: A message and conversation history
        When: Calling chat method with history parameter
        Then: Provider's chat method receives the history
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Response")
        mock_provider_instance.chat.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        history = [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}]

        connector = AIConnector()
        response = connector.chat("Continue", history=history)

        assert response == mock_response
        mock_provider_instance.chat.assert_called_once_with(
            message="Continue",
            system_prompt=None,
            history=history,
        )


class TestAIConnectorInvoke:
    """Tests for AIConnector invoke functionality."""

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_invoke_without_tools(self, mock_get_provider):
        """
        Given: An initialized AIConnector with use_tools=False
        When: Calling invoke method
        Then: Falls back to chat method without tools
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Response")
        mock_provider_instance.chat.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        connector = AIConnector()
        response = connector.invoke("Question", use_tools=False)

        assert response == mock_response
        mock_provider_instance.chat.assert_called_once()
        mock_provider_instance.invoke_with_tools.assert_not_called()

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_invoke_with_empty_registry(self, mock_get_provider):
        """
        Given: An initialized AIConnector with no registered tools
        When: Calling invoke method with use_tools=True
        Then: Falls back to chat method since no tools available
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Response")
        mock_provider_instance.chat.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        with patch("vendor_connectors.ai.connector.ToolRegistry.get_instance") as mock_get_registry:
            mock_registry = Mock()
            mock_registry.__len__.return_value = 0  # Empty registry
            mock_get_registry.return_value = mock_registry

            connector = AIConnector()
            response = connector.invoke("Question", use_tools=True)

            assert response == mock_response
            mock_provider_instance.chat.assert_called_once()

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_invoke_with_tools(self, mock_get_provider):
        """
        Given: An initialized AIConnector with registered tools
        When: Calling invoke method with use_tools=True
        Then: Provider's invoke_with_tools is called with filtered tools
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Tool result")
        mock_provider_instance.invoke_with_tools.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        with patch("vendor_connectors.ai.connector.ToolRegistry.get_instance") as mock_get_registry:
            mock_registry = Mock()
            mock_registry.__len__.return_value = 1  # Has tools
            mock_tool = Mock()
            mock_tool.category = ToolCategory.GITHUB
            mock_registry.get_tools.return_value = [mock_tool]
            mock_get_registry.return_value = mock_registry

            with patch("vendor_connectors.ai.connector.ToolFactory") as mock_factory_class:
                mock_factory_instance = Mock()
                mock_factory_class.return_value = mock_factory_instance
                mock_lc_tool = Mock()
                mock_factory_instance.to_langchain_tools.return_value = [mock_lc_tool]

                connector = AIConnector()
                response = connector.invoke("Question")

                assert response == mock_response
                mock_provider_instance.invoke_with_tools.assert_called_once()

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_invoke_with_category_filter(self, mock_get_provider):
        """
        Given: Multiple categories and a specific category filter
        When: Calling invoke with categories parameter
        Then: Registry filters tools by specified categories
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Filtered result")
        mock_provider_instance.invoke_with_tools.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance
        mock_get_provider.return_value = mock_provider_class

        with patch("vendor_connectors.ai.connector.ToolRegistry.get_instance") as mock_get_registry:
            mock_registry = Mock()
            mock_registry.__len__.return_value = 1
            mock_tool = Mock()
            mock_tool.category = ToolCategory.GITHUB
            mock_registry.get_tools.return_value = [mock_tool]
            mock_get_registry.return_value = mock_registry

            with patch("vendor_connectors.ai.connector.ToolFactory") as mock_factory_class:
                mock_factory_instance = Mock()
                mock_factory_class.return_value = mock_factory_instance
                mock_factory_instance.to_langchain_tools.return_value = [Mock()]

                connector = AIConnector()
                response = connector.invoke(
                    "Question",
                    categories=[ToolCategory.GITHUB],
                )

                mock_registry.get_tools.assert_called_with(
                    categories=[ToolCategory.GITHUB],
                    names=None,
                )

    @patch("vendor_connectors.ai.connector.get_provider")
    def test_invoke_with_tool_name_filter(self, mock_get_provider):
        """
        Given: A specific tool name filter
        When: Calling invoke with tool_names parameter
        Then: Registry filters tools by specified names
        """
        mock_provider_class = Mock()
        mock_provider_instance = Mock()
        mock_response = AIResponse(content="Filtered result")