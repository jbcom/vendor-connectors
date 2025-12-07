"""E2E tests for Meshy tools with LangChain/LangGraph.

Real E2E tests that hit actual APIs and record cassettes with pytest-vcr.
These tests take time because they wait for actual 3D model generation.

The test MUST download and save the GLB file to tests/e2e/fixtures/models/
to prove the pipeline actually works end-to-end.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest


@pytest.fixture
def output_dir() -> Path:
    """Output directory for generated models - committed to repository."""
    path = Path(__file__).parent.parent / "fixtures" / "models"
    path.mkdir(parents=True, exist_ok=True)
    return path


@pytest.mark.e2e
@pytest.mark.langchain
class TestLangChainE2E:
    """Real E2E tests with LangChain/LangGraph."""

    @pytest.fixture
    def has_deps(self):
        """Check dependencies are available."""
        pytest.importorskip("langchain_anthropic")
        pytest.importorskip("langgraph")

    @pytest.fixture
    def has_api_keys(self, has_deps):
        """Check API keys are available."""
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY required")
        if not os.environ.get("MESHY_API_KEY"):
            pytest.skip("MESHY_API_KEY required")

    @pytest.mark.vcr()
    @pytest.mark.timeout(600)  # 10 minutes - 3D generation takes time
    def test_langchain_agent_generates_3d_model(self, has_api_keys, output_dir):
        """Test LangChain agent generating a REAL 3D model end-to-end.

        This test:
        1. Creates a LangGraph ReAct agent with Claude Haiku
        2. Gives it our Meshy tools
        3. Asks it to generate a 3D sword
        4. WAITS for completion (blocking until model is ready)
        5. Downloads and saves the GLB file to tests/e2e/fixtures/models/
        6. Verifies the GLB file exists and has content
        """
        from langchain_anthropic import ChatAnthropic
        from langgraph.prebuilt import create_react_agent

        from vendor_connectors.meshy import base
        from vendor_connectors.meshy.tools import get_tools

        llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
        tools = get_tools()
        agent = create_react_agent(llm, tools)

        # Run the agent - this will wait for the model to be generated
        result = agent.invoke({
            "messages": [(
                "user",
                "Generate a 3D model of a wooden sword using text3d_generate. "
                "Use prompt='a simple wooden sword with a carved handle' and art_style='realistic'."
            )]
        })

        # Verify we got tool calls and a result
        messages = result["messages"]
        assert len(messages) > 1

        # Find the tool result containing model_url
        tool_messages = [m for m in messages if hasattr(m, "type") and m.type == "tool"]
        assert len(tool_messages) > 0, "Agent should have called text3d_generate"

        # Extract the model_url from tool results
        model_url = None
        task_id = None
        for msg in tool_messages:
            content = msg.content if hasattr(msg, "content") else str(msg)
            # Tool content may be JSON string or dict
            if isinstance(content, str):
                try:
                    data = json.loads(content)
                except json.JSONDecodeError:
                    # Try to find URL with regex
                    url_match = re.search(r'https://[^\s"\']+\.glb', content)
                    if url_match:
                        model_url = url_match.group(0)
                    task_match = re.search(r'"task_id":\s*"([^"]+)"', content)
                    if task_match:
                        task_id = task_match.group(1)
                    continue
                if isinstance(data, dict):
                    model_url = data.get("model_url") or model_url
                    task_id = data.get("task_id") or task_id
            elif isinstance(content, dict):
                model_url = content.get("model_url") or model_url
                task_id = content.get("task_id") or task_id

        assert model_url, f"Should have model_url in tool results. Messages: {tool_messages}"

        # Download the GLB file to the repository fixtures directory
        glb_filename = f"langchain_sword_{task_id or 'test'}.glb"
        glb_path = output_dir / glb_filename

        file_size = base.download(model_url, str(glb_path))

        # Verify the file was saved and has content
        assert glb_path.exists(), f"GLB file should exist at {glb_path}"
        assert file_size > 0, "GLB file should have content"
        assert glb_path.stat().st_size > 1000, "GLB file should be at least 1KB (real model)"

        # Check the final response mentions success
        final_content = str(messages[-1].content) if hasattr(messages[-1], "content") else str(messages[-1])
        assert "task" in final_content.lower() or "model" in final_content.lower() or "succeeded" in final_content.lower()

    @pytest.mark.vcr()
    @pytest.mark.timeout(60)
    def test_langchain_agent_lists_animations(self, has_api_keys):
        """Test agent listing available animations."""
        from langchain_anthropic import ChatAnthropic
        from langgraph.prebuilt import create_react_agent

        from vendor_connectors.meshy.tools import get_tools

        llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
        tools = get_tools()
        agent = create_react_agent(llm, tools)

        result = agent.invoke({
            "messages": [(
                "user",
                "List available animations using list_animations. Show me fighting animations."
            )]
        })

        messages = result["messages"]
        final_content = str(messages[-1].content) if hasattr(messages[-1], "content") else str(messages[-1])

        # Should mention animations
        assert "animation" in final_content.lower() or "fight" in final_content.lower()
