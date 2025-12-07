"""Reusable E2E test runners for AI agent frameworks.

This module provides framework-agnostic test runners that allow
the same test scenarios to be executed across different frameworks:
- LangChain / LangGraph
- CrewAI
- AWS Strands Agents

Usage:
    from tests.e2e.runners import LangChainRunner, CrewAIRunner, StrandsRunner

    # All runners share the same interface
    runner = LangChainRunner(tools=get_tools())
    result = runner.run("Generate a 3D sword")
"""

from tests.e2e.runners.base import BaseAgentRunner, RunResult
from tests.e2e.runners.crewai_runner import CrewAIRunner
from tests.e2e.runners.langchain_runner import LangChainRunner
from tests.e2e.runners.strands_runner import StrandsRunner

__all__ = [
    "BaseAgentRunner",
    "RunResult",
    "LangChainRunner",
    "CrewAIRunner",
    "StrandsRunner",
]
