"""Tests for vendor_connectors.ai.providers.mcp module.

Tests MCP provider with mocked mcp dependencies.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest


class MockTool:
    """Mock MCP Tool type."""

    def __init__(self, name, description, inputSchema):
        self.name = name
        self.description = description
        self.inputSchema = inputSchema


class MockTextContent:
    """Mock MCP TextContent type."""

    def __init__(self, type, text):
        self.type = type
        self.text = text


class MockServer:
    """Mock MCP Server."""

    def __init__(self, name):
        self.name = name
        self._list_tools_handler = None
        self._call_tool_handler = None

    def list_tools(self):
        def decorator(func):
            self._list_tools_handler = func
            return func

        return decorator

    def call_tool(self):
        def decorator(func):
            self._call_tool_handler = func
            return func

        return decorator

    def create_initialization_options(self):
        return {}

    async def run(self, read_stream, write_stream, options):
        pass


@pytest.fixture
def mock_mcp():
    """Fixture to mock mcp module."""
    mock_types = MagicMock()
    mock_types.Tool = MockTool
    mock_types.TextContent = MockTextContent

    mock_server = MagicMock()
    mock_server.Server = MockServer

    mock_stdio = MagicMock()

    with patch.dict(
        sys.modules,
        {
            "mcp": MagicMock(),
            "mcp.types": mock_types,
            "mcp.server": mock_server,
            "mcp.server.stdio": mock_stdio,
        },
    ):
        yield


class TestMCPProviderInit:
    """Tests for MCP provider __init__ module."""

    def test_imports_core_components(self):
        """Test that core components are exported."""
        from vendor_connectors.ai.providers.mcp import (
            MCPToolProvider,
            create_server,
            run_server,
        )

        assert MCPToolProvider is not None
        assert callable(create_server)
        assert callable(run_server)

    def test_all_exports(self):
        """Test __all__ exports."""
        from vendor_connectors.ai.providers import mcp

        assert hasattr(mcp, "__all__")
        assert "MCPToolProvider" in mcp.__all__
        assert "create_server" in mcp.__all__
        assert "run_server" in mcp.__all__


class TestMCPToolProvider:
    """Tests for MCPToolProvider class."""

    def setup_method(self):
        """Reset state for each test."""
        # Reset meshy tools registration
        import vendor_connectors.ai.tools.meshy_tools as mt

        mt._tools_registered = False

        # Reset global registry
        from vendor_connectors.ai.base import _registry

        _registry._tools.clear()

        # Reset provider singleton
        import vendor_connectors.ai.providers.mcp.provider as provider_mod

        provider_mod._provider = None

    def test_provider_name(self, mock_mcp):
        """Test provider name property."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        assert provider.name == "mcp"

    def test_provider_version(self, mock_mcp):
        """Test provider version property."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        assert provider.version == "1.0.0"

    def test_provider_init(self, mock_mcp):
        """Test provider initialization."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        assert provider._server is None
        assert provider._tools == []
        assert provider._tools_by_name == {}

    def test_get_tools_returns_list(self, mock_mcp):
        """Test that get_tools returns a list."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        tools = provider.get_tools()

        assert isinstance(tools, list)

    def test_get_tools_creates_mcp_tools(self, mock_mcp):
        """Test that get_tools creates MCP tool objects."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        tools = provider.get_tools()

        # Should have created tools
        assert len(tools) > 0

        # Check tools have expected attributes
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")

    def test_get_tools_caches_results(self, mock_mcp):
        """Test that get_tools caches results."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        tools1 = provider.get_tools()
        tools2 = provider.get_tools()

        assert tools1 is tools2

    def test_get_tool_by_name(self, mock_mcp):
        """Test getting a specific tool by name."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        provider.get_tools()  # Initialize

        tool = provider.get_tool("text3d_generate")
        assert tool is not None
        assert tool.name == "text3d_generate"

    def test_get_nonexistent_tool(self, mock_mcp):
        """Test getting nonexistent tool returns None."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        provider.get_tools()  # Initialize

        tool = provider.get_tool("nonexistent")
        assert tool is None

    def test_get_tool_initializes_if_needed(self, mock_mcp):
        """Test that get_tool initializes tools if not already done."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        assert provider._tools == []

        # This should trigger initialization
        provider.get_tool("list_animations")

        assert provider._tools != []


