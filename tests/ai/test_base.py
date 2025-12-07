"""Tests for vendor_connectors.ai.base module.

Tests core types and registry functionality without requiring optional dependencies.
"""

import json
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from vendor_connectors.ai.base import (
    BaseToolProvider,
    ParameterDefinition,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolRegistry,
    ToolResult,
    get_tool_definition,
    get_tool_definitions,
    register_tool,
)


class TestToolCategory:
    """Tests for ToolCategory enum."""

    def test_vendor_categories(self):
        """Test vendor connector categories exist."""
        assert ToolCategory.AWS == "aws"
        assert ToolCategory.GITHUB == "github"
        assert ToolCategory.SLACK == "slack"
        assert ToolCategory.VAULT == "vault"
        assert ToolCategory.GOOGLE_CLOUD == "google_cloud"
        assert ToolCategory.ZOOM == "zoom"
        assert ToolCategory.MESHY == "meshy"
        assert ToolCategory.CURSOR == "cursor"
        assert ToolCategory.ANTHROPIC == "anthropic"

    def test_meshy_subcategories(self):
        """Test Meshy-specific subcategories exist."""
        assert ToolCategory.GENERATION == "generation"
        assert ToolCategory.RIGGING == "rigging"
        assert ToolCategory.ANIMATION == "animation"
        assert ToolCategory.TEXTURING == "texturing"
        assert ToolCategory.UTILITY == "utility"

    def test_category_is_string_enum(self):
        """Test that ToolCategory inherits from str."""
        assert isinstance(ToolCategory.AWS, str)
        assert ToolCategory.AWS == "aws"
        # Value can be used as string
        assert ToolCategory.MESHY.value == "meshy"


class TestToolParameter:
    """Tests for ToolParameter dataclass."""

    def test_required_parameter(self):
        """Test creating a required parameter."""
        param = ToolParameter(
            name="prompt",
            description="The text prompt",
            type=str,
            required=True,
        )
        assert param.name == "prompt"
        assert param.description == "The text prompt"
        assert param.type is str
        assert param.required is True
        assert param.default is None
        assert param.enum_values is None

    def test_optional_parameter_with_default(self):
        """Test creating an optional parameter with default."""
        param = ToolParameter(
            name="limit",
            description="Maximum results",
            type=int,
            required=False,
            default=50,
        )
        assert param.name == "limit"
        assert param.required is False
        assert param.default == 50

    def test_parameter_with_enum_values(self):
        """Test creating parameter with enum constraints."""
        param = ToolParameter(
            name="style",
            description="Art style",
            type=str,
            required=False,
            default="realistic",
            enum_values=["realistic", "cartoon", "low-poly"],
        )
        assert param.enum_values == ["realistic", "cartoon", "low-poly"]
        assert param.default == "realistic"

    def test_different_types(self):
        """Test parameters with different Python types."""
        int_param = ToolParameter(name="count", description="Count", type=int)
        assert int_param.type is int

        bool_param = ToolParameter(name="enabled", description="Enabled", type=bool)
        assert bool_param.type is bool

        float_param = ToolParameter(name="ratio", description="Ratio", type=float)
        assert float_param.type is float

    def test_parameter_definition_alias(self):
        """Test that ParameterDefinition is an alias for ToolParameter."""
        assert ParameterDefinition is ToolParameter


