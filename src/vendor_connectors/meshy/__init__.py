"""Meshy AI Connector - Python SDK for Meshy AI 3D generation API.

Part of vendor-connectors, providing access to Meshy AI's 3D asset generation API.

Usage:
    # Class-based interface (recommended for new code)
    from vendor_connectors.meshy import MeshyConnector

    meshy = MeshyConnector()  # Uses MESHY_API_KEY env var

    # Text to 3D
    result = meshy.text_to_3d(
        prompt="A realistic river otter, quadruped, detailed fur texture",
        art_style="realistic",
        target_polycount=5000,
    )

    # Check status
    status = meshy.get_task(result.task_id)

    # Download result
    model_bytes = meshy.download_model(result.task_id, format="glb")

    # Functional interface (also available)
    from vendor_connectors.meshy import text3d, rigging, animate, retexture

    model = text3d.generate("a medieval sword")
    rigged = rigging.rig(model.id)
    animated = animate.apply(rigged.id, animation_id=0)
    retextured = retexture.apply(model.id, "golden with gems")
"""

from __future__ import annotations

from vendor_connectors.meshy import animate, base, retexture, rigging, text3d
from vendor_connectors.meshy.base import MeshyAPIError, RateLimitError
from vendor_connectors.meshy.connector import MeshyConnector, TaskResult

__all__ = [
    # Class-based connector
    "MeshyConnector",
    "TaskResult",
    # Errors
    "MeshyAPIError",
    "RateLimitError",
    # API modules (functional interface)
    "animate",
    "base",
    "retexture",
    "rigging",
    "text3d",
]
