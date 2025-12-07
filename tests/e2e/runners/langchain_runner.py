"""LangChain/LangGraph E2E test runner.

Runs agents using LangChain's create_react_agent (via LangGraph).
"""

from __future__ import annotations

from typing import Any

from tests.e2e.runners.base import BaseAgentRunner, RunResult


class LangChainRunner(BaseAgentRunner):
    """E2E test runner using LangChain/LangGraph.

    Uses create_react_agent from langgraph.prebuilt to create
    a ReAct agent that can use our LangChain StructuredTools.

    Example:
        from vendor_connectors.meshy.tools import get_tools

        runner = LangChainRunner(tools=get_tools())
        result = runner.run("Generate a 3D sword")
    """

    @staticmethod
    def _check_dependencies() -> None:
        """Check LangChain dependencies."""
        import langchain_anthropic  # noqa: F401
        import langchain_core  # noqa: F401
        import langgraph  # noqa: F401

    def _default_system_prompt(self) -> str:
        return (
            "You are a helpful assistant with access to tools for 3D model generation. "
            "Use the tools provided to complete the user's request. "
            "Be concise and direct in your responses."
        )

    def _create_agent(self) -> Any:
        """Create a LangGraph ReAct agent."""
        from langchain_anthropic import ChatAnthropic
        from langgraph.prebuilt import create_react_agent

        llm = ChatAnthropic(
            model=self.model,
            # Add system prompt via model kwargs if needed
        )

        return create_react_agent(
            llm,
            self.tools,
            state_modifier=self.system_prompt,
        )

    def _run_agent(self, prompt: str) -> RunResult:
        """Run the LangGraph agent."""
        result = self.agent.invoke(
            {"messages": [("user", prompt)]}
        )

        messages = result.get("messages", [])
        tool_calls = []
        final_output = ""

        for msg in messages:
            # Extract tool calls
            if hasattr(msg, "type") and msg.type == "tool":
                tool_calls.append({
                    "name": getattr(msg, "name", "unknown"),
                    "result": msg.content if hasattr(msg, "content") else None,
                })

            # Get final AI message
            if hasattr(msg, "type") and msg.type == "ai":
                if hasattr(msg, "content") and msg.content:
                    final_output = msg.content

        return RunResult(
            success=True,
            output=final_output,
            tool_calls=tool_calls,
            raw_result=result,
        )


class LangGraphRunner(LangChainRunner):
    """Alias for LangChainRunner (they use the same infrastructure)."""

    pass
