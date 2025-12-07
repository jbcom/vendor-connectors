"""Pytest configuration for E2E tests.

This module configures:
- VCR cassette recording settings
- Test fixtures for API keys
- Output directory management
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Directory for VCR cassettes
CASSETTES_DIR = Path(__file__).parent / "cassettes"

# Directory for generated model outputs
MODELS_OUTPUT_DIR = Path(__file__).parent.parent.parent / "fixtures" / "models"


@pytest.fixture
def cassettes_dir() -> Path:
    """Return the cassettes directory path."""
    CASSETTES_DIR.mkdir(parents=True, exist_ok=True)
    return CASSETTES_DIR


@pytest.fixture
def models_output_dir() -> Path:
    """Return the models output directory path."""
    MODELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return MODELS_OUTPUT_DIR


@pytest.fixture
def anthropic_api_key() -> str | None:
    """Get Anthropic API key from environment."""
    return os.environ.get("ANTHROPIC_API_KEY")


@pytest.fixture
def meshy_api_key() -> str | None:
    """Get Meshy API key from environment."""
    return os.environ.get("MESHY_API_KEY")


@pytest.fixture
def vcr_config():
    """VCR configuration for recording API cassettes.

    This configuration:
    - Records once (won't re-record if cassette exists)
    - Filters out sensitive API keys from cassettes
    - Matches requests by method, scheme, host, port, path, and query
    """
    return {
        "cassette_library_dir": str(CASSETTES_DIR),
        "record_mode": "once",
        "match_on": ["method", "scheme", "host", "port", "path", "query"],
        "filter_headers": [
            ("authorization", "FILTERED"),
            ("x-api-key", "FILTERED"),
            ("anthropic-api-key", "FILTERED"),
        ],
        "filter_post_data_parameters": [
            ("api_key", "FILTERED"),
        ],
        "decode_compressed_response": True,
    }


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "e2e: mark test as an end-to-end test requiring API keys",
    )
    config.addinivalue_line(
        "markers",
        "langchain: mark test as using LangChain framework",
    )
    config.addinivalue_line(
        "markers",
        "crewai: mark test as using CrewAI framework",
    )
    config.addinivalue_line(
        "markers",
        "strands: mark test as using AWS Strands framework",
    )
