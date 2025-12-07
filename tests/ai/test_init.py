"""Tests for vendor_connectors.ai package exports."""

from vendor_connectors.ai import ToolCategory


class TestAIPackageExports:
    """Tests for the ai package __init__ exports."""

    def test_exports_tool_category(self):
        """Test that ToolCategory is exported."""
        from vendor_connectors.ai import ToolCategory

        assert ToolCategory.MESHY == "meshy"
        assert ToolCategory.AWS == "aws"

    def test_exports_tool_definition(self):
        """Test that ToolDefinition is exported."""
        from vendor_connectors.ai import ToolDefinition

        # Verify it can be used
        definition = ToolDefinition(
            name="test",
            description="Test",
            category=ToolCategory.UTILITY,
            parameters={},
            handler=lambda: "result",
        )
        assert definition.name == "test"

    def test_exports_tool_parameter(self):
        """Test that ToolParameter is exported."""
        from vendor_connectors.ai import ToolParameter

        param = ToolParameter(
            name="test",
            description="Test param",
            type=str,
            required=True,
        )
        assert param.name == "test"

    def test_exports_tool_result(self):
        """Test that ToolResult is exported."""
        from vendor_connectors.ai import ToolResult

        result = ToolResult(success=True, data={"key": "value"})
        assert result.success is True

    def test_all_exports_are_defined(self):
        """Test that __all__ contains expected exports."""
        import vendor_connectors.ai as ai_module

        assert hasattr(ai_module, "__all__")
        expected = ["ToolCategory", "ToolDefinition", "ToolParameter", "ToolResult"]
        for name in expected:
            assert name in ai_module.__all__
            assert hasattr(ai_module, name)


class TestToolsSubpackage:
    """Tests for the ai.tools subpackage."""

    def test_meshy_tools_module_exists(self):
        """Test that meshy_tools module can be imported."""
        from vendor_connectors.ai.tools import meshy_tools

        assert hasattr(meshy_tools, "get_meshy_tools")

    def test_tools_init_exports(self):
        """Test that tools __init__ exports expected names."""
        from vendor_connectors.ai import tools

        assert "meshy_tools" in tools.__all__
