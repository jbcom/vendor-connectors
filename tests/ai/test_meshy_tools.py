"""Tests for vendor_connectors.ai.tools.meshy_tools module.

Tests tool registration and handlers with mocked Meshy API calls.
"""

import json
from unittest.mock import MagicMock, patch

from vendor_connectors.ai.base import ToolCategory, ToolDefinition


class TestMeshyToolsRegistration:
    """Tests for Meshy tool registration."""

    def setup_method(self):
        """Reset tool registration state for each test."""
        # Import and reset the registration state
        import vendor_connectors.ai.tools.meshy_tools as mt

        mt._tools_registered = False
        # Also reset the global registry
        from vendor_connectors.ai.base import _registry

        _registry._tools.clear()

    def test_get_meshy_tools_returns_list(self):
        """Test that get_meshy_tools returns a list of tool definitions."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0

    def test_get_meshy_tools_all_are_tool_definitions(self):
        """Test that all returned items are ToolDefinition instances."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()
        for tool in tools:
            assert isinstance(tool, ToolDefinition)

    def test_expected_tools_are_registered(self):
        """Test that expected Meshy tools are available."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()
        tool_names = {t.name for t in tools}

        expected_tools = {
            "text3d_generate",
            "image3d_generate",
            "rig_model",
            "apply_animation",
            "retexture_model",
            "list_animations",
            "check_task_status",
            "get_animation",
        }

        for expected in expected_tools:
            assert expected in tool_names, f"Expected tool '{expected}' not found"

    def test_tools_have_correct_categories(self):
        """Test that tools have appropriate categories."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()

        # Map tool names to expected categories
        expected_categories = {
            "text3d_generate": ToolCategory.GENERATION,
            "image3d_generate": ToolCategory.GENERATION,
            "rig_model": ToolCategory.RIGGING,
            "apply_animation": ToolCategory.ANIMATION,
            "retexture_model": ToolCategory.TEXTURING,
            "list_animations": ToolCategory.UTILITY,
            "check_task_status": ToolCategory.UTILITY,
            "get_animation": ToolCategory.UTILITY,
        }

        for tool in tools:
            if tool.name in expected_categories:
                assert tool.category == expected_categories[tool.name], (
                    f"Tool {tool.name} has category {tool.category}, expected {expected_categories[tool.name]}"
                )

    def test_tools_have_handlers(self):
        """Test that all tools have callable handlers."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()
        for tool in tools:
            assert callable(tool.handler), f"Tool {tool.name} handler is not callable"

    def test_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()
        for tool in tools:
            assert tool.description, f"Tool {tool.name} has no description"
            assert len(tool.description) > 10, f"Tool {tool.name} description is too short"

    def test_registration_is_idempotent(self):
        """Test that calling get_meshy_tools multiple times doesn't duplicate."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools1 = get_meshy_tools()
        tools2 = get_meshy_tools()

        assert len(tools1) == len(tools2)

    def test_thread_safe_registration(self):
        """Test that registration is thread-safe."""
        import threading

        from vendor_connectors.ai.tools.meshy_tools import _ensure_tools_registered

        results = []
        errors = []

        def register():
            try:
                _ensure_tools_registered()
                results.append(True)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=register) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10


class TestText3DGenerateHandler:
    """Tests for text3d_generate handler."""

    def test_successful_generation(self):
        """Test successful 3D model generation."""
        from vendor_connectors.ai.tools.meshy_tools import handle_text3d_generate

        # Mock the meshy module
        mock_result = MagicMock()
        mock_result.id = "task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/model.glb"
        mock_result.thumbnail_url = "https://example.com/thumb.png"

        with patch("vendor_connectors.meshy.text3d.generate", return_value=mock_result):
            result = handle_text3d_generate(
                prompt="a medieval sword",
                art_style="realistic",
            )

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["task_id"] == "task_123"
        assert "model_url" in parsed["data"]

    def test_generation_failure(self):
        """Test handling of generation failure."""
        from vendor_connectors.ai.tools.meshy_tools import handle_text3d_generate

        with patch("vendor_connectors.meshy.text3d.generate", side_effect=Exception("API Error")):
            result = handle_text3d_generate(prompt="test")

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "API Error" in parsed["error"]


class TestImage3DGenerateHandler:
    """Tests for image3d_generate handler."""

    def test_successful_image_to_3d(self):
        """Test successful image-to-3D generation."""
        from vendor_connectors.ai.tools.meshy_tools import handle_image3d_generate

        mock_result = MagicMock()
        mock_result.id = "img_task_456"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/img_model.glb"
        mock_result.thumbnail_url = None

        with patch("vendor_connectors.meshy.image3d.generate", return_value=mock_result):
            result = handle_image3d_generate(
                image_url="https://example.com/image.png",
                topology="quad",
            )

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["task_id"] == "img_task_456"

    def test_image_generation_failure(self):
        """Test handling of image generation failure."""
        from vendor_connectors.ai.tools.meshy_tools import handle_image3d_generate

        with patch("vendor_connectors.meshy.image3d.generate", side_effect=ValueError("Invalid URL")):
            result = handle_image3d_generate(image_url="bad-url")

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "Invalid URL" in parsed["error"]


