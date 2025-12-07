"""Base types and interfaces for AI sub-package.

This module defines:
- AIProvider enum - Supported AI providers
- ToolCategory enum - Categories for vendor connector tools
- ToolParameter - Definition of a tool parameter
- ToolDefinition - Framework-agnostic tool definition
- AIMessage - Unified message format
- AIResponse - Response from AI provider

Status: PLACEHOLDER - Implementation blocked by PR #16
See: docs/development/ai-subpackage-design.md
"""

from __future__ import annotations

# Placeholder - actual implementation will be added after PR #16 merges
#
# Example structure:
#
# from dataclasses import dataclass, field
# from enum import Enum
# from typing import Any, Callable, Optional
#
# class AIProvider(str, Enum):
#     ANTHROPIC = "anthropic"
#     OPENAI = "openai"
#     GOOGLE = "google"
#     XAI = "xai"
#     OLLAMA = "ollama"
#
# class ToolCategory(str, Enum):
#     AWS = "aws"
#     GITHUB = "github"
#     SLACK = "slack"
#     VAULT = "vault"
#     GOOGLE_CLOUD = "google_cloud"
#     ZOOM = "zoom"
#     MESHY = "meshy"
#
# @dataclass
# class AIResponse:
#     content: str
#     model: str
#     provider: AIProvider
#     usage: dict[str, int] = field(default_factory=dict)
