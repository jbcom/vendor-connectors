"""End-to-end tests for Meshy tools with real AI agent frameworks.

These tests use pytest-vcr to record and replay API calls for:
- LangChain / LangGraph agents
- CrewAI agents
- AWS Strands agents

Cassettes are stored in the cassettes/ directory and can be re-recorded
by deleting them and running tests with valid API keys:
- ANTHROPIC_API_KEY: For Claude LLM
- MESHY_API_KEY: For Meshy 3D generation
"""
