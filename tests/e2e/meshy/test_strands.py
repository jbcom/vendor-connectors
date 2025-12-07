"""E2E tests for Meshy tools with AWS Strands Agents.

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
    @pytest.mark.timeout(600)  # 10 minutes - 3D generation takes time
    def test_strands_agent_generates_3d_model(self, has_api_keys, has_strands, output_dir):
        """Test Strands agent generating a real 3D model.

        This test:
        1. Creates a Strands Agent with our tool functions
        2. Asks it to generate a 3D axe
        3. WAITS for completion (blocking until model is ready)
        4. Downloads and saves the GLB file to tests/e2e/fixtures/models/
        5. Verifies the GLB file exists and has content
        """
        from strands import Agent

        from vendor_connectors.meshy import base
        from vendor_connectors.meshy.tools import (
            check_task_status,
            list_animations,
            text3d_generate,
        )

        # Create Strands agent with our functions directly
        agent = Agent(
            system_prompt=(
                "You are a 3D asset generator. Use the tools to create 3D models. "
                "When asked to generate something, use text3d_generate with a detailed prompt. "
                "Always return the full result including task_id and model_url."
            ),
            tools=[text3d_generate, list_animations, check_task_status],
        )

        # Run the agent - use realistic art_style per Meshy API docs
        result = agent(
            "Generate a 3D model of a battle axe. "
            "Use text3d_generate with art_style='realistic' and prompt='a medieval battle axe with wooden handle and steel blade'."
        )

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
        glb_filename = f"strands_axe_{task_id or 'test'}.glb"
        glb_path = output_dir / glb_filename

        file_size = base.download(model_url, str(glb_path))

        # Verify the file was saved and has content
        assert glb_path.exists(), f"GLB file should exist at {glb_path}"
        assert file_size > 0, "GLB file should have content"
        assert glb_path.stat().st_size > 1000, "GLB file should be at least 1KB (real model)"

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
