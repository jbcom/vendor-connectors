"""MeshyConnector - Class-based interface for Meshy AI 3D generation API.

This module provides a class-based connector interface that matches the pattern
of other connectors in the vendor-connectors package (GithubConnector, AWSConnector, etc.).

Usage:
    from vendor_connectors.meshy import MeshyConnector

    meshy = MeshyConnector()  # Uses MESHY_API_KEY

    # Text to 3D
    result = meshy.text_to_3d(
        prompt="A realistic river otter",
        art_style="realistic",
        target_polycount=5000,
    )

    # Check status
    status = meshy.get_task(result.task_id)

    # Download result
    model_bytes = meshy.download_model(result.task_id, format="glb")
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from directed_inputs_class import DirectedInputsClass
from lifecyclelogging import Logging

from vendor_connectors.meshy import animate, base, retexture, rigging, text3d
from vendor_connectors.meshy.models import (
    AnimationResult,
    ArtStyle,
    Image3DRequest,
    Image3DResult,
    RetextureResult,
    RiggingResult,
    TaskStatus,
    Text3DResult,
)


@dataclass
class TaskResult:
    """Result from a Meshy task submission.

    Provides a unified interface for task results across all task types.

    Attributes:
        task_id: The Meshy task ID for tracking
        task_type: Type of task (text-to-3d, image-to-3d, rigging, animation, retexture)
        status: Current task status
        progress: Progress percentage (0-100)
        model_url: URL to download GLB model (when complete)
        thumbnail_url: URL to thumbnail preview
        error: Error message if task failed
    """

    task_id: str
    task_type: str
    status: TaskStatus = TaskStatus.PENDING
    progress: int = 0
    model_url: str | None = None
    thumbnail_url: str | None = None
    error: str | None = None
    raw_result: Any = field(default=None, repr=False)


class MeshyConnector(DirectedInputsClass):
    """Meshy AI connector for 3D asset generation.

    Provides a class-based interface matching other connectors in vendor-connectors.
    Wraps the functional API modules (text3d, rigging, animate, retexture).

    Args:
        api_key: Meshy API key. Defaults to MESHY_API_KEY env var.
        logger: Optional logger instance.
        **kwargs: Passed to DirectedInputsClass.

    Usage:
        from vendor_connectors.meshy import MeshyConnector

        meshy = MeshyConnector()

        # Generate a 3D model from text
        result = meshy.text_to_3d(
            prompt="A realistic river otter, quadruped, detailed fur texture",
            art_style="realistic",
            target_polycount=5000,
        )

        # Check task status
        status = meshy.get_task(result.task_id)

        # Download the model
        model_bytes = meshy.download_model(result.task_id, format="glb")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        logger: Optional[Logging] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.logging = logger or Logging(logger_name="MeshyConnector")
        self.logger = self.logging.logger

        # Set API key (env var or explicit)
        self._api_key = api_key or self.get_input("MESHY_API_KEY", required=False) or os.getenv("MESHY_API_KEY")
        if self._api_key:
            # Update the global API key in base module
            base._api_key = self._api_key

        self.logger.info("Initialized MeshyConnector")

    @property
    def api_key(self) -> str | None:
        """Get the configured API key."""
        return self._api_key

    def _validate_api_key(self) -> None:
        """Validate that API key is set."""
        if not self._api_key:
            msg = "MESHY_API_KEY not set. Provide api_key or set MESHY_API_KEY env var."
            raise ValueError(msg)

    # =========================================================================
    # Text-to-3D
    # =========================================================================

    def text_to_3d(
        self,
        prompt: str,
        *,
        art_style: ArtStyle | str = ArtStyle.REALISTIC,
        negative_prompt: str = "",
        topology: Optional[str] = None,  # "quad" or "triangle"
        target_polycount: int = 15000,
        enable_pbr: bool = True,
        wait: bool = True,
        poll_interval: float = 5.0,
        timeout: float = 600.0,
    ) -> TaskResult:
        """Generate a 3D model from text description.

        Args:
            prompt: Detailed text description of the 3D model to generate.
            art_style: Art style ("realistic", "cartoon", "low-poly", "sculpt", "pbr").
            negative_prompt: Things to avoid in the generation.
            topology: Mesh topology type ("quad" or "triangle").
            target_polycount: Target polygon count for the model.
            enable_pbr: Enable PBR (physically-based rendering) materials.
            wait: Wait for completion (default True).
            poll_interval: Polling interval in seconds when waiting.
            timeout: Timeout in seconds when waiting.

        Returns:
            TaskResult with task_id and status/model info.

        Raises:
            ValueError: If API key not set.
            RuntimeError: If task fails or times out.
        """
        self._validate_api_key()
        self.logger.info(f"Starting text-to-3d generation: {prompt[:50]}...")

        if isinstance(art_style, str):
            art_style = ArtStyle(art_style)

        if wait:
            result = text3d.generate(
                prompt,
                art_style=art_style,
                negative_prompt=negative_prompt,
                target_polycount=target_polycount,
                enable_pbr=enable_pbr,
                wait=True,
            )
            return self._text3d_result_to_task_result(result)

        # Non-blocking: just create the task
        from vendor_connectors.meshy.models import Text3DRequest

        request = Text3DRequest(
            mode="preview",
            prompt=prompt,
            art_style=art_style,
            negative_prompt=negative_prompt,
            topology=topology,
            target_polycount=target_polycount,
            enable_pbr=enable_pbr,
        )
        task_id = text3d.create(request)
        self.logger.info(f"Created text-to-3d task: {task_id}")

        return TaskResult(
            task_id=task_id,
            task_type="text-to-3d",
            status=TaskStatus.PENDING,
        )

    def _text3d_result_to_task_result(self, result: Text3DResult) -> TaskResult:
        """Convert Text3DResult to TaskResult."""
        model_url = None
        if result.model_urls and result.model_urls.glb:
            model_url = result.model_urls.glb

        return TaskResult(
            task_id=result.id,
            task_type="text-to-3d",
            status=result.status,
            progress=result.progress,
            model_url=model_url,
            thumbnail_url=result.thumbnail_url,
            error=result.error,
            raw_result=result,
        )

    # =========================================================================
    # Image-to-3D
    # =========================================================================

    def image_to_3d(
        self,
        image_url: str,
        *,
        topology: Optional[str] = None,  # "quad" or "triangle"
        target_polycount: Optional[int] = None,
        enable_pbr: bool = True,
        wait: bool = True,
        poll_interval: float = 5.0,
        timeout: float = 600.0,
    ) -> TaskResult:
        """Generate a 3D model from an image.

        Args:
            image_url: URL to the source image.
            topology: Mesh topology type ("quad" or "triangle").
            target_polycount: Target polygon count for the model.
            enable_pbr: Enable PBR (physically-based rendering) materials.
            wait: Wait for completion (default True).
            poll_interval: Polling interval in seconds when waiting.
            timeout: Timeout in seconds when waiting.

        Returns:
            TaskResult with task_id and status/model info.

        Raises:
            ValueError: If API key not set.
            RuntimeError: If task fails or times out.
        """
        self._validate_api_key()
        self.logger.info(f"Starting image-to-3d generation from: {image_url[:50]}...")

        request = Image3DRequest(
            mode="preview",
            image_url=image_url,
            topology=topology,
            target_polycount=target_polycount,
            enable_pbr=enable_pbr,
        )

        # Create task
        response = base.request(
            "POST",
            "image-to-3d",
            version="v2",
            json=request.model_dump(exclude_none=True),
        )
        task_id = response.json().get("result")
        self.logger.info(f"Created image-to-3d task: {task_id}")

        if not wait:
            return TaskResult(
                task_id=task_id,
                task_type="image-to-3d",
                status=TaskStatus.PENDING,
            )

        # Poll until complete
        result = self._poll_image3d(task_id, poll_interval, timeout)
        return self._image3d_result_to_task_result(result)

    def _poll_image3d(self, task_id: str, interval: float, timeout: float) -> Image3DResult:
        """Poll image-to-3d task until complete."""
        import time

        start = time.time()
        while True:
            response = base.request("GET", f"image-to-3d/{task_id}", version="v2")
            result = Image3DResult(**response.json())

            if result.status == TaskStatus.SUCCEEDED:
                return result
            if result.status == TaskStatus.FAILED:
                msg = f"Image-to-3d task failed: {result.error or 'Unknown error'}"
                raise RuntimeError(msg)
            if result.status == TaskStatus.EXPIRED:
                msg = "Image-to-3d task expired"
                raise RuntimeError(msg)
            if time.time() - start > timeout:
                msg = f"Image-to-3d task timed out after {timeout}s"
                raise TimeoutError(msg)

            time.sleep(interval)

    def _image3d_result_to_task_result(self, result: Image3DResult) -> TaskResult:
        """Convert Image3DResult to TaskResult."""
        model_url = None
        if result.model_urls and result.model_urls.glb:
            model_url = result.model_urls.glb

        return TaskResult(
            task_id=result.id,
            task_type="image-to-3d",
            status=result.status,
            progress=result.progress,
            model_url=model_url,
            thumbnail_url=result.thumbnail_url,
            error=result.error,
            raw_result=result,
        )

    # =========================================================================
    # Rigging
    # =========================================================================

    def rig_model(
        self,
        model_task_id: str,
        *,
        height_meters: float = 1.7,
        wait: bool = True,
        poll_interval: float = 5.0,
        timeout: float = 600.0,
    ) -> TaskResult:
        """Add a skeleton/rig to a 3D model for animation.

        Args:
            model_task_id: Task ID of the model to rig (from text_to_3d or image_to_3d).
            height_meters: Character height in meters (affects bone scaling).
            wait: Wait for completion (default True).
            poll_interval: Polling interval in seconds when waiting.
            timeout: Timeout in seconds when waiting.

        Returns:
            TaskResult with rigging info.

        Raises:
            ValueError: If API key not set.
            RuntimeError: If task fails or times out.
        """
        self._validate_api_key()
        self.logger.info(f"Starting rigging for model: {model_task_id}")

        if wait:
            result = rigging.rig(model_task_id, height_meters=height_meters, wait=True)
            return self._rigging_result_to_task_result(result)

        task_id = rigging.rig(model_task_id, height_meters=height_meters, wait=False)
        return TaskResult(
            task_id=task_id,
            task_type="rigging",
            status=TaskStatus.PENDING,
        )

    def _rigging_result_to_task_result(self, result: RiggingResult) -> TaskResult:
        """Convert RiggingResult to TaskResult."""
        model_url = None
        if result.result and result.result.rigged_character_glb_url:
            model_url = result.result.rigged_character_glb_url

        return TaskResult(
            task_id=result.id,
            task_type="rigging",
            status=result.status,
            progress=result.progress,
            model_url=model_url,
            error=str(result.task_error) if result.task_error else None,
            raw_result=result,
        )

    # =========================================================================
    # Animation
    # =========================================================================

    def apply_animation(
        self,
        rigged_task_id: str,
        animation_id: int,
        *,
        loop: bool = True,
        frame_rate: int = 30,
        wait: bool = True,
        poll_interval: float = 5.0,
        timeout: float = 600.0,
    ) -> TaskResult:
        """Apply an animation to a rigged model.

        Args:
            rigged_task_id: Task ID of the rigged model (from rig_model).
            animation_id: Animation ID from the Meshy catalog (0-677).
            loop: Whether the animation should loop.
            frame_rate: Animation frame rate.
            wait: Wait for completion (default True).
            poll_interval: Polling interval in seconds when waiting.
            timeout: Timeout in seconds when waiting.

        Returns:
            TaskResult with animation info.

        Raises:
            ValueError: If API key not set.
            RuntimeError: If task fails or times out.
        """
        self._validate_api_key()
        self.logger.info(f"Applying animation {animation_id} to model: {rigged_task_id}")

        if wait:
            result = animate.apply(
                rigged_task_id,
                animation_id,
                loop=loop,
                frame_rate=frame_rate,
                wait=True,
            )
            return self._animation_result_to_task_result(result)

        task_id = animate.apply(
            rigged_task_id,
            animation_id,
            loop=loop,
            frame_rate=frame_rate,
            wait=False,
        )
        return TaskResult(
            task_id=task_id,
            task_type="animation",
            status=TaskStatus.PENDING,
        )

    def _animation_result_to_task_result(self, result: AnimationResult) -> TaskResult:
        """Convert AnimationResult to TaskResult."""
        return TaskResult(
            task_id=result.id,
            task_type="animation",
            status=result.status,
            progress=result.progress,
            model_url=result.animation_glb_url,
            error=str(result.task_error) if result.task_error else None,
            raw_result=result,
        )

    # =========================================================================
    # Retexture
    # =========================================================================

    def retexture_model(
        self,
        model_task_id: str,
        prompt: str,
        *,
        enable_original_uv: bool = True,
        enable_pbr: bool = True,
        wait: bool = True,
        poll_interval: float = 5.0,
        timeout: float = 600.0,
    ) -> TaskResult:
        """Apply new textures to a model based on text description.

        Args:
            model_task_id: Task ID of the model to retexture.
            prompt: Text description of the new texture/appearance.
            enable_original_uv: Keep original UV mapping.
            enable_pbr: Enable PBR materials.
            wait: Wait for completion (default True).
            poll_interval: Polling interval in seconds when waiting.
            timeout: Timeout in seconds when waiting.

        Returns:
            TaskResult with retexture info.

        Raises:
            ValueError: If API key not set.
            RuntimeError: If task fails or times out.
        """
        self._validate_api_key()
        self.logger.info(f"Starting retexture for model {model_task_id}: {prompt[:50]}...")

        if wait:
            result = retexture.apply(
                model_task_id,
                prompt,
                enable_original_uv=enable_original_uv,
                enable_pbr=enable_pbr,
                wait=True,
            )
            return self._retexture_result_to_task_result(result)

        task_id = retexture.apply(
            model_task_id,
            prompt,
            enable_original_uv=enable_original_uv,
            enable_pbr=enable_pbr,
            wait=False,
        )
        return TaskResult(
            task_id=task_id,
            task_type="retexture",
            status=TaskStatus.PENDING,
        )

    def _retexture_result_to_task_result(self, result: RetextureResult) -> TaskResult:
        """Convert RetextureResult to TaskResult."""
        model_url = None
        if result.model_urls and result.model_urls.glb:
            model_url = result.model_urls.glb

        return TaskResult(
            task_id=result.id,
            task_type="retexture",
            status=result.status,
            progress=result.progress,
            model_url=model_url,
            thumbnail_url=result.thumbnail_url,
            error=str(result.task_error) if result.task_error else None,
            raw_result=result,
        )

    # =========================================================================
    # Task Management
    # =========================================================================

    def get_task(
        self,
        task_id: str,
        task_type: Literal["text-to-3d", "image-to-3d", "rigging", "animation", "retexture"] = "text-to-3d",
    ) -> TaskResult:
        """Get the status of a Meshy task.

        Args:
            task_id: The Meshy task ID.
            task_type: Type of task to query.

        Returns:
            TaskResult with current status.

        Raises:
            ValueError: If API key not set or unknown task type.
        """
        self._validate_api_key()

        if task_type == "text-to-3d":
            result = text3d.get(task_id)
            return self._text3d_result_to_task_result(result)
        elif task_type == "image-to-3d":
            response = base.request("GET", f"image-to-3d/{task_id}", version="v2")
            result = Image3DResult(**response.json())
            return self._image3d_result_to_task_result(result)
        elif task_type == "rigging":
            result = rigging.get(task_id)
            return self._rigging_result_to_task_result(result)
        elif task_type == "animation":
            result = animate.get(task_id)
            return self._animation_result_to_task_result(result)
        elif task_type == "retexture":
            result = retexture.get(task_id)
            return self._retexture_result_to_task_result(result)
        else:
            msg = f"Unknown task type: {task_type}"
            raise ValueError(msg)

    def download_model(
        self,
        task_id: str,
        *,
        format: Literal["glb", "fbx", "usdz", "obj"] = "glb",
        task_type: Literal["text-to-3d", "image-to-3d", "rigging", "animation", "retexture"] = "text-to-3d",
    ) -> bytes:
        """Download a completed model.

        Args:
            task_id: The Meshy task ID.
            format: Model format to download (glb, fbx, usdz, obj).
            task_type: Type of task.

        Returns:
            Model file as bytes.

        Raises:
            ValueError: If model not available or format not supported.
            RuntimeError: If download fails.
        """
        self._validate_api_key()

        # Get task to find model URL
        task_result = self.get_task(task_id, task_type)

        if task_result.status != TaskStatus.SUCCEEDED:
            msg = f"Task {task_id} not complete (status: {task_result.status})"
            raise ValueError(msg)

        # Get the appropriate URL based on format
        model_url = self._get_model_url_for_format(task_result, format)
        if not model_url:
            msg = f"Model URL not available for format: {format}"
            raise ValueError(msg)

        self.logger.info(f"Downloading {format} model from task {task_id}")

        # Download the file
        import httpx

        response = httpx.get(model_url)
        response.raise_for_status()
        return response.content

    def _get_model_url_for_format(self, task_result: TaskResult, format: str) -> str | None:
        """Get model URL for the specified format."""
        if not task_result.raw_result:
            return task_result.model_url if format == "glb" else None

        raw = task_result.raw_result

        # Handle different result types
        if hasattr(raw, "model_urls") and raw.model_urls:
            return getattr(raw.model_urls, format, None)
        elif hasattr(raw, "animation_glb_url") and format == "glb":
            return raw.animation_glb_url
        elif hasattr(raw, "result") and raw.result:
            if format == "glb" and hasattr(raw.result, "rigged_character_glb_url"):
                return raw.result.rigged_character_glb_url
            elif format == "fbx" and hasattr(raw.result, "rigged_character_fbx_url"):
                return raw.result.rigged_character_fbx_url

        return task_result.model_url if format == "glb" else None

    def download_model_to_file(
        self,
        task_id: str,
        output_path: str,
        *,
        format: Literal["glb", "fbx", "usdz", "obj"] = "glb",
        task_type: Literal["text-to-3d", "image-to-3d", "rigging", "animation", "retexture"] = "text-to-3d",
    ) -> int:
        """Download a completed model to a file.

        Args:
            task_id: The Meshy task ID.
            output_path: Path to save the model file.
            format: Model format to download (glb, fbx, usdz, obj).
            task_type: Type of task.

        Returns:
            Number of bytes written.

        Raises:
            ValueError: If model not available or format not supported.
            RuntimeError: If download fails.
        """
        model_bytes = self.download_model(task_id, format=format, task_type=task_type)

        import os

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(model_bytes)

        self.logger.info(f"Saved {len(model_bytes)} bytes to {output_path}")
        return len(model_bytes)

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def close(self) -> None:
        """Close the HTTP client."""
        base.close()
        self.logger.info("Closed MeshyConnector")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
