"""End-to-end tests for Meshy AI tools integration.

Tests verify that Meshy LangChain/CrewAI/Strands tools work correctly
with real AI agent frameworks.

Cassette recording requires:
- ANTHROPIC_API_KEY: For Claude LLM calls
- MESHY_API_KEY: For Meshy 3D generation API

Once cassettes are recorded, tests run without API keys.
"""
