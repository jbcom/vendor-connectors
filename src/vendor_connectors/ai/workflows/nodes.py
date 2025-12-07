"""Pre-built workflow nodes for common operations.

This module provides reusable nodes for LangGraph workflows.

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example nodes:

    def chat_node(state: dict, ai: AIConnector, prompt: str) -> dict:
        '''Node that sends a chat message and updates state.'''
        response = ai.chat(prompt.format(**state))
        return {"messages": state.get("messages", []) + [response]}

    def tool_node(state: dict, ai: AIConnector, prompt: str) -> dict:
        '''Node that executes with tools.'''
        response = ai.invoke_with_tools(prompt.format(**state))
        return {"messages": state.get("messages", []) + [response]}

    def human_input_node(state: dict) -> dict:
        '''Node that waits for human input (requires interrupt).'''
        ...

    def conditional_node(
        state: dict,
        condition: Callable[[dict], bool],
    ) -> str:
        '''Node that returns next step based on condition.'''
        return "true_branch" if condition(state) else "false_branch"
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
