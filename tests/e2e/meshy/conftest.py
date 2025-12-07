"""Pytest configuration for Meshy E2E tests.

Provides Meshy-specific fixtures and VCR configuration.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


# Meshy E2E directories
MESHY_E2E_DIR = Path(__file__).parent
CASSETTES_DIR = MESHY_E2E_DIR / "cassettes"
MODELS_OUTPUT_DIR = MESHY_E2E_DIR.parent / "fixtures" / "models"


@pytest.fixture
def meshy_cassettes_dir() -> Path:
    """Return the Meshy cassettes directory."""
    CASSETTES_DIR.mkdir(parents=True, exist_ok=True)
    return CASSETTES_DIR


@pytest.fixture
def models_output_dir() -> Path:
    """Return the models output directory for downloaded GLBs."""
    MODELS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return MODELS_OUTPUT_DIR


@pytest.fixture
def meshy_api_key() -> str | None:
    """Get Meshy API key from environment."""
    return os.environ.get("MESHY_API_KEY")


@pytest.fixture
def skip_without_meshy(meshy_api_key: str | None):
    """Skip test if MESHY_API_KEY not set."""
    if not meshy_api_key:
        pytest.skip("MESHY_API_KEY required")


@pytest.fixture
def vcr_config(meshy_cassettes_dir: Path):
    """VCR configuration for recording Meshy API cassettes.

    Configuration:
    - Records once (won't re-record if cassette exists)
    - Filters sensitive API keys from cassettes
    - Matches requests by method, scheme, host, port, path, query
    """
    return {
        "cassette_library_dir": str(meshy_cassettes_dir),
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
