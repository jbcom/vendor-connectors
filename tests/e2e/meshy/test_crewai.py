"""E2E tests for Meshy tools with CrewAI.

CrewAI supports LangChain tools via LangChainTool adapter.
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
    """E2E tests with real CrewAI agents."""

    @pytest.mark.skip(reason="Requires API keys for cassette recording")
    @pytest.mark.vcr()
    def test_crewai_agent_generates_model(
        self,
        skip_without_anthropic,
        skip_without_meshy,
        models_output_dir: Path,
    ):
        """Test CrewAI agent generating a 3D model.

        Cassette: crewai_agent_generates_model.yaml
        """
        pytest.importorskip("crewai")

        from crewai import Agent, Crew, Task
        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        langchain_tools = get_tools()
        crewai_tools = [LangChainTool(tool=t) for t in langchain_tools]

        artist = Agent(
            role="3D Artist",
            goal="Generate 3D models using Meshy AI",
            backstory="An AI assistant that creates 3D assets.",
            tools=crewai_tools,
            llm="anthropic/claude-haiku-4-5-20251001",
            verbose=True,
        )

        task = Task(
            description="Generate a 3D model of a wooden sword using text3d_generate.",
            agent=artist,
            expected_output="A dictionary with task_id, status, and model_url",
        )

        crew = Crew(agents=[artist], tasks=[task], verbose=True)
        result = crew.kickoff()

        assert result is not None
        assert "task_id" in str(result) or "model" in str(result).lower()
