"""Tests for MeshyConnector class."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from vendor_connectors.meshy import MeshyConnector, TaskResult
from vendor_connectors.meshy.models import (
    AnimationResult,
    ModelUrls,
    RetextureResult,
    RiggingResult,
    RiggingResultData,
    TaskStatus,
    Text3DResult,
)


class TestMeshyConnectorInit:
    """Tests for MeshyConnector initialization."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        connector = MeshyConnector(api_key="test-key-123")
        assert connector.api_key == "test-key-123"

    def test_init_without_api_key(self, monkeypatch):
        """Test initialization without API key (uses env var)."""
        monkeypatch.setenv("MESHY_API_KEY", "env-key-456")
        connector = MeshyConnector()
        assert connector.api_key == "env-key-456"

    def test_init_no_api_key_available(self, monkeypatch):
        """Test initialization when no API key is available."""
        monkeypatch.delenv("MESHY_API_KEY", raising=False)
        connector = MeshyConnector()
        assert connector.api_key is None


class TestMeshyConnectorValidation:
    """Tests for API key validation."""

    def test_validate_api_key_raises_without_key(self, monkeypatch):
        """Test that validation raises when no API key."""
        monkeypatch.delenv("MESHY_API_KEY", raising=False)
        connector = MeshyConnector()

        with pytest.raises(ValueError, match="MESHY_API_KEY not set"):
            connector._validate_api_key()

    def test_validate_api_key_passes_with_key(self):
        """Test that validation passes with API key."""
        connector = MeshyConnector(api_key="test-key")
        connector._validate_api_key()  # Should not raise


class TestTaskResult:
    """Tests for TaskResult dataclass."""

    def test_task_result_defaults(self):
        """Test TaskResult default values."""
        result = TaskResult(task_id="test-123", task_type="text-to-3d")
        assert result.task_id == "test-123"
        assert result.task_type == "text-to-3d"
        assert result.status == TaskStatus.PENDING
        assert result.progress == 0
        assert result.model_url is None
        assert result.error is None

    def test_task_result_with_values(self):
        """Test TaskResult with all values."""
        result = TaskResult(
            task_id="test-123",
            task_type="text-to-3d",
            status=TaskStatus.SUCCEEDED,
            progress=100,
            model_url="https://example.com/model.glb",
            thumbnail_url="https://example.com/thumb.png",
        )
        assert result.status == TaskStatus.SUCCEEDED
        assert result.progress == 100
        assert result.model_url == "https://example.com/model.glb"


class TestMeshyConnectorTextTo3D:
    """Tests for text_to_3d method."""

    @patch("vendor_connectors.meshy.text3d.generate")
    def test_text_to_3d_blocking(self, mock_generate):
        """Test text_to_3d with wait=True."""
        mock_result = Text3DResult(
            id="task-123",
            status=TaskStatus.SUCCEEDED,
            progress=100,
            created_at=1700000000,
            model_urls=ModelUrls(glb="https://example.com/model.glb"),
            thumbnail_url="https://example.com/thumb.png",
        )
        mock_generate.return_value = mock_result

        connector = MeshyConnector(api_key="test-key")
        result = connector.text_to_3d("A medieval sword", wait=True)

        assert result.task_id == "task-123"
        assert result.status == TaskStatus.SUCCEEDED
        assert result.model_url == "https://example.com/model.glb"
        mock_generate.assert_called_once()

    @patch("vendor_connectors.meshy.text3d.create")
    def test_text_to_3d_non_blocking(self, mock_create):
        """Test text_to_3d with wait=False."""
        mock_create.return_value = "task-456"

        connector = MeshyConnector(api_key="test-key")
        result = connector.text_to_3d("A medieval sword", wait=False)

        assert result.task_id == "task-456"
        assert result.status == TaskStatus.PENDING
        mock_create.assert_called_once()


class TestMeshyConnectorRigging:
    """Tests for rig_model method."""

    @patch("vendor_connectors.meshy.rigging.rig")
    def test_rig_model_blocking(self, mock_rig):
        """Test rig_model with wait=True."""
        mock_result = RiggingResult(
            id="rig-123",
            status=TaskStatus.SUCCEEDED,
            progress=100,
            created_at=1700000000,
            result=RiggingResultData(rigged_character_glb_url="https://example.com/rigged.glb"),
        )
        mock_rig.return_value = mock_result

        connector = MeshyConnector(api_key="test-key")
        result = connector.rig_model("model-task-123", wait=True)

        assert result.task_id == "rig-123"
        assert result.status == TaskStatus.SUCCEEDED
        assert result.model_url == "https://example.com/rigged.glb"

    @patch("vendor_connectors.meshy.rigging.rig")
    def test_rig_model_non_blocking(self, mock_rig):
        """Test rig_model with wait=False."""
        mock_rig.return_value = "rig-456"

        connector = MeshyConnector(api_key="test-key")
        result = connector.rig_model("model-task-123", wait=False)

        assert result.task_id == "rig-456"
        assert result.status == TaskStatus.PENDING


