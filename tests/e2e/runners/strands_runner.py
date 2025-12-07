"""AWS Strands E2E test runner.

Runs agents using Strands Agents framework.
"""

from __future__ import annotations

from typing import Any

from tests.e2e.runners.base import BaseAgentRunner, RunResult


class StrandsRunner(BaseAgentRunner):
    """E2E test runner using AWS Strands Agents.

    Creates a Strands Agent that uses Python function tools directly.
    Strands supports both plain functions and tools decorated with @tool.

    Example:
        from vendor_connectors.meshy.tools import text3d_generate, list_animations

        runner = StrandsRunner(tools=[text3d_generate, list_animations])
        result = runner.run("Generate a 3D sword")
    """

    def __init__(
        self,
        tools: list[Any],
        model: str = "claude-haiku-4-5-20251001",
        system_prompt: str | None = None,
        verbose: bool = False,
        use_bedrock: bool = False,
    ):
        """Initialize Strands runner.

        Args:
            tools: List of Python functions or LangChain tools
            model: Model identifier
            system_prompt: Optional system prompt
            verbose: Enable verbose output
            use_bedrock: Use Bedrock instead of direct Anthropic API
        """
        super().__init__(tools, model, system_prompt, verbose)
        self.use_bedrock = use_bedrock

    @staticmethod
    def _check_dependencies() -> None:
        """Check Strands dependencies."""
        import strands  # noqa: F401

    def _default_system_prompt(self) -> str:
        return (
            "You are a helpful assistant with access to 3D generation tools. "
            "Use the tools to complete the user's request."
        )

    def _extract_functions(self) -> list[Any]:
        """Extract callable functions from tools.

        Strands works with plain Python functions. If we have LangChain
        StructuredTools, extract the underlying function.
        """
        from langchain_core.tools import StructuredTool

        functions = []
        for tool in self.tools:
            if isinstance(tool, StructuredTool):
                # Extract the underlying function
                functions.append(tool.func)
            elif callable(tool):
                functions.append(tool)
            else:
                raise ValueError(f"Tool {tool} is not callable")
        return functions

    def _create_agent(self) -> Any:
        """Create a Strands Agent."""
        from strands import Agent

        strands_tools = self._extract_functions()

        if self.use_bedrock:
            from strands.models import BedrockModel

            # Map model name to Bedrock model ID
            bedrock_model_id = self._get_bedrock_model_id()
            model = BedrockModel(model_id=bedrock_model_id)

            return Agent(
                model=model,
                system_prompt=self.system_prompt,
                tools=strands_tools,
            )
        else:
            # Use default Anthropic provider
            return Agent(
                system_prompt=self.system_prompt,
                tools=strands_tools,
            )

    def _get_bedrock_model_id(self) -> str:
        """Map model name to Bedrock model ID."""
        model_map = {
            "claude-haiku-4-5-20251001": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "claude-sonnet-4-20250514": "us.anthropic.claude-sonnet-4-20250514-v1:0",
            "claude-3-5-sonnet-20241022": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        }
        return model_map.get(self.model, f"anthropic.{self.model}-v1:0")

    def _run_agent(self, prompt: str) -> RunResult:
        """Run the Strands agent."""
        import os

        # Enable tool console mode for visibility if verbose
        if self.verbose:
            os.environ["STRANDS_TOOL_CONSOLE_MODE"] = "enabled"

        result = self.agent(prompt)

        # Strands returns the result directly
        # Tool calls are not easily extractable without callbacks
        output = str(result) if result else ""

        return RunResult(
            success=True,
            output=output,
            tool_calls=[],  # Would need event handlers to capture
            raw_result=result,
        )
