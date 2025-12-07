"""Shared pytest configuration for E2E tests.

This module provides common fixtures and configuration used across
all E2E test subpackages.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Base directories
E2E_DIR = Path(__file__).parent
FIXTURES_DIR = E2E_DIR / "fixtures"


@pytest.fixture(scope="session")
def e2e_fixtures_dir() -> Path:
    """Return the shared E2E fixtures directory."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIXTURES_DIR


@pytest.fixture
def anthropic_api_key() -> str | None:
    """Get Anthropic API key from environment."""
    return os.environ.get("ANTHROPIC_API_KEY")


@pytest.fixture
def skip_without_anthropic(anthropic_api_key: str | None):
    """Skip test if ANTHROPIC_API_KEY not set."""
    if not anthropic_api_key:
        pytest.skip("ANTHROPIC_API_KEY required")


def pytest_configure(config):
    """Register custom markers for E2E tests."""
    config.addinivalue_line(
        "markers",
        "e2e: mark test as end-to-end (may require API keys)",
    )
    config.addinivalue_line(
        "markers",
        "langchain: mark test as using LangChain/LangGraph framework",
    )
    config.addinivalue_line(
        "markers",
        "crewai: mark test as using CrewAI framework",
    )
    config.addinivalue_line(
        "markers",
        "strands: mark test as using AWS Strands framework",
    )
    config.addinivalue_line(
        "markers",
        "vcr: mark test for VCR cassette recording",
    )
