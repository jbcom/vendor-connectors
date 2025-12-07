"""E2E tests for Meshy tools with AWS Strands Agents.

Uses the reusable StrandsRunner for framework-agnostic testing.
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

    def test_extract_functions_from_langchain_tools(self):
        """Test extracting functions from LangChain tools for Strands."""
        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        # Extract underlying functions (what StrandsRunner does)
        functions = [tool.func for tool in tools]

        assert len(functions) == 8
        for func in functions:
            assert callable(func)


@pytest.mark.e2e
@pytest.mark.strands
class TestStrandsE2E:
    """E2E tests with real Strands agents using reusable runner."""

    @pytest.fixture
    def runner(self):
        """Create Strands runner with Meshy tools."""
        pytest.importorskip("strands")

        from tests.e2e.runners import StrandsRunner
        from vendor_connectors.meshy.tools import (
            check_task_status,
            list_animations,
            text3d_generate,
        )

        # Strands uses functions directly, not LangChain tools
        return StrandsRunner(
            tools=[text3d_generate, list_animations, check_task_status],
        )

    @pytest.mark.skip(reason="Requires API keys for cassette recording")
    @pytest.mark.vcr()
    def test_agent_generates_model(
        self,
        runner,
        skip_without_anthropic,
        skip_without_meshy,
        models_output_dir: Path,
    ):
        """Test Strands agent generating a 3D model.

        Cassette: strands_agent_generates_model.yaml
        """
        result = runner.run(
            "Generate a 3D model of a wooden sword using text3d_generate."
        )

        assert result.success
        assert any(
            term in result.output.lower()
            for term in ["task", "model", "sword", "generated"]
        )
