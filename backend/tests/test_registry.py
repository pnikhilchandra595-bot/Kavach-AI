"""
Unit and Integration Tests for Model Registry and Rollback
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

from model_router.registry_manager import (
    ModelRegistryManager,
    RegistryValidationError,
    ModelNotFoundError,
    VersionRollbackError,
)


class TestModelRegistryManager(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory to isolate test registry and history
        self.test_dir = tempfile.mkdtemp()
        self.registry_file = Path(self.test_dir) / "model_registry.yaml"
        self.history_dir = Path(self.test_dir) / "history"

        # Copy original registry to temp file
        original_registry = Path(__file__).parent.parent / "model_router" / "model_registry.yaml"
        shutil.copy2(original_registry, self.registry_file)

        self.manager = ModelRegistryManager(
            registry_path=str(self.registry_file),
            history_dir=str(self.history_dir),
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_registry_loading_and_version(self):
        """Verify registry loads successfully and extracts version metadata."""
        version = self.manager.get_registry_version()
        self.assertTrue(len(version) > 0)
        models = self.manager.list_models()
        self.assertGreaterEqual(len(models), 4)

    def test_hardware_tier_detection(self):
        """Verify hardware tier classification and degraded mode detection."""
        # Force low VRAM (e.g., 4096 MB)
        self.manager.system_vram_mb = 4096
        self.manager._detect_hardware()
        self.assertTrue(self.manager.reduced_capacity_mode)
        self.assertEqual(self.manager.get_hardware_tier(), "degraded")

        # Force high VRAM (e.g., 24576 MB)
        self.manager.system_vram_mb = 24576
        self.manager.reduced_capacity_mode = False
        self.assertEqual(self.manager.get_hardware_tier(), "recommended")

    def test_get_model_success_and_missing(self):
        """Test model retrieval and ModelNotFoundError on missing ID."""
        model = self.manager.get_model("qwen2.5-14b-q4")
        self.assertEqual(model["family"], "qwen")
        self.assertEqual(model["adapter"], "ollama")

        with self.assertRaises(ModelNotFoundError):
            self.manager.get_model("non_existent_model_999")

    def test_task_filtering(self):
        """Test retrieving models capable of specific refinery tasks."""
        coding_models = self.manager.get_models_for_task("coding", strict_hardware=False)
        self.assertTrue(any("coder" in m["model_id"] for m in coding_models))

        vision_models = self.manager.get_models_for_task("vision_ocr", strict_hardware=False)
        self.assertTrue(any("vl" in m["model_id"] or "llava" in m["model_id"] for m in vision_models))

    def test_version_update_and_rollback(self):
        """Test updating model parameter, creating history snapshot, and rolling back."""
        initial_version = self.manager.get_registry_version()

        # Update context window on a model
        new_version = self.manager.update_model_param(
            model_id="qwen2.5-7b-q4",
            updates={"context_window": 12000},
            author="engineer_test",
            reason="Increase context for distillation log processing",
        )
        self.assertNotEqual(initial_version, new_version)

        # Verify change took effect
        updated_model = self.manager.get_model("qwen2.5-7b-q4")
        self.assertEqual(updated_model["context_window"], 12000)

        # Verify history was recorded
        history = self.manager.list_version_history()
        self.assertGreaterEqual(len(history), 1)

        # Execute rollback to initial version
        rollback_res = self.manager.rollback_to_version(initial_version, author="supervisor_test")
        self.assertEqual(rollback_res["status"], "ROLLBACK_SUCCESSFUL")
        self.assertEqual(rollback_res["restored_version"], initial_version)

        # Verify model param is restored to original
        restored_model = self.manager.get_model("qwen2.5-7b-q4")
        self.assertEqual(restored_model["context_window"], 8192)


if __name__ == "__main__":
    unittest.main()