class TestToolDefinition:
    """Tests for ToolDefinition dataclass."""

    def test_basic_tool_definition(self):
        """Test creating a basic tool definition."""

        def sample_handler(prompt: str) -> str:
            return f"Generated: {prompt}"

        definition = ToolDefinition(
            name="test_tool",
            description="A test tool",
            category=ToolCategory.MESHY,
            parameters={
                "prompt": ToolParameter(
                    name="prompt",
                    description="The prompt",
                    type=str,
                    required=True,
                ),
            },
            handler=sample_handler,
        )

        assert definition.name == "test_tool"
        assert definition.description == "A test tool"
        assert definition.category == ToolCategory.MESHY
        assert "prompt" in definition.parameters
        assert definition.handler is sample_handler
        assert definition.requires_api_key is True  # default
        assert definition.connector_class is None  # default
        assert definition.method_name is None  # default

    def test_tool_definition_with_optional_fields(self):
        """Test tool definition with optional fields."""

        class MockConnector:
            pass

        definition = ToolDefinition(
            name="connector_tool",
            description="Tool from connector",
            category=ToolCategory.AWS,
            parameters={},
            handler=lambda: "result",
            requires_api_key=False,
            connector_class=MockConnector,
            method_name="do_something",
        )

        assert definition.requires_api_key is False
        assert definition.connector_class is MockConnector
        assert definition.method_name == "do_something"

    def test_tool_handler_is_callable(self):
        """Test that tool handler can be called."""

        def handler(x: int, y: int) -> str:
            return str(x + y)

        definition = ToolDefinition(
            name="add_tool",
            description="Adds numbers",
            category=ToolCategory.UTILITY,
            parameters={},
            handler=handler,
        )

        result = definition.handler(2, 3)
        assert result == "5"


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_success_result(self):
        """Test creating a successful result."""
        result = ToolResult(
            success=True,
            data={"id": "abc123", "status": "completed"},
            task_id="abc123",
        )
        assert result.success is True
        assert result.data == {"id": "abc123", "status": "completed"}
        assert result.error is None
        assert result.task_id == "abc123"

    def test_error_result(self):
        """Test creating an error result."""
        result = ToolResult(
            success=False,
            error="API key not provided",
        )
        assert result.success is False
        assert result.error == "API key not provided"
        assert result.data == {}

    def test_to_json(self):
        """Test JSON serialization."""
        result = ToolResult(
            success=True,
            data={"count": 10},
            task_id="task_123",
        )
        json_str = result.to_json()
        parsed = json.loads(json_str)

        assert parsed["success"] is True
        assert parsed["data"]["count"] == 10
        assert parsed["task_id"] == "task_123"
        assert parsed["error"] is None

    def test_to_json_error(self):
        """Test JSON serialization of error result."""
        result = ToolResult(success=False, error="Something failed")
        json_str = result.to_json()
        parsed = json.loads(json_str)

        assert parsed["success"] is False
        assert parsed["error"] == "Something failed"

    def test_default_data_is_empty_dict(self):
        """Test that default data is an empty dict, not shared."""
        result1 = ToolResult(success=True)
        result2 = ToolResult(success=True)

        result1.data["key"] = "value"

        assert "key" not in result2.data  # Verify no shared state


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def setup_method(self):
        """Create a fresh registry for each test."""
        self.registry = ToolRegistry()

    def _create_test_definition(self, name: str, category: ToolCategory = ToolCategory.UTILITY):
        """Helper to create test tool definitions."""
        return ToolDefinition(
            name=name,
            description=f"Test tool: {name}",
            category=category,
            parameters={},
            handler=lambda: "result",
        )

    def test_register_and_get(self):
        """Test registering and retrieving a tool."""
        definition = self._create_test_definition("my_tool")
        self.registry.register(definition)

        retrieved = self.registry.get("my_tool")
        assert retrieved is definition

    def test_get_nonexistent_returns_none(self):
        """Test getting a nonexistent tool returns None."""
        result = self.registry.get("nonexistent")
        assert result is None

    def test_get_all(self):
        """Test getting all registered tools."""
        tool1 = self._create_test_definition("tool1")
        tool2 = self._create_test_definition("tool2")

        self.registry.register(tool1)
        self.registry.register(tool2)

        all_tools = self.registry.get_all()
        assert len(all_tools) == 2
        names = {t.name for t in all_tools}
        assert names == {"tool1", "tool2"}

    def test_thread_safety(self):
        """Test that registry is thread-safe."""
        results = []
        errors = []

        def register_tool(i):
            try:
                definition = self._create_test_definition(f"thread_tool_{i}")
                self.registry.register(definition)
                results.append(i)
            except Exception as e:
                errors.append(e)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(register_tool, i) for i in range(100)]
            for f in futures:
                f.result()

        assert len(errors) == 0
        assert len(results) == 100
        assert len(self.registry.get_all()) == 100


class TestGlobalRegistryFunctions:
    """Tests for global registry functions."""

    def test_register_tool_function(self):
        """Test the register_tool convenience function."""

        def handler() -> str:
            return "result"

        # Create unique name to avoid collisions with other tests
        import uuid

        unique_name = f"global_test_tool_{uuid.uuid4().hex[:8]}"

        definition = ToolDefinition(
            name=unique_name,
            description="Global test",
            category=ToolCategory.UTILITY,
            parameters={},
            handler=handler,
        )

        register_tool(definition)
        retrieved = get_tool_definition(unique_name)

        assert retrieved is not None
        assert retrieved.name == unique_name

    def test_get_tool_definitions_returns_list(self):
        """Test that get_tool_definitions returns a list."""
        definitions = get_tool_definitions()
        assert isinstance(definitions, list)


class TestBaseToolProvider:
    """Tests for BaseToolProvider abstract base class."""

    def test_cannot_instantiate_directly(self):
        """Test that BaseToolProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseToolProvider()

    def test_concrete_implementation(self):
        """Test creating a concrete implementation."""

        class MockTool:
            def __init__(self, name: str):
                self.name = name

        class ConcreteProvider(BaseToolProvider):
            def __init__(self):
                self._tools = [MockTool("tool1"), MockTool("tool2")]

            @property
            def name(self) -> str:
                return "mock"

            @property
            def version(self) -> str:
                return "1.0.0"

            def get_tools(self):
                return self._tools

            def get_tool(self, name: str):
                for tool in self._tools:
                    if tool.name == name:
                        return tool
                return None

        provider = ConcreteProvider()
        assert provider.name == "mock"
        assert provider.version == "1.0.0"
        assert len(provider.get_tools()) == 2
        assert provider.get_tool("tool1") is not None
        assert provider.get_tool("nonexistent") is None

    def test_list_tools_default_implementation(self):
        """Test the default list_tools implementation."""

        class MockTool:
            def __init__(self, name: str):
                self.name = name

        class ConcreteProvider(BaseToolProvider):
            @property
            def name(self) -> str:
                return "mock"

            @property
            def version(self) -> str:
                return "1.0.0"

            def get_tools(self):
                return [MockTool("tool_a"), MockTool("tool_b")]

            def get_tool(self, name: str):
                return None

        provider = ConcreteProvider()
        tool_names = provider.list_tools()
        assert tool_names == ["tool_a", "tool_b"]
