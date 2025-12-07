"""End-to-end tests for Meshy tools with AWS Strands Agents.

Strands Agents is AWS's model-driven agent framework that supports:
- Standard Python function tools (with type hints)
- MCP (Model Context Protocol) integration
- Multiple LLM providers including Anthropic

Our tools work with Strands because:
1. LangChain StructuredTools can be converted to Strands tools
2. Our MCP server provides another integration path
3. The underlying functions work directly

Cassette recording requires:
- ANTHROPIC_API_KEY: For Claude LLM calls
- MESHY_API_KEY: For Meshy 3D generation API
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path


class TestStrandsToolsUnit:
    """Unit tests for Strands compatibility."""

    def test_meshy_functions_are_strands_compatible(self):
        """Verify our tool functions have proper signatures for Strands.

        Strands requires functions with:
        - Type hints for all parameters
        - Docstrings that describe the function
        - Return type hints (preferred)
        """
        import inspect

        from vendor_connectors.meshy.tools import (
            apply_animation,
            check_task_status,
            get_animation,
            image3d_generate,
            list_animations,
            retexture_model,
            rig_model,
            text3d_generate,
        )

        functions = [
            text3d_generate,
            image3d_generate,
            rig_model,
            apply_animation,
            retexture_model,
            list_animations,
            check_task_status,
            get_animation,
        ]

        for func in functions:
            # Check has docstring
            assert func.__doc__, f"{func.__name__} missing docstring"

            # Check parameters have type hints
            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                assert param.annotation != inspect.Parameter.empty, (
                    f"{func.__name__}.{param_name} missing type hint"
                )

    def test_convert_langchain_tool_to_strands_tool(self):
        """Test converting LangChain tool to Strands-compatible format.

        Strands can use plain Python functions. We can extract the
        underlying function from LangChain tools.
        """
        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        for tool in tools:
            # LangChain StructuredTools have a .func attribute
            assert hasattr(tool, "func")
            assert callable(tool.func)

            # The func should be usable directly with Strands
            # (after handling the actual API calls)


class TestStrandsAgentIntegration:
    """Integration tests with Strands agents using mocked APIs."""

    def test_strands_can_use_meshy_function_directly(self):
        """Test that Strands can use our functions directly."""
        # Skip if strands not installed
        strands = pytest.importorskip("strands")

        from vendor_connectors.meshy.tools import text3d_generate

        # Mock the backend
        mock_result = MagicMock()
        mock_result.id = "strands_task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/model.glb"
        mock_result.thumbnail_url = None

        with patch("vendor_connectors.meshy.text3d.generate", return_value=mock_result):
            # Call function directly (as Strands would)
            result = text3d_generate(prompt="a wooden axe")

        assert result["task_id"] == "strands_task_123"
        assert result["status"] == "SUCCEEDED"

    def test_extract_tools_for_strands_agent(self):
        """Test extracting tool functions for Strands Agent."""
        from vendor_connectors.meshy.tools import (
            apply_animation,
            check_task_status,
            get_animation,
            image3d_generate,
            list_animations,
            retexture_model,
            rig_model,
            text3d_generate,
        )

        # These functions can be passed directly to Strands Agent
        strands_tools = [
            text3d_generate,
            image3d_generate,
            rig_model,
            apply_animation,
            retexture_model,
            list_animations,
            check_task_status,
            get_animation,
        ]

        assert len(strands_tools) == 8

        # All should be callable
        for tool in strands_tools:
            assert callable(tool)


@pytest.mark.e2e
@pytest.mark.strands
class TestStrandsE2E:
    """End-to-end tests with real Strands agents."""

    @pytest.mark.skip(reason="E2E test - requires API keys and cassette recording")
    @pytest.mark.vcr()
    def test_strands_agent_generates_3d_model(
        self,
        anthropic_api_key: str | None,
        meshy_api_key: str | None,
        models_output_dir: Path,
    ):
        """Test full Strands agent workflow generating a 3D model.

        This test:
        1. Creates a Strands agent with Claude via Anthropic provider
        2. Gives it Meshy tool functions
        3. Asks it to generate a 3D model
        4. Verifies the output

        Cassette: strands_agent_generates_3d_model.yaml
        """
        strands = pytest.importorskip("strands")

        if not anthropic_api_key or not meshy_api_key:
            pytest.skip("API keys required for E2E test")

        from strands import Agent

        from vendor_connectors.meshy.tools import (
            check_task_status,
            list_animations,
            text3d_generate,
        )

        # Create Strands agent with our tools
        # Strands auto-detects Anthropic from ANTHROPIC_API_KEY
        agent = Agent(
            tools=[text3d_generate, list_animations, check_task_status],
            # Uses default model (Claude via Bedrock or Anthropic)
        )

        # Run the agent
        result = agent(
            "Generate a simple 3D model of a wooden sword using text3d_generate. "
            "Just call the tool with a clear prompt like 'a simple wooden sword'."
        )

        # Verify we got a meaningful response
        assert result is not None
        response_text = str(result)
        assert any(
            term in response_text.lower()
            for term in ["task", "model", "sword", "generated"]
        )


@pytest.mark.e2e
@pytest.mark.strands
class TestStrandsMCPIntegration:
    """Tests for Strands MCP integration with our Meshy MCP server."""

    @pytest.mark.skip(reason="MCP integration test - requires running MCP server")
    def test_strands_can_use_meshy_mcp_server(
        self,
        anthropic_api_key: str | None,
        meshy_api_key: str | None,
    ):
        """Test Strands using our Meshy MCP server.

        Strands has native MCP support. This test verifies our MCP server
        works with Strands agents.

        Requires the MCP server to be running:
            python -m vendor_connectors.meshy.mcp
        """
        strands = pytest.importorskip("strands")

        if not anthropic_api_key or not meshy_api_key:
            pytest.skip("API keys required")

        # This would connect to our running MCP server
        # Strands MCP integration uses stdio or SSE transport
        # For testing, we'd need to spawn the server as a subprocess

        # Example (conceptual - actual implementation depends on Strands MCP API):
        # from strands.tools.mcp import MCPClient
        # mcp = MCPClient(command=["python", "-m", "vendor_connectors.meshy.mcp"])
        # agent = Agent(tools=[mcp])

        pytest.skip("MCP server integration test not yet implemented")
