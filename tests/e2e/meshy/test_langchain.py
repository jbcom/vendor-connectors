"""E2E tests for Meshy tools with LangChain/LangGraph.

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
    @pytest.mark.timeout(120)  # 2 minutes for API calls
    def test_langchain_agent_generates_3d_model(self, has_api_keys, output_dir):
        """Test LangChain agent starting a real 3D model generation task.

        This test:
        1. Creates a LangGraph ReAct agent with Claude Haiku
        2. Gives it our Meshy tools
        3. Asks it to start generating a 3D sword (doesn't wait for completion)
        4. Verifies we get a task_id back
        """
        from langchain_anthropic import ChatAnthropic
        from langgraph.prebuilt import create_react_agent

        from vendor_connectors.meshy.tools import check_task_status, list_animations

        # Use only non-blocking tools for this test
        # text3d_generate uses wait=True by default which takes too long
        # Instead, we'll test list_animations which is fast
        from langchain_core.tools import StructuredTool

        def text3d_generate_nowait(
            prompt: str,
            art_style: str = "realistic",
        ) -> dict:
            """Generate a 3D model (non-blocking)."""
            from vendor_connectors.meshy import text3d
            result = text3d.generate(prompt, art_style=art_style, wait=False)
            return {"task_id": result, "status": "pending", "message": "Task submitted"}

        tools = [
            StructuredTool.from_function(
                func=text3d_generate_nowait,
                name="text3d_generate",
                description="Generate a 3D model from text. Returns task_id immediately.",
            ),
            StructuredTool.from_function(func=check_task_status, name="check_task_status", description="Check task status"),
            StructuredTool.from_function(func=list_animations, name="list_animations", description="List animations"),
        ]

        llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
        agent = create_react_agent(llm, tools)

        # Run the agent
        result = agent.invoke({
            "messages": [(
                "user",
                "Generate a 3D model of a simple wooden sword using text3d_generate. "
                "Use art_style='realistic' and prompt='a simple wooden sword'."
            )]
        })

        # Verify we got tool calls and a result
        messages = result["messages"]
        assert len(messages) > 1

        # Find the tool result
        tool_messages = [m for m in messages if hasattr(m, "type") and m.type == "tool"]
        assert len(tool_messages) > 0, "Agent should have called text3d_generate"

        # Check for task_id in the result
        final_content = str(messages[-1].content) if hasattr(messages[-1], "content") else str(messages[-1])
        assert "task" in final_content.lower() or "pending" in final_content.lower()

    @pytest.mark.vcr()
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