class TestRigModelHandler:
    """Tests for rig_model handler."""

    def test_successful_rigging_with_wait(self):
        """Test successful model rigging with wait=True."""
        from vendor_connectors.ai.tools.meshy_tools import handle_rig_model

        mock_result = MagicMock()
        mock_result.id = "rig_789"
        mock_result.status.value = "SUCCEEDED"

        with patch("vendor_connectors.meshy.rigging.rig", return_value=mock_result):
            result = handle_rig_model(model_id="model_123", wait=True)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["task_id"] == "rig_789"
        assert "Rigging completed" in parsed["data"]["message"]

    def test_rigging_without_wait(self):
        """Test model rigging with wait=False."""
        from vendor_connectors.ai.tools.meshy_tools import handle_rig_model

        # When wait=False, rigging.rig returns just the task_id string
        with patch("vendor_connectors.meshy.rigging.rig", return_value="pending_rig_task"):
            result = handle_rig_model(model_id="model_123", wait=False)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["status"] == "pending"

    def test_rigging_failure(self):
        """Test handling of rigging failure."""
        from vendor_connectors.ai.tools.meshy_tools import handle_rig_model

        with patch("vendor_connectors.meshy.rigging.rig", side_effect=Exception("Rigging failed")):
            result = handle_rig_model(model_id="bad_model")

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "Rigging failed" in parsed["error"]


class TestApplyAnimationHandler:
    """Tests for apply_animation handler."""

    def test_successful_animation(self):
        """Test successful animation application."""
        from vendor_connectors.ai.tools.meshy_tools import handle_apply_animation

        mock_result = MagicMock()
        mock_result.id = "anim_task_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.animation_glb_url = "https://example.com/animated.glb"

        with patch("vendor_connectors.meshy.animate.apply", return_value=mock_result):
            result = handle_apply_animation(
                model_id="rigged_model",
                animation_id=42,
                wait=True,
            )

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["glb_url"] == "https://example.com/animated.glb"

    def test_animation_without_wait(self):
        """Test animation without waiting."""
        from vendor_connectors.ai.tools.meshy_tools import handle_apply_animation

        with patch("vendor_connectors.meshy.animate.apply", return_value="anim_pending"):
            result = handle_apply_animation(
                model_id="model",
                animation_id=1,
                wait=False,
            )

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["status"] == "pending"


class TestRetextureModelHandler:
    """Tests for retexture_model handler."""

    def test_successful_retexture(self):
        """Test successful retexturing."""
        from vendor_connectors.ai.tools.meshy_tools import handle_retexture_model

        mock_result = MagicMock()
        mock_result.id = "retex_123"
        mock_result.status.value = "SUCCEEDED"
        mock_result.model_url = "https://example.com/retextured.glb"

        with patch("vendor_connectors.meshy.retexture.apply", return_value=mock_result):
            result = handle_retexture_model(
                model_id="original_model",
                texture_prompt="golden metallic finish",
            )

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["task_id"] == "retex_123"


