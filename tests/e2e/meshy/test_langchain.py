"""E2E tests for Meshy tools with LangChain/LangGraph.

Uses the reusable LangChainRunner for framework-agnostic testing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path


class TestLangChainToolDefinitions:
    """Unit tests for LangChain tool definitions."""

    def test_tools_are_valid_structured_tools(self):
        """Verify tools are valid LangChain StructuredTools."""
        from langchain_core.tools import StructuredTool

        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        for tool in tools:
            assert isinstance(tool, StructuredTool)
            assert tool.name
            assert tool.description
            assert callable(tool.func)

    def test_tool_descriptions_are_helpful(self):
        """Verify tool descriptions help LLM understand usage."""
        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        for tool in tools:
            assert len(tool.description) > 50, f"{tool.name} description too short"

    def test_text3d_tool_requires_prompt(self):
        """Verify text3d_generate requires prompt parameter."""
        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()
        text3d_tool = next(t for t in tools if t.name == "text3d_generate")
        schema = text3d_tool.args_schema.model_json_schema()
        assert "prompt" in schema.get("required", [])


class TestLangChainAgentMocked:
    """Integration tests with mocked API calls."""

    def test_tool_invocation(self):
        """Test tool invocation with mocked backend."""
        from vendor_connectors.meshy.tools import get_tools

        mock_result = MagicMock()
        mock_result.id = "test_task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/sword.glb"
        mock_result.thumbnail_url = "https://example.com/thumb.png"

        with patch("vendor_connectors.meshy.text3d.generate", return_value=mock_result):
            tools = get_tools()
            text3d_tool = next(t for t in tools if t.name == "text3d_generate")
            result = text3d_tool.invoke({"prompt": "a medieval sword"})

        assert result["task_id"] == "test_task_123"
        assert result["status"] == "SUCCEEDED"

    def test_multi_step_workflow(self):
        """Test generate then check status workflow."""
        from vendor_connectors.meshy.tools import get_tools

        generate_result = MagicMock()
        generate_result.id = "workflow_task"
        generate_result.status.value = "PROCESSING"
        generate_result.model_urls = None
        generate_result.thumbnail_url = None

        status_result = MagicMock()
        status_result.status.value = "SUCCEEDED"
        status_result.progress = 100
        status_result.model_urls = MagicMock()
        status_result.model_urls.glb = "https://example.com/model.glb"

        tools = get_tools()
        text3d_tool = next(t for t in tools if t.name == "text3d_generate")
        status_tool = next(t for t in tools if t.name == "check_task_status")

        with patch("vendor_connectors.meshy.text3d.generate", return_value=generate_result):
            gen_result = text3d_tool.invoke({"prompt": "a shield"})

        with patch("vendor_connectors.meshy.text3d.get", return_value=status_result):
            final_result = status_tool.invoke(
                {"task_id": gen_result["task_id"], "task_type": "text-to-3d"}
            )

        assert final_result["status"] == "SUCCEEDED"


@pytest.mark.e2e
@pytest.mark.langchain
class TestLangChainE2E:
    """E2E tests with real API calls using reusable runner."""

    @pytest.fixture
    def runner(self):
        """Create LangChain runner with Meshy tools."""
        pytest.importorskip("langchain_anthropic")
        pytest.importorskip("langgraph")

        from tests.e2e.runners import LangChainRunner
        from vendor_connectors.meshy.tools import get_tools

        return LangChainRunner(tools=get_tools())

    @pytest.mark.skip(reason="Requires API keys for cassette recording")
    @pytest.mark.vcr()
    def test_agent_generates_model(
        self,
        runner,
        skip_without_anthropic,
        skip_without_meshy,
        models_output_dir: Path,
    ):
        """Test LangChain agent generating a 3D model.

        Cassette: langchain_agent_generates_model.yaml
        """
        result = runner.run(
            "Generate a 3D model of a wooden sword using text3d_generate."
        )

        assert result.success
        assert result.has_tool_call("text3d_generate") or "task" in result.output.lower()
