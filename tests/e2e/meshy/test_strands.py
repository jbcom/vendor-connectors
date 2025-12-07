"""E2E tests for Meshy tools with AWS Strands Agents.

Strands supports Python function tools and MCP integration.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path


class TestStrandsToolCompatibility:
    """Unit tests for Strands compatibility."""

    def test_functions_have_proper_signatures(self):
        """Verify tool functions have type hints for Strands."""
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
            assert func.__doc__, f"{func.__name__} missing docstring"

            sig = inspect.signature(func)
            for param_name, param in sig.parameters.items():
                assert param.annotation != inspect.Parameter.empty, (
                    f"{func.__name__}.{param_name} missing type hint"
                )

    def test_langchain_tools_expose_underlying_functions(self):
        """Test LangChain tools expose .func for Strands."""
        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        for tool in tools:
            assert hasattr(tool, "func")
            assert callable(tool.func)


class TestStrandsAgentMocked:
    """Integration tests with mocked API calls."""

    def test_direct_function_invocation(self):
        """Test direct function call (as Strands would do)."""
        from vendor_connectors.meshy.tools import text3d_generate

        mock_result = MagicMock()
        mock_result.id = "strands_task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/model.glb"
        mock_result.thumbnail_url = None

        with patch("vendor_connectors.meshy.text3d.generate", return_value=mock_result):
            result = text3d_generate(prompt="a wooden axe")

        assert result["task_id"] == "strands_task_123"
        assert result["status"] == "SUCCEEDED"

    def test_extract_tools_for_strands(self):
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
        for tool in strands_tools:
            assert callable(tool)


@pytest.mark.e2e
@pytest.mark.strands
class TestStrandsE2E:
    """E2E tests with real Strands agents."""

    @pytest.mark.skip(reason="Requires API keys for cassette recording")
    @pytest.mark.vcr()
    def test_strands_agent_generates_model(
        self,
        skip_without_anthropic,
        skip_without_meshy,
        models_output_dir: Path,
    ):
        """Test Strands agent generating a 3D model.

        Cassette: strands_agent_generates_model.yaml
        """
        strands = pytest.importorskip("strands")

        from strands import Agent

        from vendor_connectors.meshy.tools import (
            check_task_status,
            list_animations,
            text3d_generate,
        )

        agent = Agent(
            tools=[text3d_generate, list_animations, check_task_status],
        )

        result = agent(
            "Generate a 3D model of a wooden sword using text3d_generate."
        )

        assert result is not None
        response_text = str(result)
        assert any(
            term in response_text.lower()
            for term in ["task", "model", "sword", "generated"]
        )


@pytest.mark.e2e
@pytest.mark.strands
class TestStrandsMCP:
    """Tests for Strands MCP integration."""

    @pytest.mark.skip(reason="Requires running MCP server")
    def test_strands_with_meshy_mcp_server(
        self,
        skip_without_anthropic,
        skip_without_meshy,
    ):
        """Test Strands using Meshy MCP server.

        Requires MCP server running:
            python -m vendor_connectors.meshy.mcp
        """
        pytest.skip("MCP server integration not yet implemented")
