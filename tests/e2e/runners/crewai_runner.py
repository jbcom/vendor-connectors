"""CrewAI E2E test runner.

Runs agents using CrewAI's Agent, Task, and Crew abstractions.
"""

from __future__ import annotations

from typing import Any

from tests.e2e.runners.base import BaseAgentRunner, RunResult


class CrewAIRunner(BaseAgentRunner):
    """E2E test runner using CrewAI.

    Creates a simple single-agent Crew that can use our tools.
    Tools can be either LangChain StructuredTools (wrapped via LangChainTool)
    or native CrewAI tools.

    Example:
        from vendor_connectors.meshy.tools import get_tools

        runner = CrewAIRunner(tools=get_tools())
        result = runner.run("Generate a 3D sword")
    """

    def __init__(
        self,
        tools: list[Any],
        model: str = "claude-haiku-4-5-20251001",
        system_prompt: str | None = None,
        verbose: bool = False,
        role: str = "3D Asset Generator",
        goal: str = "Generate 3D models using Meshy AI tools",
        backstory: str = "An AI assistant specialized in creating 3D assets.",
    ):
        """Initialize CrewAI runner with agent configuration.

        Args:
            tools: List of tools (LangChain or CrewAI native)
            model: Model identifier
            system_prompt: Optional system prompt
            verbose: Enable verbose output
            role: Agent role description
            goal: Agent goal description
            backstory: Agent backstory
        """
        super().__init__(tools, model, system_prompt, verbose)
        self.role = role
        self.goal = goal
        self.backstory = backstory

    @staticmethod
    def _check_dependencies() -> None:
        """Check CrewAI dependencies."""
        import crewai  # noqa: F401

    def _default_system_prompt(self) -> str:
        return "Complete the assigned task using the available tools."

    def _wrap_tools(self) -> list[Any]:
        """Wrap LangChain tools for CrewAI if needed."""
        from langchain_core.tools import StructuredTool

        wrapped = []
        for tool in self.tools:
            if isinstance(tool, StructuredTool):
                # Import here to avoid requiring crewai for other runners
                from crewai.tools import LangChainTool
                wrapped.append(LangChainTool(tool=tool))
            else:
                wrapped.append(tool)
        return wrapped

    def _create_agent(self) -> Any:
        """Create a CrewAI Crew with a single agent."""
        from crewai import Agent

        crewai_tools = self._wrap_tools()

        agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=crewai_tools,
            llm=f"anthropic/{self.model}",
            verbose=self.verbose,
        )

        # Store agent for later use in _run_agent
        self._crewai_agent = agent
        return agent

    def _run_agent(self, prompt: str) -> RunResult:
        """Run the CrewAI agent via a Crew."""
        from crewai import Crew, Task

        # Ensure agent is created
        agent = self.agent

        # Create task for this prompt
        task = Task(
            description=prompt,
            agent=agent,
            expected_output="A result with task_id, status, and relevant URLs",
        )

        # Create and run crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=self.verbose,
        )

        result = crew.kickoff()

        # Extract tool calls from task output if available
        tool_calls = []
        # CrewAI doesn't expose tool calls directly in the same way
        # We'd need to parse the output or use callbacks

        return RunResult(
            success=True,
            output=str(result),
            tool_calls=tool_calls,
            raw_result=result,
        )
