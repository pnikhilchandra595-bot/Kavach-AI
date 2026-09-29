"""
Unit and Integration Tests for Concurrent Load Profiler
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer (Stretch Feature)
"""

import unittest
from observability.eval_harness.load_test import ConcurrentLoadProfiler, SLA_BUDGETS


class TestLoadProfiler(unittest.TestCase):

    def setUp(self):
        self.profiler = ConcurrentLoadProfiler()

    def test_load_profile_execution(self):
        """Verify concurrent multi-worker load execution and metric aggregation."""
        report = self.profiler.run_load_profile(concurrency=4, total_requests=8)
        summary = report.get("load_test_summary", {})

        self.assertEqual(summary.get("concurrency_level"), 4)
        self.assertEqual(summary.get("total_requests"), 8)
        self.assertGreater(summary.get("throughput_requests_per_sec", 0), 0)
        self.assertGreaterEqual(summary.get("latency_p50_ms", -1), 0)
        self.assertGreaterEqual(summary.get("latency_p95_ms", -1), 0)
        self.assertGreaterEqual(summary.get("sla_compliance_rate", -1), 0)

    def test_sla_budgets_defined(self):
        """Ensure all required industrial task types have registered SLA targets."""
        required_tasks = ["vision_ocr", "coding", "summarization", "planning", "sop_qa"]
        for t in required_tasks:
            self.assertIn(t, SLA_BUDGETS)
            self.assertGreater(SLA_BUDGETS[t].target_max_latency_ms, 0)


if __name__ == "__main__":
    unittest.main()
