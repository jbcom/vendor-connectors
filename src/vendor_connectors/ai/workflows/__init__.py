"""LangGraph workflow support for multi-step agentic operations.

This package provides:
- WorkflowBuilder - Declarative DSL for building LangGraph workflows
- Pre-built workflow nodes for common operations
- Workflow templates for common patterns

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Usage (after implementation):
    from vendor_connectors.ai.workflows import WorkflowBuilder

    # Declarative multi-step workflows
    workflow = (
        WorkflowBuilder()
        .add_step("analyze", "Review this PR for security issues: {pr_url}")
        .add_step("report", "Post findings to Slack #security")
        .add_conditional(
            "is_critical",
            true_step="create_issue",
            false_step="done",
        )
        .add_step("create_issue", "Create GitHub issue if critical")
        .build()
    )

    result = workflow.invoke({"pr_url": "https://github.com/org/repo/pull/123"})
"""

from __future__ import annotations

__all__ = [
    # Will export:
    # "WorkflowBuilder",
    # "create_workflow",
]

# Placeholder - actual imports will be added after PR #16 merges
# from vendor_connectors.ai.workflows.builder import WorkflowBuilder, create_workflow
