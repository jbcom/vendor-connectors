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

    # LangChain tools
    from vendor_connectors.meshy.tools import get_tools
    tools = get_tools()

    # CrewAI tools
    from vendor_connectors.meshy.tools import get_crewai_tools
    crewai_tools = get_crewai_tools()

    # MCP server
    from vendor_connectors.meshy.mcp import create_server, run_server
    server = create_server()
    run_server(server)
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
