"""Tests for vendor_connectors.ai.providers.crewai module.

Tests CrewAI provider with mocked crewai dependencies.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


class MockBaseTool:
    """Mock CrewAI BaseTool for testing."""

    def __init__(self):
        pass


@pytest.fixture
def mock_crewai():
    """Fixture to mock crewai module."""
    mock_module = MagicMock()
    mock_tools_module = MagicMock()
    mock_tools_module.BaseTool = MockBaseTool

    with patch.dict(
        sys.modules,
        {
            "crewai": mock_module,
            "crewai.tools": mock_tools_module,
        },
    ):
        yield mock_module


class TestCrewAIProviderInit:
    """Tests for CrewAI provider __init__ module."""

    def test_imports_core_components(self):
        """Test that core components are exported."""
        from vendor_connectors.ai.providers.crewai import (
            CrewAIToolProvider,
            get_tool,
            get_tools,
        )

        assert CrewAIToolProvider is not None
        assert callable(get_tools)
        assert callable(get_tool)

    def test_all_exports(self):
        """Test __all__ exports."""
        from vendor_connectors.ai.providers import crewai

        assert hasattr(crewai, "__all__")
        # Core exports
        assert "CrewAIToolProvider" in crewai.__all__
        assert "get_tools" in crewai.__all__
        assert "get_tool" in crewai.__all__
        # Lazy-loaded tool classes
        assert "Text3DGenerateTool" in crewai.__all__

    def test_lazy_tool_class_loading(self, mock_crewai):
        """Test that tool classes are lazily loaded."""
        # Reset any cached state
        import vendor_connectors.ai.providers.crewai as crewai_module

        crewai_module._tool_classes = {}

        # Accessing a tool class should trigger lazy loading
        from vendor_connectors.ai.providers.crewai import __getattr__

        # This should not raise - it uses lazy loading
        try:
            _ = __getattr__("Text3DGenerateTool")
            # May be None if registration hasn't happened
        except AttributeError:
            pass

    def test_unknown_attribute_raises(self):
        """Test that accessing unknown attribute raises AttributeError."""
        from vendor_connectors.ai.providers import crewai

        with pytest.raises(AttributeError, match="has no attribute"):
            _ = crewai.NonExistentThing


class TestCrewAIToolProvider:
    """Tests for CrewAIToolProvider class."""

    def setup_method(self):
        """Reset state for each test."""
        # Reset meshy tools registration
        import vendor_connectors.ai.tools.meshy_tools as mt

        mt._tools_registered = False

        # Reset global registry
        from vendor_connectors.ai.base import _registry

        _registry._tools.clear()

        # Reset provider singleton
        import vendor_connectors.ai.providers.crewai.provider as provider_mod

        provider_mod._provider = None

    def test_provider_name(self, mock_crewai):
        """Test provider name property."""
        from vendor_connectors.ai.providers.crewai.provider import CrewAIToolProvider

        provider = CrewAIToolProvider()
        assert provider.name == "crewai"

    def test_provider_version(self, mock_crewai):
        """Test provider version property."""
        from vendor_connectors.ai.providers.crewai.provider import CrewAIToolProvider

        provider = CrewAIToolProvider()
        assert provider.version == "1.0.0"

    def test_provider_init(self, mock_crewai):
        """Test provider initialization."""
        from vendor_connectors.ai.providers.crewai.provider import CrewAIToolProvider

        provider = CrewAIToolProvider()
        assert provider._tool_classes == {}
        assert provider._tool_instances == {}

    def test_get_tools_creates_tool_classes(self, mock_crewai):
        """Test that get_tools creates tool classes."""
        from vendor_connectors.ai.providers.crewai.provider import CrewAIToolProvider

        provider = CrewAIToolProvider()
        provider.get_tools()

        # Should have created tools
        assert len(provider._tool_classes) > 0

    def test_get_tool_by_name(self, mock_crewai):
        """Test getting a specific tool by name."""
        from vendor_connectors.ai.providers.crewai.provider import CrewAIToolProvider

        provider = CrewAIToolProvider()

        # First get all tools to ensure they're created
        provider.get_tools()

        # Now get specific tool - just verify it doesn't raise
        provider.get_tool("text3d_generate")

    def test_get_nonexistent_tool(self, mock_crewai):
        """Test getting a nonexistent tool returns None."""
        from vendor_connectors.ai.providers.crewai.provider import CrewAIToolProvider

        provider = CrewAIToolProvider()
        provider.get_tools()  # Initialize tools

        tool = provider.get_tool("nonexistent_tool")
        assert tool is None

    def test_get_tool_class(self, mock_crewai):
        """Test getting tool class (not instance)."""
        from vendor_connectors.ai.providers.crewai.provider import CrewAIToolProvider

        provider = CrewAIToolProvider()
        provider.get_tools()  # Initialize tools

        # Should be able to get the class - just verify it doesn't raise
        provider.get_tool_class("text3d_generate")


class TestCrewAIModuleFunctions:
    """Tests for module-level convenience functions."""

    def setup_method(self):
        """Reset state for each test."""
        import vendor_connectors.ai.tools.meshy_tools as mt

        mt._tools_registered = False

        from vendor_connectors.ai.base import _registry

        _registry._tools.clear()

        import vendor_connectors.ai.providers.crewai.provider as provider_mod

        provider_mod._provider = None

    def test_get_tools_function(self, mock_crewai):
        """Test module-level get_tools function."""
        from vendor_connectors.ai.providers.crewai.provider import get_tools

        tools = get_tools()
        assert isinstance(tools, list)

    def test_get_tool_function(self, mock_crewai):
        """Test module-level get_tool function."""
        from vendor_connectors.ai.providers.crewai.provider import get_tool, get_tools

        # Initialize
        get_tools()

        # Get specific tool - just verify it doesn't raise
        get_tool("list_animations")

    def test_singleton_provider(self, mock_crewai):
        """Test that module functions use singleton provider."""
        from vendor_connectors.ai.providers.crewai.provider import _get_provider

        provider1 = _get_provider()
        provider2 = _get_provider()

        assert provider1 is provider2


class TestPydanticModelCreation:
    """Tests for Pydantic model creation from tool definitions."""

    def test_create_pydantic_model_basic(self, mock_crewai):
        """Test creating basic Pydantic model."""
        from vendor_connectors.ai.base import ToolCategory, ToolDefinition, ToolParameter
        from vendor_connectors.ai.providers.crewai.provider import _create_pydantic_model

        definition = ToolDefinition(
            name="test_tool",
            description="Test",
            category=ToolCategory.UTILITY,
            parameters={
                "name": ToolParameter(
                    name="name",
                    description="The name",
                    type=str,
                    required=True,
                ),
            },
            handler=lambda name: name,
        )

        model = _create_pydantic_model(definition)

        # Check model was created
        assert model is not None
        assert "Input" in model.__name__

    def test_create_pydantic_model_with_optional(self, mock_crewai):
        """Test creating Pydantic model with optional fields."""
        from vendor_connectors.ai.base import ToolCategory, ToolDefinition, ToolParameter
        from vendor_connectors.ai.providers.crewai.provider import _create_pydantic_model

        definition = ToolDefinition(
            name="optional_tool",
            description="Test with optional",
            category=ToolCategory.UTILITY,
            parameters={
                "required_field": ToolParameter(
                    name="required_field",
                    description="Required",
                    type=str,
                    required=True,
                ),
                "optional_field": ToolParameter(
                    name="optional_field",
                    description="Optional",
                    type=int,
                    required=False,
                    default=42,
                ),
            },
            handler=lambda **kwargs: str(kwargs),
        )

        model = _create_pydantic_model(definition)
        assert model is not None


class TestToolClassCreation:
    """Tests for CrewAI tool class creation."""

    def test_create_tool_class(self, mock_crewai):
        """Test creating a CrewAI tool class from definition."""
        from vendor_connectors.ai.base import ToolCategory, ToolDefinition, ToolParameter
        from vendor_connectors.ai.providers.crewai.provider import _create_tool_class

        def handler(prompt: str) -> str:
            return f"Handled: {prompt}"

        definition = ToolDefinition(
            name="create_test",
            description="Test tool creation",
            category=ToolCategory.UTILITY,
            parameters={
                "prompt": ToolParameter(
                    name="prompt",
                    description="The prompt",
                    type=str,
                    required=True,
                ),
            },
            handler=handler,
        )

        tool_class = _create_tool_class(definition)

        # Check class attributes
        assert tool_class.name == "create_test"
        assert tool_class.description == "Test tool creation"

    def test_tool_class_run_calls_handler(self, mock_crewai):
        """Test that tool _run method calls the handler."""
        from vendor_connectors.ai.base import ToolCategory, ToolDefinition, ToolParameter
        from vendor_connectors.ai.providers.crewai.provider import _create_tool_class

        call_log = []

        def handler(value: str) -> str:
            call_log.append(value)
            return f"Result: {value}"

        definition = ToolDefinition(
            name="run_test",
            description="Test running",
            category=ToolCategory.UTILITY,
            parameters={
                "value": ToolParameter(
                    name="value",
                    description="Value",
                    type=str,
                    required=True,
                ),
            },
            handler=handler,
        )

        tool_class = _create_tool_class(definition)
        tool_instance = tool_class()

        # Call _run
        result = tool_instance._run(value="test_input")

        assert "test_input" in call_log
        assert result == "Result: test_input"
