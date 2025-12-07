"""Meshy AI - Python SDK for Meshy AI 3D generation API.

Part of vendor-connectors, providing access to Meshy AI's 3D asset generation API.

Usage:
    # Functional interface
    from vendor_connectors.meshy import text3d, image3d, rigging, animate, retexture

    # Text to 3D
    model = text3d.generate("a medieval sword")

    # Image to 3D
    model = image3d.generate("https://example.com/image.png")

    # Rig for animation
    rigged = rigging.rig(model.id)

    # Apply animation
    animated = animate.apply(rigged.id, animation_id=0)

    # Retexture
    retextured = retexture.apply(model.id, "golden with gems")

    # AI agent integration
    from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools
    tools = get_meshy_tools()

    # For CrewAI
    from vendor_connectors.ai.providers.crewai import get_tools
    crewai_tools = get_tools()

    # For MCP
    from vendor_connectors.ai.providers.mcp import create_server
    server = create_server()
"""

from __future__ import annotations

from vendor_connectors.meshy import animate, base, image3d, retexture, rigging, text3d
from vendor_connectors.meshy.base import MeshyAPIError, RateLimitError

__all__ = [
    # Errors
    "MeshyAPIError",
    "RateLimitError",
    # API modules (functional interface)
    "animate",
    "base",
    "image3d",
    "retexture",
    "rigging",
    "text3d",
]
