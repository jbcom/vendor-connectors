"""End-to-end tests for vendor-connectors.

This subpackage contains E2E tests that verify integration with real
AI agent frameworks using pytest-vcr for cassette recording.

Structure:
    e2e/
    ├── __init__.py          # This file
    ├── conftest.py          # Shared E2E fixtures
    └── meshy/               # Meshy connector E2E tests
        ├── __init__.py
        ├── conftest.py      # Meshy-specific fixtures
        ├── cassettes/       # VCR cassettes
        ├── test_langchain.py
        ├── test_crewai.py
        └── test_strands.py

Supported frameworks:
- LangChain / LangGraph
- CrewAI
- AWS Strands Agents
"""
