"""E2E tests for Meshy tools with AWS Strands Agents.

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
@pytest.mark.strands
class TestStrandsE2E:
    """Real E2E tests with AWS Strands Agents."""

    @pytest.fixture
    def has_api_keys(self):
        """Check API keys are available."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY required")
        if not os.environ.get("MESHY_API_KEY"):
            pytest.skip("MESHY_API_KEY required")

    @pytest.fixture
    def has_strands(self):
        """Check Strands is installed."""
        pytest.importorskip("strands")

    @pytest.mark.vcr()
    def test_strands_agent_generates_3d_model(self, has_api_keys, has_strands, output_dir):
        """Test Strands agent generating a real 3D model.

        This test:
        1. Creates a Strands Agent with our tool functions
        2. Asks it to generate a 3D sword
        3. Verifies we get a real result
        """
        from strands import Agent

        from vendor_connectors.meshy.tools import (
            check_task_status,
            list_animations,
            text3d_generate,
        )

        # Create Strands agent with our functions directly
        agent = Agent(
            system_prompt=(
                "You are a 3D asset generator. Use the tools to create 3D models. "
                "When asked to generate something, use text3d_generate with a detailed prompt."
            ),
            tools=[text3d_generate, list_animations, check_task_status],
        )

        # Run the agent
        result = agent(
            "Generate a 3D model of a simple wooden sword. "
            "Use text3d_generate with art_style='sculpture' and a clear prompt."
        )

        # Verify result
        result_str = str(result)
        assert "task" in result_str.lower() or "model" in result_str.lower() or "sword" in result_str.lower()

    @pytest.mark.vcr()
    def test_strands_agent_lists_animations(self, has_api_keys, has_strands):
        """Test Strands agent listing animations."""
        from strands import Agent

        from vendor_connectors.meshy.tools import list_animations

        agent = Agent(
            system_prompt="You help users find animations. Use list_animations to search the catalog.",
            tools=[list_animations],
        )

        result = agent("List fighting animations using list_animations with category='Fighting'.")

        result_str = str(result)
        assert "animation" in result_str.lower() or "fight" in result_str.lower()


@pytest.mark.e2e
@pytest.mark.strands
class TestStrandsWithBedrock:
    """E2E tests with Strands using AWS Bedrock."""

    @pytest.fixture
    def has_bedrock(self):
        """Check Bedrock credentials are available."""
        # Bedrock uses AWS credentials
        if not (os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE")):
            pytest.skip("AWS credentials required for Bedrock")
        if not os.environ.get("MESHY_API_KEY"):
            pytest.skip("MESHY_API_KEY required")

    @pytest.fixture
    def has_strands(self):
        """Check Strands is installed."""
        pytest.importorskip("strands")

    @pytest.mark.vcr()
    def test_strands_bedrock_generates_model(self, has_bedrock, has_strands):
        """Test Strands with Bedrock model generating a 3D model."""
        from strands import Agent
        from strands.models import BedrockModel

        from vendor_connectors.meshy.tools import text3d_generate

        # Use Claude via Bedrock
        model = BedrockModel(model_id="anthropic.claude-3-haiku-20240307-v1:0")

        agent = Agent(
            model=model,
            system_prompt="You are a 3D asset generator. Use text3d_generate to create models.",
            tools=[text3d_generate],
        )

        result = agent("Generate a 3D wooden sword using text3d_generate.")

        result_str = str(result)
        assert "task" in result_str.lower() or "model" in result_str.lower()
