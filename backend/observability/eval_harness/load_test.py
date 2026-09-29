"""
Concurrent-Load Profiling and SLA Budget Compliance Harness
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer (Stretch Feature, in collaboration with P6)

Simulates multi-operator concurrent load across refinery shift workstations.
Profiles throughput (req/sec), queue latency (P50, P95, P99), and flags SLA breaches:
- OCR / Vision Extraction SLA : < 5,000 ms
- Code Sandboxing SLA         : < 10,000 ms
- Drafting / Summarization SLA: < 15,000 ms
"""

import time
import math
import statistics
import concurrent.futures
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from pathlib import Path
import sys

# Ensure root sovereign-workbench is in python path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from model_router.registry_manager import ModelRegistryManager
from model_router.fallback_policy import FallbackPolicyEngine


@dataclass
class SLABudget:
    task_type: str
    target_max_latency_ms: float
    target_min_tps: float


SLA_BUDGETS = {
    "vision_ocr": SLABudget("vision_ocr", target_max_latency_ms=5000.0, target_min_tps=10.0),
    "coding": SLABudget("coding", target_max_latency_ms=10000.0, target_min_tps=15.0),
    "summarization": SLABudget("summarization", target_max_latency_ms=15000.0, target_min_tps=20.0),
    "planning": SLABudget("planning", target_max_latency_ms=15000.0, target_min_tps=15.0),
    "sop_qa": SLABudget("sop_qa", target_max_latency_ms=8000.0, target_min_tps=20.0),
}


class ConcurrentLoadProfiler:
    """Profiles multi-threaded concurrent task dispatch and detects SLA violations."""

    def __init__(self, registry_manager: Optional[ModelRegistryManager] = None):
        self.registry = registry_manager or ModelRegistryManager()
        # Pre-seed mock adapters so concurrent load testing operates deterministically offline
        from model_router.adapters.mock_adapter import MockAdapter
        for mid in list(self.registry._raw_config.get("models", {}).keys()):
            if mid not in self.registry._active_adapters:
                self.registry._active_adapters[mid] = MockAdapter(mid, {"simulated_latency_sec": 0.002})
        self.fallback_engine = FallbackPolicyEngine(self.registry)

    def _execute_single_request(self, task_type: str, prompt: str) -> Dict[str, Any]:
        start = time.perf_counter()
        resp, events = self.fallback_engine.execute_with_fallback(
            task_type=task_type,
            inference_callable=lambda adapter: adapter.generate(prompt),
        )
        latency_ms = (time.perf_counter() - start) * 1000.0

        budget = SLA_BUDGETS.get(task_type, SLABudget(task_type, 15000.0, 10.0))
        breached = latency_ms > budget.target_max_latency_ms

        return {
            "task_type": task_type,
            "latency_ms": latency_ms,
            "model_id": resp.model_id,
            "tokens": resp.usage.total_tokens,
            "tps": resp.usage.tokens_per_second,
            "is_fallback": resp.is_fallback,
            "sla_budget_ms": budget.target_max_latency_ms,
            "sla_breached": breached,
        }

    def run_load_profile(
        self,
        concurrency: int = 8,
        total_requests: int = 24,
    ) -> Dict[str, Any]:
        tasks = [
            ("vision_ocr", "Extract P&ID equipment tags for pump 10-P-101A"),
            ("coding", "Generate SQL query for DCS temperature sensor threshold alarms"),
            ("summarization", "Summarize night shift log for Coker Unit 2"),
            ("planning", "Plan isolation and hot work permits for Heat Exchanger E-102"),
            ("sop_qa", "Look up SRU tail gas safety shutdown interlocks"),
        ]

        # Build task list round-robin
        workload = [tasks[i % len(tasks)] for i in range(total_requests)]

        results: List[Dict[str, Any]] = []
        wall_clock_start = time.perf_counter()

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_to_req = {
                executor.submit(self._execute_single_request, t_type, prompt): (t_type, prompt)
                for t_type, prompt in workload
            }
            for future in concurrent.futures.as_completed(future_to_req):
                res = future.result()
                results.append(res)

        total_wall_clock_sec = time.perf_counter() - wall_clock_start
        latencies = [r["latency_ms"] for r in results]
        latencies.sort()

        p50 = statistics.median(latencies) if latencies else 0.0
        p95_idx = int(math.ceil(0.95 * len(latencies))) - 1
        p99_idx = int(math.ceil(0.99 * len(latencies))) - 1
        p95 = latencies[min(max(0, p95_idx), len(latencies) - 1)] if latencies else 0.0
        p99 = latencies[min(max(0, p99_idx), len(latencies) - 1)] if latencies else 0.0

        throughput_rps = (total_requests / total_wall_clock_sec) if total_wall_clock_sec > 0 else 0.0
        sla_breaches = [r for r in results if r["sla_breached"]]

        return {
            "load_test_summary": {
                "concurrency_level": concurrency,
                "total_requests": total_requests,
                "wall_clock_seconds": round(total_wall_clock_sec, 3),
                "throughput_requests_per_sec": round(throughput_rps, 2),
                "latency_p50_ms": round(p50, 2),
                "latency_p95_ms": round(p95, 2),
                "latency_p99_ms": round(p99, 2),
                "sla_breach_count": len(sla_breaches),
                "sla_compliance_rate": round(((total_requests - len(sla_breaches)) / total_requests) * 100.0, 2),
            },
            "sla_breaches": sla_breaches,
            "sample_results": results[:5],
        }


if __name__ == "__main__":
    profiler = ConcurrentLoadProfiler()
    print("Running Multi-Operator Concurrent Load Profile...")
    report = profiler.run_load_profile(concurrency=6, total_requests=18)
    summary = report["load_test_summary"]
    print("=" * 65)
    print("CONCURRENT LOAD PROFILING & SLA COMPLIANCE REPORT (P2)")
    print("=" * 65)
    print(f"Concurrency Level : {summary['concurrency_level']} concurrent operators")
    print(f"Total Requests    : {summary['total_requests']}")
    print(f"Throughput        : {summary['throughput_requests_per_sec']} req/sec")
    print(f"P50 Latency       : {summary['latency_p50_ms']} ms")
    print(f"P95 Latency       : {summary['latency_p95_ms']} ms")
    print(f"P99 Latency       : {summary['latency_p99_ms']} ms")
    print(f"SLA Compliance    : {summary['sla_compliance_rate']}% (Breaches: {summary['sla_breach_count']})")
    print("=" * 65)
