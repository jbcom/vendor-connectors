"""Pytest configuration for Meshy E2E tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# Meshy E2E directories
MESHY_E2E_DIR = Path(__file__).parent
CASSETTES_DIR = MESHY_E2E_DIR / "cassettes"
MODELS_OUTPUT_DIR = MESHY_E2E_DIR.parent / "fixtures" / "models"


@pytest.fixture(scope="session")
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
def anthropic_api_key() -> str | None:
    """Get Anthropic API key from environment."""
    return os.environ.get("ANTHROPIC_API_KEY")


@pytest.fixture(scope="module")
def vcr_config():
    """VCR configuration for recording Meshy API cassettes."""
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
