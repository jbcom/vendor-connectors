"""E2E tests for Meshy tools with CrewAI.

Real E2E tests that hit actual APIs and record cassettes with pytest-vcr.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture
def output_dir() -> Path:
    """Output directory for generated models."""
    path = Path(__file__).parent.parent / "fixtures" / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.mark.e2e
@pytest.mark.crewai
class TestCrewAIE2E:
    """Real E2E tests with CrewAI."""

    @pytest.fixture
    def has_api_keys(self):
        """Check API keys are available."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY required")
        if not os.environ.get("MESHY_API_KEY"):
            pytest.skip("MESHY_API_KEY required")

    @pytest.fixture
    def has_crewai(self):
        """Check CrewAI is installed."""
        pytest.importorskip("crewai")

    @pytest.mark.vcr()
    def test_crewai_agent_generates_3d_model(self, has_api_keys, has_crewai, output_dir):
        """Test CrewAI agent generating a real 3D model.

        This test:
        1. Creates a CrewAI agent with Claude Haiku
        2. Wraps our LangChain tools for CrewAI
        3. Runs a Crew to generate a 3D model
        4. Verifies we get a real result
        """
        from crewai import Agent, Crew, Task
        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        # Wrap our tools for CrewAI
        langchain_tools = get_tools()
        crewai_tools = [LangChainTool(tool=t) for t in langchain_tools]

        # Create agent
        artist = Agent(
            role="3D Artist",
            goal="Generate 3D models using Meshy AI tools",
            backstory="An AI assistant that creates 3D game assets using Meshy AI.",
            tools=crewai_tools,
            llm="anthropic/claude-haiku-4-5-20251001",
            verbose=True,
        )

        # Create task
        task = Task(
            description=(
                "Generate a 3D model of a simple wooden sword using the text3d_generate tool. "
                "Use art_style='sculpture' and provide a clear, detailed prompt."
            ),
            agent=artist,
            expected_output="A dictionary containing task_id, status, and model_url from Meshy AI",
        )

        # Run crew
        crew = Crew(agents=[artist], tasks=[task], verbose=True)
        result = crew.kickoff()

        # Verify result
        result_str = str(result)
        assert "task" in result_str.lower() or "model" in result_str.lower()

    @pytest.mark.vcr()
    def test_crewai_agent_lists_animations(self, has_api_keys, has_crewai):
        """Test CrewAI agent listing animations."""
        from crewai import Agent, Crew, Task
        from crewai.tools import LangChainTool

        from vendor_connectors.meshy.tools import get_tools

        langchain_tools = get_tools()
        # Only include the list_animations tool for this test
        list_anim_tool = next(t for t in langchain_tools if t.name == "list_animations")
        crewai_tools = [LangChainTool(tool=list_anim_tool)]

        agent = Agent(
            role="Animation Researcher",
            goal="Find available animations in the Meshy catalog",
            backstory="An AI that researches animation options.",
            tools=crewai_tools,
            llm="anthropic/claude-haiku-4-5-20251001",
            verbose=True,
        )

        task = Task(
            description="List available fighting animations using list_animations with category='Fighting'.",
            agent=agent,
            expected_output="A list of fighting animations with their IDs and names",
        )

        crew = Crew(agents=[agent], tasks=[task], verbose=True)
        result = crew.kickoff()

        result_str = str(result)
        assert "animation" in result_str.lower() or "fight" in result_str.lower()
