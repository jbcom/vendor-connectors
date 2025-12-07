"""GitHub operations as AI-callable tools.

This module exposes GithubConnector methods as LangChain tools:
- Repository operations: list_repositories, get_repository
- Branch operations: get_repository_branch, create_repository_branch
- File operations: get_repository_file, update_repository_file, delete_repository_file
- Organization: list_org_members, get_org_member
- Teams: list_teams, get_team, add_team_member, remove_team_member
- GraphQL: execute_graphql

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md

Example structure:

    GITHUB_TOOL_METHODS = [
        "list_repositories",
        "get_repository",
        "list_org_members",
        "get_org_member",
        "list_teams",
        "get_team",
        "get_repository_file",
        "update_repository_file",
        "create_repository_branch",
    ]

    def get_github_tools() -> list[StructuredTool]:
        tools = []
        for method_name in GITHUB_TOOL_METHODS:
            tool = create_tool_from_method(
                GithubConnector,
                method_name,
                exclude_params=["logger", "inputs"],
            )
            register_tool(tool, category=ToolCategory.GITHUB)
            tools.append(tool)
        return tools
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