class TestMeshyConnectorAnimation:
    """Tests for apply_animation method."""

    @patch("vendor_connectors.meshy.animate.apply")
    def test_apply_animation_blocking(self, mock_apply):
        """Test apply_animation with wait=True."""
        mock_result = AnimationResult(
            id="anim-123",
            status=TaskStatus.SUCCEEDED,
            progress=100,
            created_at=1700000000,
            animation_glb_url="https://example.com/anim.glb",
        )
        mock_apply.return_value = mock_result

        connector = MeshyConnector(api_key="test-key")
        result = connector.apply_animation("rig-123", animation_id=5, wait=True)

        assert result.task_id == "anim-123"
        assert result.status == TaskStatus.SUCCEEDED
        assert result.model_url == "https://example.com/anim.glb"


class TestMeshyConnectorRetexture:
    """Tests for retexture_model method."""

    @patch("vendor_connectors.meshy.retexture.apply")
    def test_retexture_model_blocking(self, mock_apply):
        """Test retexture_model with wait=True."""
        mock_result = RetextureResult(
            id="retex-123",
            status=TaskStatus.SUCCEEDED,
            progress=100,
            created_at=1700000000,
            model_urls=ModelUrls(glb="https://example.com/retextured.glb"),
        )
        mock_apply.return_value = mock_result

        connector = MeshyConnector(api_key="test-key")
        result = connector.retexture_model("model-123", "golden with gems", wait=True)

        assert result.task_id == "retex-123"
        assert result.status == TaskStatus.SUCCEEDED


class TestMeshyConnectorGetTask:
    """Tests for get_task method."""

    @patch("vendor_connectors.meshy.text3d.get")
    def test_get_task_text3d(self, mock_get):
        """Test get_task for text-to-3d task."""
        mock_result = Text3DResult(
            id="task-123",
            status=TaskStatus.IN_PROGRESS,
            progress=50,
            created_at=1700000000,
        )
        mock_get.return_value = mock_result

        connector = MeshyConnector(api_key="test-key")
        result = connector.get_task("task-123", task_type="text-to-3d")

        assert result.task_id == "task-123"
        assert result.status == TaskStatus.IN_PROGRESS
        assert result.progress == 50

    def test_get_task_unknown_type(self):
        """Test get_task with unknown task type."""
        connector = MeshyConnector(api_key="test-key")

        with pytest.raises(ValueError, match="Unknown task type"):
            connector.get_task("task-123", task_type="unknown")


class TestMeshyConnectorDownload:
    """Tests for download_model method."""

    @patch("httpx.get")
    @patch("vendor_connectors.meshy.text3d.get")
    def test_download_model(self, mock_get, mock_httpx_get):
        """Test download_model."""
        mock_result = Text3DResult(
            id="task-123",
            status=TaskStatus.SUCCEEDED,
            progress=100,
            created_at=1700000000,
            model_urls=ModelUrls(glb="https://example.com/model.glb"),
        )
        mock_get.return_value = mock_result

        mock_response = MagicMock()
        mock_response.content = b"model binary data"
        mock_httpx_get.return_value = mock_response

        connector = MeshyConnector(api_key="test-key")
        model_bytes = connector.download_model("task-123", format="glb")

        assert model_bytes == b"model binary data"
        mock_httpx_get.assert_called_once_with("https://example.com/model.glb")

    @patch("vendor_connectors.meshy.text3d.get")
    def test_download_model_not_complete(self, mock_get):
        """Test download_model when task not complete."""
        mock_result = Text3DResult(
            id="task-123",
            status=TaskStatus.IN_PROGRESS,
            progress=50,
            created_at=1700000000,
        )
        mock_get.return_value = mock_result

        connector = MeshyConnector(api_key="test-key")

        with pytest.raises(ValueError, match="Task task-123 not complete"):
            connector.download_model("task-123", format="glb")


class TestMeshyConnectorContextManager:
    """Tests for context manager support."""

    @patch("vendor_connectors.meshy.base.close")
    def test_context_manager(self, mock_close):
        """Test using MeshyConnector as context manager."""
        with MeshyConnector(api_key="test-key") as connector:
            assert connector.api_key == "test-key"

        mock_close.assert_called_once()


class TestVendorConnectorsIntegration:
    """Tests for VendorConnectors.get_meshy_client()."""

    def test_get_meshy_client(self):
        """Test VendorConnectors.get_meshy_client."""
        from vendor_connectors import VendorConnectors

        vc = VendorConnectors()
        meshy = vc.get_meshy_client(api_key="test-key")

        assert isinstance(meshy, MeshyConnector)
        assert meshy.api_key == "test-key"

    def test_get_meshy_client_cached(self):
        """Test that get_meshy_client returns cached instance."""
        from vendor_connectors import VendorConnectors

        vc = VendorConnectors()
        meshy1 = vc.get_meshy_client(api_key="test-key")
        meshy2 = vc.get_meshy_client(api_key="test-key")

        assert meshy1 is meshy2
