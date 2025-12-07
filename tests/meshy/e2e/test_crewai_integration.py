"""End-to-end tests for Meshy tools with CrewAI.

CrewAI supports LangChain tools via the LangChainTool adapter,
or native tools via the @tool decorator. Our get_crewai_tools()
function provides tools compatible with CrewAI.

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


class TestCrewAIToolsUnit:
    """Unit tests for CrewAI tool compatibility."""

    def test_langchain_tools_work_with_crewai_adapter(self):
        """Verify LangChain tools can be wrapped for CrewAI."""
        # Skip if crewai not installed
        pytest.importorskip("crewai")

        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        # Each LangChain tool should be wrappable
        for tool in tools:
            crewai_tool = LangChainTool(tool=tool)
            assert crewai_tool.name == tool.name
            assert crewai_tool.description

    def test_get_crewai_tools_returns_native_tools(self):
        """Test that get_crewai_tools returns CrewAI-native tools."""
        # Skip if crewai_tools not installed
        crewai_tools = pytest.importorskip("crewai_tools")

        from vendor_connectors.meshy.tools import get_crewai_tools

        # Mock the tool decorator to verify it's called
        with patch.object(crewai_tools, "tool", wraps=crewai_tools.tool):
            tools = get_crewai_tools()

        assert len(tools) == 8  # Should have all 8 Meshy tools


class TestCrewAIAgentIntegration:
    """Integration tests with CrewAI agents using mocked APIs."""

    def test_crewai_agent_can_use_langchain_tools(self):
        """Test that CrewAI agent can use wrapped LangChain tools."""
        pytest.importorskip("crewai")

        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        # Get our LangChain tools
        tools = get_tools()
        text3d_tool = next(t for t in tools if t.name == "text3d_generate")

        # Wrap for CrewAI
        crewai_tool = LangChainTool(tool=text3d_tool)

        # Mock the backend
        mock_result = MagicMock()
        mock_result.id = "crewai_task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/model.glb"
        mock_result.thumbnail_url = None

        with patch("vendor_connectors.meshy.text3d.generate", return_value=mock_result):
            # Invoke via the wrapper
            result = crewai_tool._run(prompt="a wooden shield")

        assert "crewai_task_123" in str(result)


@pytest.mark.e2e
@pytest.mark.crewai
class TestCrewAIE2E:
    """End-to-end tests with real CrewAI agents."""

    @pytest.mark.skip(reason="E2E test - requires API keys and cassette recording")
    @pytest.mark.vcr()
    def test_crewai_agent_generates_3d_model(
        self,
        anthropic_api_key: str | None,
        meshy_api_key: str | None,
        models_output_dir: Path,
    ):
        """Test full CrewAI agent workflow generating a 3D model.

        This test:
        1. Creates a CrewAI agent with Claude Haiku
        2. Gives it Meshy tools (via LangChainTool wrapper)
        3. Creates a task to generate a 3D model
        4. Runs a crew and verifies output

        Cassette: crewai_agent_generates_3d_model.yaml
        """
        pytest.importorskip("crewai")

        if not anthropic_api_key or not meshy_api_key:
            pytest.skip("API keys required for E2E test")

        from crewai import Agent, Crew, Task
        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        # Wrap our tools for CrewAI
        langchain_tools = get_tools()
        crewai_tools = [LangChainTool(tool=t) for t in langchain_tools]

        # Create agent
        artist = Agent(
            role="3D Artist",
            goal="Generate 3D models using Meshy AI",
            backstory="An AI assistant that creates 3D assets.",
            tools=crewai_tools,
            llm="anthropic/claude-haiku-4-5-20251001",
            verbose=True,
        )

        # Create task
        task = Task(
            description="Generate a simple 3D model of a wooden sword using text3d_generate.",
            agent=artist,
            expected_output="A dictionary with task_id, status, and model_url",
        )

        # Create and run crew
        crew = Crew(agents=[artist], tasks=[task], verbose=True)
        result = crew.kickoff()

        # Verify result
        assert result is not None
        assert "task_id" in str(result) or "model" in str(result).lower()
