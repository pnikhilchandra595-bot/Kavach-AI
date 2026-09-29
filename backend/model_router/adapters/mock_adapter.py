"""
Deterministic Air-Gapped Simulation Adapter
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer

Provides realistic, deterministic MRPL refinery domain inference offline without GPU weights.
Includes programmable fault injection (OOM, Process Crash, High Latency) for judge testing
and fallback policy verification.
"""

import time
import json
from typing import Any, Dict, List, Optional

from .base import (
    BaseModelAdapter,
    ModelResponse,
    ToolCallRequest,
    TokenUsage,
    HealthStatus,
    OutOfMemoryError,
    ModelUnavailableError,
)


class MockAdapter(BaseModelAdapter):
    """Deterministic air-gapped simulation adapter with MRPL domain knowledge and fault injection."""

    def __init__(self, model_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_id, config)
        self.simulate_oom = self.config.get("simulate_oom", False)
        self.simulate_crash = self.config.get("simulate_crash", False)
        self.simulated_latency_sec = self.config.get("simulated_latency_sec", 0.05)
        self.simulated_tps = self.config.get("simulated_tps", 42.5)

    def get_adapter_type(self) -> str:
        return "mock"

    def set_fault_injection(self, oom: bool = False, crash: bool = False, latency_sec: float = 0.05):
        """Programmatically inject faults for fallback testing."""
        self.simulate_oom = oom
        self.simulate_crash = crash
        self.simulated_latency_sec = latency_sec

    def _check_faults(self):
        if self.simulate_oom:
            raise OutOfMemoryError(
                f"CUDA Out of Memory: Tried to allocate 4.20 GiB (GPU 0; 4.00 GiB total capacity; 3.85 GiB already allocated)",
                self.model_id,
                self.get_adapter_type(),
                status_code=503,
            )
        if self.simulate_crash:
            raise ModelUnavailableError(
                f"Connection refused: Inference server process PID 4192 terminated unexpectedly (SIGKILL)",
                self.model_id,
                self.get_adapter_type(),
            )

    def generate(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> ModelResponse:
        self._check_faults()
        start = time.perf_counter()
        if self.simulated_latency_sec > 0:
            time.sleep(self.simulated_latency_sec)
        latency_ms = (time.perf_counter() - start) * 1000.0

        p_lower = prompt.lower()
        if "p&id" in p_lower or "diagram" in p_lower or "drawing" in p_lower:
            text = (
                "### P&ID Technical Analysis [MRPL Phase-III CDU/VDU]\n"
                "- **Equipment Tag**: 10-P-101A/B (Crude Charge Pumps)\n"
                "- **Suction Line**: 14\"-C-101-A1A with isolation gate valve MOV-1001\n"
                "- **Discharge Rating**: Class 300 RF, Design Temp: 180°C, Design Pressure: 24.5 kg/cm²g\n"
                "- **Instrumentation**: PT-1004 (Transmitter), TI-1002 (Thermowell), PSV-1001 set at 28 kg/cm²g"
            )
        elif "code" in p_lower or "python" in p_lower or "sql" in p_lower:
            text = (
                "```python\n"
                "# MRPL SCADA Vibration & Temperature Anomaly Detector\n"
                "import numpy as np\n\n"
                "def check_pump_bearing_health(vibration_rms: float, temp_c: float) -> dict:\n"
                "    status = 'NORMAL'\n"
                "    if vibration_rms > 4.5 or temp_c > 85.0:\n"
                "        status = 'CRITICAL_ALERT'\n"
                "    elif vibration_rms > 2.8 or temp_c > 75.0:\n"
                "        status = 'WARNING'\n"
                "    return {'status': status, 'vibration_rms': vibration_rms, 'temp_c': temp_c}\n"
                "```"
            )
        elif "sop" in p_lower or "procedure" in p_lower or "sulfur" in p_lower:
            text = (
                "### Standard Operating Procedure: MRPL SRU-II Tail Gas Unit Startup\n"
                "1. Confirm nitrogen purging until O2 < 0.5% vol.\n"
                "2. Establish lean amine circulation at 45 m³/hr to Absorber C-201.\n"
                "3. Ignite Reaction Furnace F-101 pilot burners under supervisor authorization.\n"
                "4. Maintain H2S/SO2 stoichiometric ratio strictly at 2:1 via Analyzer AI-101."
            )
        else:
            text = (
                f"Sovereign on-premise response from [{self.model_id}]. "
                "Air-gapped verification complete. Prompt processed securely on local compute."
            )

        prompt_tokens = len(prompt.split()) + 10
        comp_tokens = len(text.split()) + 15
        total_tokens = prompt_tokens + comp_tokens

        return ModelResponse(
            text=text,
            model_id=self.model_id,
            adapter_type=self.get_adapter_type(),
            latency_ms=latency_ms,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                total_tokens=total_tokens,
                tokens_per_second=self.simulated_tps,
            ),
            finish_reason="stop",
            confidence_score=0.98,
        )

    def generate_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        self._check_faults()
        last_msg = messages[-1]["content"] if messages else ""
        if isinstance(last_msg, list):
            # Multimodal content block
            last_msg = " ".join(item.get("text", "") for item in last_msg if isinstance(item, dict))

        tool_calls: List[ToolCallRequest] = []
        # If caller provided tools and asking about files or inspection, simulate structured tool call
        if tools and ("inspect" in str(last_msg).lower() or "generate" in str(last_msg).lower() or "read" in str(last_msg).lower()):
            tool_name = tools[0].get("function", {}).get("name", "inspect_refinery_doc")
            tool_calls.append(
                ToolCallRequest(
                    id=f"call_mock_{int(time.time())}",
                    name=tool_name,
                    arguments={"doc_type": "inspection_report", "tag": "MRPL-CDU-01", "action": "extract_parameters"},
                )
            )

        resp = self.generate(str(last_msg), options=options)
        resp.tool_calls = tool_calls
        return resp

    def generate_multimodal(
        self,
        prompt: str,
        image_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        self._check_faults()
        img_size_info = f"{len(image_bytes)} bytes" if image_bytes else (image_path or "provided image")
        resp = self.generate(f"P&ID Visual Processing: {prompt}", options=options)
        resp.metadata["multimodal_source"] = img_size_info
        resp.confidence_score = 0.96
        return resp

    def health_check(self) -> HealthStatus:
        if self.simulate_crash or self.simulate_oom:
            return HealthStatus(
                is_healthy=False,
                status_code=503,
                message="Fault injection active: service unhealthy",
                latency_ms=1.2,
            )
        return HealthStatus(
            is_healthy=True,
            status_code=200,
            message="Mock air-gapped inference engine active",
            latency_ms=0.8,
            vram_used_mb=128.0,
            vram_total_mb=4096.0,
        )
