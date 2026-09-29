"""
Unit and Integration Tests for Speculative Model Cascading
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer (Stretch Feature)
"""

import unittest
from model_router.registry_manager import ModelRegistryManager
from model_router.cascade import ModelCascader, CascadeResult
from model_router.adapters import MockAdapter


class TestModelCascader(unittest.TestCase):

    def setUp(self):
        self.registry = ModelRegistryManager()
        # Set up mock draft and flagship models
        self.draft_ad = MockAdapter("draft_7b", {"simulated_latency_sec": 0.001})
        self.flagship_ad = MockAdapter("flagship_32b", {"simulated_latency_sec": 0.001})

        self.registry._active_adapters["draft_7b"] = self.draft_ad
        self.registry._active_adapters["flagship_32b"] = self.flagship_ad

        self.cascader = ModelCascader(
            registry_manager=self.registry,
            draft_model_id="draft_7b",
            flagship_model_id="flagship_32b",
            confidence_threshold=0.85,
        )

    def test_draft_served_fast_path(self):
        """Standard query should be answered by the draft model to conserve compute."""
        result = self.cascader.run_cascaded("Summarize shift notes for crude pump")
        self.assertFalse(result.escalated)
        self.assertEqual(result.response.model_id, "draft_7b")
        self.assertGreater(result.tokens_saved, 0)
        self.assertGreaterEqual(result.draft_confidence, 0.85)

    def test_safety_critical_keyword_escalation(self):
        """Prompt containing high-risk industrial safety keywords must escalate directly."""
        result = self.cascader.run_cascaded(
            "Execute emergency shutdown sequence for hydrocracker high-pressure alarm"
        )
        self.assertTrue(result.escalated)
        self.assertEqual(result.response.model_id, "flagship_32b")
        self.assertIn("Safety-Critical Policy", result.decision_reason)

    def test_cascade_metrics_tracking(self):
        """Verify performance metrics aggregation across calls."""
        # 1 standard call
        self.cascader.run_cascaded("Simple query 1")
        # 1 safety call
        self.cascader.run_cascaded("sil-3 emergency shutdown protocol")

        metrics = self.cascader.get_metrics()
        self.assertEqual(metrics["total_requests"], 2)
        self.assertEqual(metrics["escalation_count"], 1)
        self.assertEqual(metrics["fast_path_served"], 1)
        self.assertEqual(metrics["escalation_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
