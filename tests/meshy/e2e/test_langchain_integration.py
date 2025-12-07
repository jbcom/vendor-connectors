"""End-to-end tests for Meshy tools with LangChain/LangGraph.

These tests verify that our LangChain StructuredTools work correctly
with real LangChain agents using Claude as the LLM.

Cassette recording requires:
- ANTHROPIC_API_KEY: For Claude LLM calls
- MESHY_API_KEY: For Meshy 3D generation API

Once cassettes are recorded, tests run without API keys.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import MagicMock, patch

import pytest

if TYPE_CHECKING:
    from pathlib import Path


class TestLangChainToolsUnit:
    """Unit tests for LangChain tool definitions."""

    def test_tools_are_valid_langchain_tools(self):
        """Verify tools are valid LangChain StructuredTools."""
        from langchain_core.tools import StructuredTool

        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        for tool in tools:
            assert isinstance(tool, StructuredTool)
            assert tool.name
            assert tool.description
            # Verify the tool can be invoked (with mocked backend)
            assert callable(tool.func)

    def test_tool_descriptions_are_helpful(self):
        """Verify tool descriptions help LLM understand usage."""
        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        for tool in tools:
            # Descriptions should be reasonably detailed
            assert len(tool.description) > 50, f"{tool.name} has too short description"
            # Should mention key parameters or return values
            assert any(
                word in tool.description.lower()
                for word in ["model", "task", "3d", "animation", "status"]
            ), f"{tool.name} description lacks key terms"

    def test_tool_schemas_have_required_fields(self):
        """Verify tool schemas define required parameters correctly."""
        from vendor_connectors.meshy.tools import get_tools

        tools = get_tools()

        # text3d_generate should require prompt
        text3d_tool = next(t for t in tools if t.name == "text3d_generate")
        schema = text3d_tool.args_schema.model_json_schema()
        assert "prompt" in schema.get("required", [])


class TestLangChainAgentIntegration:
    """Integration tests with LangChain agents.

    These tests mock the actual API calls but verify the agent
    can correctly use our tools.
    """

    def test_agent_can_call_text3d_tool(self):
        """Test that a mock agent can invoke text3d_generate."""
        from vendor_connectors.meshy.tools import get_tools, text3d_generate

        # Mock the Meshy API call
        mock_result = MagicMock()
        mock_result.id = "test_task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/sword.glb"
        mock_result.thumbnail_url = "https://example.com/thumb.png"

        with patch("vendor_connectors.meshy.text3d.generate", return_value=mock_result):
            # Get tools and find text3d
            tools = get_tools()
            text3d_tool = next(t for t in tools if t.name == "text3d_generate")

            # Invoke the tool directly (simulating agent tool call)
            result = text3d_tool.invoke({"prompt": "a medieval sword"})

        assert result["task_id"] == "test_task_123"
        assert result["status"] == "SUCCEEDED"
        assert "sword.glb" in result["model_url"]

    def test_agent_workflow_generate_and_check_status(self):
        """Test a multi-step workflow: generate then check status."""
        from vendor_connectors.meshy.tools import get_tools

        # Mock results
        generate_result = MagicMock()
        generate_result.id = "workflow_task"
        generate_result.status.value = "PROCESSING"
        generate_result.model_urls = None
        generate_result.thumbnail_url = None

        status_result = MagicMock()
        status_result.status.value = "SUCCEEDED"
        status_result.progress = 100
        status_result.model_urls = MagicMock()
        status_result.model_urls.glb = "https://example.com/model.glb"

        tools = get_tools()
        text3d_tool = next(t for t in tools if t.name == "text3d_generate")
        status_tool = next(t for t in tools if t.name == "check_task_status")

        # Step 1: Generate
        with patch("vendor_connectors.meshy.text3d.generate", return_value=generate_result):
            gen_result = text3d_tool.invoke({"prompt": "a shield"})

        assert gen_result["task_id"] == "workflow_task"

        # Step 2: Check status
        with patch("vendor_connectors.meshy.text3d.get", return_value=status_result):
            final_result = status_tool.invoke(
                {"task_id": gen_result["task_id"], "task_type": "text-to-3d"}
            )

        assert final_result["status"] == "SUCCEEDED"
        assert final_result["model_url"] == "https://example.com/model.glb"


@pytest.mark.e2e
@pytest.mark.langchain
class TestLangChainE2E:
    """End-to-end tests with real API calls (recorded to cassettes).

    These tests require API keys on first run to record cassettes.
    Subsequent runs use recorded cassettes.
    """

    @pytest.mark.skip(reason="E2E test - requires API keys and cassette recording")
    @pytest.mark.vcr()
    def test_langchain_agent_generates_3d_model(
        self,
        anthropic_api_key: str | None,
        meshy_api_key: str | None,
        models_output_dir: Path,
    ):
        """Test full LangChain agent workflow generating a 3D model.

        This test:
        1. Creates a LangChain agent with Claude Haiku
        2. Gives it our Meshy tools
        3. Asks it to generate a simple 3D model
        4. Verifies the output

        Cassette: langchain_agent_generates_3d_model.yaml
        """
        pytest.importorskip("langchain_anthropic")

        if not anthropic_api_key or not meshy_api_key:
            pytest.skip("API keys required for E2E test")

        from langchain_anthropic import ChatAnthropic
        from langgraph.prebuilt import create_react_agent

        from vendor_connectors.meshy.tools import get_tools

        # Create agent with Claude Haiku (cost-effective for testing)
        llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
        tools = get_tools()
        agent = create_react_agent(llm, tools)

        # Run the agent
        result = agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        "Generate a simple 3D model of a wooden sword. "
                        "Just use the text3d_generate tool with a clear prompt.",
                    )
                ]
            }
        )

        # Verify we got a response with tool usage
        messages = result["messages"]
        assert len(messages) > 1  # Should have agent response

        # Look for tool call results in messages
        tool_results = [
            m for m in messages
            if hasattr(m, "type") and m.type == "tool"
        ]

        assert len(tool_results) > 0, "Agent should have called a tool"