class TestMCPServerCreation:
    """Tests for MCP server creation."""

    def setup_method(self):
        """Reset state for each test."""
        import vendor_connectors.ai.tools.meshy_tools as mt

        mt._tools_registered = False

        from vendor_connectors.ai.base import _registry

        _registry._tools.clear()

        import vendor_connectors.ai.providers.mcp.provider as provider_mod

        provider_mod._provider = None

    def test_create_server_returns_server(self, mock_mcp):
        """Test that create_server returns a server instance."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        server = provider.create_server()

        assert server is not None

    def test_create_server_registers_list_tools(self, mock_mcp):
        """Test that server has list_tools handler registered."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        server = provider.create_server()

        # MockServer stores the handler
        assert server._list_tools_handler is not None

    def test_create_server_registers_call_tool(self, mock_mcp):
        """Test that server has call_tool handler registered."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        server = provider.create_server()

        # MockServer stores the handler
        assert server._call_tool_handler is not None


class TestMCPModuleFunctions:
    """Tests for module-level convenience functions."""

    def setup_method(self):
        """Reset state for each test."""
        import vendor_connectors.ai.tools.meshy_tools as mt

        mt._tools_registered = False

        from vendor_connectors.ai.base import _registry

        _registry._tools.clear()

        import vendor_connectors.ai.providers.mcp.provider as provider_mod

        provider_mod._provider = None

    def test_create_server_function(self, mock_mcp):
        """Test module-level create_server function."""
        from vendor_connectors.ai.providers.mcp.provider import create_server

        server = create_server()
        assert server is not None

    def test_singleton_provider(self, mock_mcp):
        """Test that module functions use singleton provider."""
        from vendor_connectors.ai.providers.mcp.provider import _get_provider

        provider1 = _get_provider()
        provider2 = _get_provider()

        assert provider1 is provider2


class TestPythonTypeToJsonSchema:
    """Tests for _python_type_to_json_schema function."""

    def test_string_type(self, mock_mcp):
        """Test converting str to JSON schema type."""
        from vendor_connectors.ai.providers.mcp.provider import _python_type_to_json_schema

        assert _python_type_to_json_schema(str) == "string"

    def test_int_type(self, mock_mcp):
        """Test converting int to JSON schema type."""
        from vendor_connectors.ai.providers.mcp.provider import _python_type_to_json_schema

        assert _python_type_to_json_schema(int) == "integer"

    def test_float_type(self, mock_mcp):
        """Test converting float to JSON schema type."""
        from vendor_connectors.ai.providers.mcp.provider import _python_type_to_json_schema

        assert _python_type_to_json_schema(float) == "number"

    def test_bool_type(self, mock_mcp):
        """Test converting bool to JSON schema type."""
        from vendor_connectors.ai.providers.mcp.provider import _python_type_to_json_schema

        assert _python_type_to_json_schema(bool) == "boolean"

    def test_list_type(self, mock_mcp):
        """Test converting list to JSON schema type."""
        from vendor_connectors.ai.providers.mcp.provider import _python_type_to_json_schema

        assert _python_type_to_json_schema(list) == "array"

    def test_dict_type(self, mock_mcp):
        """Test converting dict to JSON schema type."""
        from vendor_connectors.ai.providers.mcp.provider import _python_type_to_json_schema

        assert _python_type_to_json_schema(dict) == "object"

    def test_unknown_type_defaults_to_string(self, mock_mcp):
        """Test that unknown types default to string."""
        from vendor_connectors.ai.providers.mcp.provider import _python_type_to_json_schema

        class CustomType:
            pass

        assert _python_type_to_json_schema(CustomType) == "string"


class TestMCPToolSchemaGeneration:
    """Tests for MCP tool schema generation."""

    def setup_method(self):
        """Reset state for each test."""
        import vendor_connectors.ai.tools.meshy_tools as mt

        mt._tools_registered = False

        from vendor_connectors.ai.base import _registry

        _registry._tools.clear()

    def test_tool_has_input_schema(self, mock_mcp):
        """Test that created tools have input schemas."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        tools = provider.get_tools()

        for tool in tools:
            assert tool.inputSchema is not None
            assert "type" in tool.inputSchema
            assert tool.inputSchema["type"] == "object"
            assert "properties" in tool.inputSchema

    def test_required_parameters_in_schema(self, mock_mcp):
        """Test that required parameters are marked in schema."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        tools = provider.get_tools()

        # Find text3d_generate which has required 'prompt' parameter
        text3d_tool = next((t for t in tools if t.name == "text3d_generate"), None)
        assert text3d_tool is not None

        schema = text3d_tool.inputSchema
        assert "required" in schema
        assert "prompt" in schema["required"]

    def test_optional_parameters_have_defaults(self, mock_mcp):
        """Test that optional parameters have defaults in schema."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        tools = provider.get_tools()

        text3d_tool = next((t for t in tools if t.name == "text3d_generate"), None)
        assert text3d_tool is not None

        schema = text3d_tool.inputSchema
        properties = schema["properties"]

        # art_style should have a default
        assert "art_style" in properties
        assert "default" in properties["art_style"]

    def test_enum_parameters_have_enum_values(self, mock_mcp):
        """Test that enum parameters include allowed values."""
        from vendor_connectors.ai.providers.mcp.provider import MCPToolProvider

        provider = MCPToolProvider()
        tools = provider.get_tools()

        text3d_tool = next((t for t in tools if t.name == "text3d_generate"), None)
        assert text3d_tool is not None

        schema = text3d_tool.inputSchema
        properties = schema["properties"]

        # art_style should have enum values
        assert "art_style" in properties
        assert "enum" in properties["art_style"]
        assert "realistic" in properties["art_style"]["enum"]
