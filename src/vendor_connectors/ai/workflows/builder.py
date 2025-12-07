"""Workflow builder for creating LangGraph workflows.

This module provides a fluent DSL for building multi-step workflows.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    class WorkflowBuilder:
        def __init__(self, ai_connector: Optional[AIConnector] = None):
            self._steps: list[WorkflowStep] = []
            self._conditionals: dict[str, ConditionalStep] = {}
            self._ai = ai_connector

        def add_step(
            self,
            name: str,
            prompt: str,
            tools: Optional[list] = None,
        ) -> "WorkflowBuilder":
            '''Add a step to the workflow.'''
            ...

        def add_conditional(
            self,
            name: str,
            condition: Callable[[dict], bool] | str,
            true_step: str,
            false_step: str,
        ) -> "WorkflowBuilder":
            '''Add a conditional branch.'''
            ...

        def build(self) -> CompiledGraph:
            '''Build and return the LangGraph workflow.'''
            from langgraph.graph import StateGraph
            ...

    def create_workflow(
        steps: list[tuple[str, str]],
        ai_connector: Optional[AIConnector] = None,
    ) -> CompiledGraph:
        '''Convenience function for simple sequential workflows.'''
        builder = WorkflowBuilder(ai_connector)
        for name, prompt in steps:
            builder.add_step(name, prompt)
        return builder.build()
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