class TestListAnimationsHandler:
    """Tests for list_animations handler."""

    def test_list_all_animations(self):
        """Test listing all animations."""
        from vendor_connectors.ai.tools.meshy_tools import handle_list_animations

        # Create mock animations
        mock_anim_1 = MagicMock()
        mock_anim_1.id = 1
        mock_anim_1.name = "Walk"
        mock_anim_1.category = "Movement"
        mock_anim_1.subcategory = "Basic"

        mock_anim_2 = MagicMock()
        mock_anim_2.id = 2
        mock_anim_2.name = "Run"
        mock_anim_2.category = "Movement"
        mock_anim_2.subcategory = "Basic"

        mock_animations = {1: mock_anim_1, 2: mock_anim_2}

        with patch("vendor_connectors.meshy.animations.ANIMATIONS", mock_animations):
            result = handle_list_animations()

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["count"] == 2
        assert len(parsed["data"]["animations"]) == 2

    def test_list_animations_with_category_filter(self):
        """Test listing animations with category filter."""
        from vendor_connectors.ai.tools.meshy_tools import handle_list_animations

        mock_anim_fight = MagicMock()
        mock_anim_fight.id = 1
        mock_anim_fight.name = "Punch"
        mock_anim_fight.category = "Fighting"
        mock_anim_fight.subcategory = "Combat"

        mock_anim_walk = MagicMock()
        mock_anim_walk.id = 2
        mock_anim_walk.name = "Walk"
        mock_anim_walk.category = "Movement"
        mock_anim_walk.subcategory = "Basic"

        mock_animations = {1: mock_anim_fight, 2: mock_anim_walk}

        with patch("vendor_connectors.meshy.animations.ANIMATIONS", mock_animations):
            result = handle_list_animations(category="Fighting")

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["count"] == 1
        assert parsed["data"]["animations"][0]["name"] == "Punch"

    def test_list_animations_with_limit(self):
        """Test listing animations with limit."""
        from vendor_connectors.ai.tools.meshy_tools import handle_list_animations

        mock_animations = {}
        for i in range(100):
            mock_anim = MagicMock()
            mock_anim.id = i
            mock_anim.name = f"Animation_{i}"
            mock_anim.category = "Test"
            mock_anim.subcategory = "Test"
            mock_animations[i] = mock_anim

        with patch("vendor_connectors.meshy.animations.ANIMATIONS", mock_animations):
            result = handle_list_animations(limit=10)

        parsed = json.loads(result)
        assert parsed["data"]["count"] == 10
        assert parsed["data"]["total"] == 100


class TestCheckTaskStatusHandler:
    """Tests for check_task_status handler."""

    def test_check_text3d_status(self):
        """Test checking text-to-3D task status."""
        from vendor_connectors.ai.tools.meshy_tools import handle_check_task_status

        mock_result = MagicMock()
        mock_result.status.value = "SUCCEEDED"
        mock_result.progress = 100
        mock_result.model_urls = MagicMock()
        mock_result.model_urls.glb = "https://example.com/model.glb"

        with patch("vendor_connectors.meshy.text3d.get", return_value=mock_result):
            result = handle_check_task_status(
                task_id="task_123",
                task_type="text-to-3d",
            )

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["status"] == "SUCCEEDED"
        assert parsed["data"]["progress"] == 100

    def test_check_unknown_task_type(self):
        """Test checking unknown task type."""
        from vendor_connectors.ai.tools.meshy_tools import handle_check_task_status

        result = handle_check_task_status(
            task_id="task_123",
            task_type="invalid-type",
        )

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "Unknown task type" in parsed["error"]


class TestGetAnimationHandler:
    """Tests for get_animation handler."""

    def test_get_existing_animation(self):
        """Test getting an existing animation."""
        from vendor_connectors.ai.tools.meshy_tools import handle_get_animation_by_id

        mock_anim = MagicMock()
        mock_anim.id = 42
        mock_anim.name = "Dance"
        mock_anim.category = "Dancing"
        mock_anim.subcategory = "Casual"
        mock_anim.preview_url = "https://example.com/preview.gif"

        with patch("vendor_connectors.meshy.animations.ANIMATIONS", {42: mock_anim}):
            result = handle_get_animation_by_id(animation_id=42)

        parsed = json.loads(result)
        assert parsed["success"] is True
        assert parsed["data"]["name"] == "Dance"
        assert parsed["data"]["preview_url"] == "https://example.com/preview.gif"

    def test_get_nonexistent_animation(self):
        """Test getting a nonexistent animation."""
        from vendor_connectors.ai.tools.meshy_tools import handle_get_animation_by_id

        with patch("vendor_connectors.meshy.animations.ANIMATIONS", {}):
            result = handle_get_animation_by_id(animation_id=999)

        parsed = json.loads(result)
        assert parsed["success"] is False
        assert "not found" in parsed["error"]


class TestToolParameters:
    """Tests for tool parameter definitions."""

    def test_text3d_generate_parameters(self):
        """Test text3d_generate has correct parameters."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()
        text3d_tool = next((t for t in tools if t.name == "text3d_generate"), None)

        assert text3d_tool is not None
        params = text3d_tool.parameters

        # Check required parameter
        assert "prompt" in params
        assert params["prompt"].required is True
        assert params["prompt"].type is str

        # Check optional parameters with defaults
        assert "art_style" in params
        assert params["art_style"].required is False
        assert params["art_style"].enum_values is not None
        assert "realistic" in params["art_style"].enum_values

    def test_rig_model_parameters(self):
        """Test rig_model has correct parameters."""
        from vendor_connectors.ai.tools.meshy_tools import get_meshy_tools

        tools = get_meshy_tools()
        rig_tool = next((t for t in tools if t.name == "rig_model"), None)

        assert rig_tool is not None
        params = rig_tool.parameters

        assert "model_id" in params
        assert params["model_id"].required is True

        assert "wait" in params
        assert params["wait"].required is False
        assert params["wait"].default is True
