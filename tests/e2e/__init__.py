"""End-to-end tests for vendor-connectors.

Real E2E tests that hit actual APIs and record cassettes with pytest-vcr.

Structure:
    e2e/
    ├── __init__.py
    ├── conftest.py          # Shared fixtures
    ├── fixtures/            # Output directory for generated models
    │   └── models/
    └── meshy/               # Meshy connector E2E tests
        ├── cassettes/       # VCR cassettes
        ├── test_langchain.py
        ├── test_crewai.py
        └── test_strands.py

Running E2E tests:
    # Record cassettes (requires API keys)
    ANTHROPIC_API_KEY=... MESHY_API_KEY=... pytest tests/e2e -v

    # Replay from cassettes (no API keys needed)
    pytest tests/e2e -v
"""
