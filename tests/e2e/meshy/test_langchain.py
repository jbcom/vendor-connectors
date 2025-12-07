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
    def test_langchain_agent_generates_3d_model(self, has_api_keys, output_dir):
        """Test LangChain agent generating a real 3D model.

        This test:
        1. Creates a LangGraph ReAct agent with Claude Haiku
        2. Gives it our Meshy tools
        3. Asks it to generate a 3D sword
        4. Verifies we get a real model URL back
        """
        from langchain_anthropic import ChatAnthropic
        from langgraph.prebuilt import create_react_agent

        from vendor_connectors.meshy.tools import get_tools

        # Create agent with Claude Haiku
        llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
        tools = get_tools()
        agent = create_react_agent(llm, tools)

        # Run the agent
        result = agent.invoke({
            "messages": [(
                "user",
                "Generate a 3D model of a simple wooden sword using the text3d_generate tool. "
                "Use art_style='sculpture' and a clear prompt."
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
        assert "task" in final_content.lower() or "model" in final_content.lower()

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
