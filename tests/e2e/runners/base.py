"""Base interface for E2E test runners.

Defines the common interface that all framework runners must implement,
enabling framework-agnostic test scenarios.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RunResult:
    """Result from an agent run.

    Provides a unified result format across all frameworks.
    """

    success: bool
    """Whether the run completed successfully."""

    output: str
    """The agent's final output/response."""

    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    """List of tool calls made during the run."""

    raw_result: Any = None
    """Framework-specific raw result for debugging."""

    error: str | None = None
    """Error message if the run failed."""

    def has_tool_call(self, tool_name: str) -> bool:
        """Check if a specific tool was called."""
        return any(tc.get("name") == tool_name for tc in self.tool_calls)

    def get_tool_result(self, tool_name: str) -> dict[str, Any] | None:
        """Get the result of a specific tool call."""
        for tc in self.tool_calls:
            if tc.get("name") == tool_name:
                return tc.get("result")
        return None


class BaseAgentRunner(ABC):
    """Base class for E2E test runners.

    Provides a common interface for running agents across different
    frameworks (LangChain, CrewAI, Strands).

    Usage:
        runner = SomeFrameworkRunner(tools=[...], model="claude-haiku-4-5-20251001")
        result = runner.run("Generate a 3D model of a sword")
        assert result.success
        assert result.has_tool_call("text3d_generate")
    """

    def __init__(
        self,
        tools: list[Any],
        model: str = "claude-haiku-4-5-20251001",
        system_prompt: str | None = None,
        verbose: bool = False,
    ):
        """Initialize the runner.

        Args:
            tools: List of tools (format depends on framework)
            model: Model identifier (framework may interpret differently)
            system_prompt: Optional system prompt for the agent
            verbose: Enable verbose output
        """
        self.tools = tools
        self.model = model
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.verbose = verbose
        self._agent = None

    @abstractmethod
    def _default_system_prompt(self) -> str:
        """Return the default system prompt for this runner."""
        pass

    @abstractmethod
    def _create_agent(self) -> Any:
        """Create the framework-specific agent instance."""
        pass

    @abstractmethod
    def _run_agent(self, prompt: str) -> RunResult:
        """Execute the agent with the given prompt."""
        pass

    @property
    def agent(self) -> Any:
        """Lazily create and return the agent."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    def run(self, prompt: str) -> RunResult:
        """Run the agent with the given prompt.

        Args:
            prompt: The user prompt/task for the agent

        Returns:
            RunResult with success status, output, and tool calls
        """
        try:
            return self._run_agent(prompt)
        except Exception as e:
            return RunResult(
                success=False,
                output="",
                error=str(e),
            )

    @classmethod
    def is_available(cls) -> bool:
        """Check if this runner's framework is installed."""
        try:
            cls._check_dependencies()
            return True
        except ImportError:
            return False

    @staticmethod
    @abstractmethod
    def _check_dependencies() -> None:
        """Check that required dependencies are installed.

        Raises:
            ImportError: If dependencies are missing
        """
        pass
