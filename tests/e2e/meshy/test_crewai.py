"""E2E tests for Meshy tools with CrewAI.

Real E2E tests that hit actual APIs and record cassettes with pytest-vcr.
The test MUST download and save the GLB file to prove end-to-end functionality.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest


@pytest.fixture
def output_dir() -> Path:
    """Output directory for generated models - committed to repository.

    Path: tests/e2e/meshy/fixtures/models/
    Each connector has its own fixtures directory.
    """
    path = Path(__file__).parent / "fixtures" / "models"
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
    @pytest.mark.timeout(600)  # 10 minutes - 3D generation takes time
    def test_crewai_agent_generates_3d_model(self, has_api_keys, has_crewai, output_dir):
        """Test CrewAI agent generating a real 3D model.

        This test:
        1. Creates a CrewAI agent with Claude Haiku
        2. Wraps our LangChain tools for CrewAI
        3. Runs a Crew to generate a 3D model
        4. WAITS for completion (blocking until model is ready)
        5. Downloads and saves the GLB file to tests/e2e/fixtures/models/
        6. Verifies the GLB file exists and has content
        """
        from crewai import Agent, Crew, Task
        from crewai.tools import LangChainTool

        from vendor_connectors.meshy import base
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

        # Create task - use realistic art_style per Meshy API docs
        task = Task(
            description=(
                "Generate a 3D model of a medieval shield using the text3d_generate tool. "
                "Use art_style='realistic' and prompt='a wooden medieval shield with metal reinforcements'. "
                "Return the full result including task_id and model_url."
            ),
            agent=artist,
            expected_output="A dictionary containing task_id, status, and model_url from Meshy AI",
        )

        # Run crew - this will WAIT for completion
        crew = Crew(agents=[artist], tasks=[task], verbose=True)
        result = crew.kickoff()

        # Extract model_url from result
        result_str = str(result)
        model_url = None
        task_id = None

        # Try to find URL and task_id in result
        url_match = re.search(r'https://[^\s"\'<>]+\.glb', result_str)
        if url_match:
            model_url = url_match.group(0)
        task_match = re.search(r'task_id["\s:]+([a-f0-9-]+)', result_str, re.IGNORECASE)
        if task_match:
            task_id = task_match.group(1)

        # If not found in result string, try to parse as JSON
        if not model_url:
            try:
                data = json.loads(result_str)
                model_url = data.get("model_url")
                task_id = data.get("task_id")
            except (json.JSONDecodeError, TypeError):
                pass

        assert model_url, f"Should have model_url in result. Result: {result_str[:500]}"

        # Download the GLB file
        glb_filename = f"crewai_shield_{task_id or 'test'}.glb"
        glb_path = output_dir / glb_filename

        file_size = base.download(model_url, str(glb_path))

        # Verify the file was saved and has content
        assert glb_path.exists(), f"GLB file should exist at {glb_path}"
        assert file_size > 0, "GLB file should have content"
        assert glb_path.stat().st_size > 1000, "GLB file should be at least 1KB (real model)"

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
