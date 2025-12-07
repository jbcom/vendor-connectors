"""Image-to-3D API.

Usage:
    from vendor_connectors.meshy import image3d

    result = image3d.generate("https://example.com/image.png")
    print(result.model_urls.glb)
"""

from __future__ import annotations

import time

from vendor_connectors.meshy import base
from vendor_connectors.meshy.models import Image3DRequest, Image3DResult, TaskStatus


def create(request: Image3DRequest) -> str:
    """Create image-to-3d task. Returns task_id."""
    response = base.request(
        "POST",
        "image-to-3d",
        version="v2",
        json=request.model_dump(exclude_none=True),
    )
    return response.json().get("result")


def get(task_id: str) -> Image3DResult:
    """Get task status."""
    response = base.request("GET", f"image-to-3d/{task_id}", version="v2")
    return Image3DResult(**response.json())


def refine(task_id: str) -> str:
    """Refine preview to full quality. Returns new task_id."""
    response = base.request(
        "POST",
        f"image-to-3d/{task_id}/refine",
        version="v2",
        json={},
    )
    return response.json().get("result")


def poll(task_id: str, interval: float = 5.0, timeout: float = 600.0) -> Image3DResult:
    """Poll until complete or failed."""
    start = time.time()
    while True:
        result = get(task_id)
        if result.status == TaskStatus.SUCCEEDED:
            return result
        if result.status == TaskStatus.FAILED:
            msg = f"Task failed: {result.error or 'Unknown error'}"
            raise RuntimeError(msg)
        if result.status == TaskStatus.EXPIRED:
            msg = "Task expired"
            raise RuntimeError(msg)
        if time.time() - start > timeout:
            msg = f"Task timed out after {timeout}s"
            raise TimeoutError(msg)
        time.sleep(interval)


def generate(
    image_url: str,
    *,
    topology: str | None = None,
    target_polycount: int | None = None,
    enable_pbr: bool = True,
    wait: bool = True,
) -> Image3DResult | str:
    """Generate a 3D model from an image.

    Args:
        image_url: URL to the source image
        topology: Mesh topology ("quad" or "triangle")
        target_polycount: Target polygon count
        enable_pbr: Enable PBR materials
        wait: Wait for completion (default True)

    Returns:
        Image3DResult if wait=True, task_id if wait=False
    """
    request = Image3DRequest(
        mode="preview",
        image_url=image_url,
        topology=topology,
        target_polycount=target_polycount,
        enable_pbr=enable_pbr,
    )

    task_id = create(request)

    if not wait:
        return task_id

    return poll(task_id)
