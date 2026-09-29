"""
Unit and Integration Tests for Resilient Fallback Policy
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer
"""

import unittest
from model_router.registry_manager import ModelRegistryManager
from model_router.fallback_policy import (
    FallbackPolicyEngine,
    FallbackExhaustedError,
    FallbackEvent,
)
from model_router.adapters import MockAdapter, OutOfMemoryError, ModelUnavailableError


class TestFallbackPolicy(unittest.TestCase):

    def setUp(self):
        self.registry = ModelRegistryManager()
        self.engine = FallbackPolicyEngine(self.registry)

        # Set up a deterministic mock fallback chain
        self.engine.set_chain("test_task", ["m_primary", "m_secondary", "m_tertiary"])

        # Inject mock adapters into registry
        self.ad_primary = MockAdapter("m_primary", {"simulated_latency_sec": 0.001})
        self.ad_secondary = MockAdapter("m_secondary", {"simulated_latency_sec": 0.001})
        self.ad_tertiary = MockAdapter("m_tertiary", {"simulated_latency_sec": 0.001})

        self.registry._active_adapters["m_primary"] = self.ad_primary
        self.registry._active_adapters["m_secondary"] = self.ad_secondary
        self.registry._active_adapters["m_tertiary"] = self.ad_tertiary

    def test_successful_primary_execution(self):
        """When primary model is healthy, no fallback occurs."""
        resp, events = self.engine.execute_with_fallback(
            task_type="test_task",
            inference_callable=lambda ad: ad.generate("Hello refinery"),
        )
        self.assertEqual(resp.model_id, "m_primary")
        self.assertFalse(resp.is_fallback)
        self.assertEqual(len(events), 0)

    def test_oom_failover(self):
        """When primary model triggers OOM, engine falls back to secondary model."""
        # Inject OOM fault into primary model
        self.ad_primary.set_fault_injection(oom=True)

        resp, events = self.engine.execute_with_fallback(
            task_type="test_task",
            inference_callable=lambda ad: ad.generate("Run complex planning"),
        )

        # Execution must have succeeded on secondary model
        self.assertEqual(resp.model_id, "m_secondary")
        self.assertTrue(resp.is_fallback)
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.failed_model, "m_primary")
        self.assertEqual(event.failover_model, "m_secondary")
        self.assertIn("out of memory", event.failure_reason.lower())

    def test_kill_model_simulation(self):
        """Simulate killing the preferred model and verify instant failover with audit trail."""
        self.engine.kill_model("m_primary")
        self.assertTrue(self.engine.is_killed("m_primary"))

        resp, events = self.engine.execute_with_fallback(
            task_type="test_task",
            inference_callable=lambda ad: ad.generate("Generate shutdown procedure"),
        )

        self.assertEqual(resp.model_id, "m_secondary")
        self.assertTrue(resp.is_fallback)
        self.assertEqual(len(events), 1)
        self.assertIn("kill-switch", events[0].failure_reason.lower())

        # Verify audit trail contains the event
        trail = self.engine.get_audit_trail()
        self.assertGreaterEqual(len(trail), 1)
        self.assertEqual(trail[-1]["failed_model"], "m_primary")

    def test_cascade_exhaustion(self):
        """When all models in the chain fail, FallbackExhaustedError is raised."""
        self.ad_primary.set_fault_injection(crash=True)
        self.ad_secondary.set_fault_injection(oom=True)
        self.ad_tertiary.set_fault_injection(crash=True)

        with self.assertRaises(FallbackExhaustedError) as ctx:
            self.engine.execute_with_fallback(
                task_type="test_task",
                inference_callable=lambda ad: ad.generate("Mission critical query"),
            )

        err = ctx.exception
        self.assertEqual(err.task_type, "test_task")
        self.assertEqual(len(err.attempted_models), 3)

    def test_coding_chain_fallback_to_qwen_1_5b(self):
        """Verify that a failure on qwen2.5-coder-14b falls back directly to qwen2.5-coder-1.5b."""
        self.engine.kill_model("qwen2.5-coder-14b")
        resp, events = self.engine.execute_with_fallback(
            task_type="coding",
            inference_callable=lambda ad: ad.generate("Write Python check"),
            preferred_model="qwen2.5-coder-14b",
        )
        self.assertEqual(resp.model_id, "qwen2.5-coder-1.5b")
        self.assertTrue(resp.is_fallback)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].failed_model, "qwen2.5-coder-14b")
        self.assertEqual(events[0].failover_model, "qwen2.5-coder-1.5b")
        self.assertLess(events[0].failover_latency_ms, 50.0)


if __name__ == "__main__":
    unittest.main()
