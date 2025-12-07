"""E2E tests for Meshy tools with CrewAI.

Uses the reusable CrewAIRunner for framework-agnostic testing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path


class TestCrewAIToolCompatibility:
    """Unit tests for CrewAI tool compatibility."""

    def test_langchain_tools_wrap_for_crewai(self):
        """Verify LangChain tools can be wrapped for CrewAI."""
        pytest.importorskip("crewai")

        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        for tool in tools:
            crewai_tool = LangChainTool(tool=tool)
            assert crewai_tool.name == tool.name
            assert crewai_tool.description

    def test_get_crewai_tools_returns_native_tools(self):
        """Test get_crewai_tools returns CrewAI-native tools."""
        pytest.importorskip("crewai_tools")

        from vendor_connectors.meshy.tools import get_crewai_tools

        tools = get_crewai_tools()
        assert len(tools) == 8


class TestCrewAIAgentMocked:
    """Integration tests with mocked API calls."""

    def test_crewai_wrapped_tool_invocation(self):
        """Test CrewAI-wrapped tool invocation."""
        pytest.importorskip("crewai")

        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()
        text3d_tool = next(t for t in tools if t.name == "text3d_generate")
        crewai_tool = LangChainTool(tool=text3d_tool)

        mock_result = MagicMock()
        mock_result.id = "crewai_task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/model.glb"
        mock_result.thumbnail_url = None

        with patch("vendor_connectors.meshy.text3d.generate", return_value=mock_result):
            result = crewai_tool._run(prompt="a wooden shield")

        assert "crewai_task_123" in str(result)


@pytest.mark.e2e
@pytest.mark.crewai
class TestCrewAIE2E:
    """E2E tests with real CrewAI agents using reusable runner."""

    @pytest.fixture
    def runner(self):
        """Create CrewAI runner with Meshy tools."""
        pytest.importorskip("crewai")

        from tests.e2e.runners import CrewAIRunner
        from vendor_connectors.meshy.tools import get_tools

        return CrewAIRunner(
            tools=get_tools(),
            role="3D Artist",
            goal="Generate 3D models using Meshy AI",
            backstory="An AI assistant that creates 3D game assets.",
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
        """Test CrewAI agent generating a 3D model.

        Cassette: crewai_agent_generates_model.yaml
        """
        result = runner.run(
            "Generate a 3D model of a wooden sword using text3d_generate."
        )

        assert result.success
        assert "task" in result.output.lower() or "model" in result.output.lower()
