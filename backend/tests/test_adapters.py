"""
Unit and Integration Tests for Model Adapters
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer
"""

import unittest
from model_router.adapters import (
    create_adapter,
    MockAdapter,
    VLLMAdapter,
    OllamaAdapter,
    LlamaCppAdapter,
    ModelResponse,
    ToolCallRequest,
)


class TestModelAdapters(unittest.TestCase):

    def test_adapter_factory(self):
        """Verify adapter factory instantiates correct adapter class per config."""
        mock_ad = create_adapter("m1", {"adapter": "mock"})
        self.assertIsInstance(mock_ad, MockAdapter)

        vllm_ad = create_adapter("m2", {"adapter": "vllm", "endpoint": "http://127.0.0.1:8000/v1"})
        self.assertIsInstance(vllm_ad, VLLMAdapter)

        ollama_ad = create_adapter("m3", {"adapter": "ollama", "endpoint": "http://127.0.0.1:11434"})
        self.assertIsInstance(ollama_ad, OllamaAdapter)

        llama_ad = create_adapter("m4", {"adapter": "llamacpp", "endpoint": "http://127.0.0.1:8080"})
        self.assertIsInstance(llama_ad, LlamaCppAdapter)

    def test_mock_adapter_refinery_prompts(self):
        """Verify deterministic domain responses for P&ID, coding, and SOP queries."""
        adapter = MockAdapter("qwen2.5-14b-q4", {"simulated_latency_sec": 0.001})

        # Test P&ID prompt
        resp_pid = adapter.generate("Inspect the suction line on P&ID drawing for 10-P-101A")
        self.assertIn("10-P-101A/B", resp_pid.text)
        self.assertIn("Crude Charge Pumps", resp_pid.text)
        self.assertGreater(resp_pid.usage.total_tokens, 0)
        self.assertGreater(resp_pid.usage.tokens_per_second, 0)

        # Test Coding prompt
        resp_code = adapter.generate("Write Python code to analyze pump vibration RMS")
        self.assertIn("def check_pump_bearing_health", resp_code.text)

        # Test SOP prompt
        resp_sop = adapter.generate("What is the standard operating procedure for Sulfur Recovery Unit startup?")
        self.assertIn("SRU-II Tail Gas Unit Startup", resp_sop.text)

    def test_mock_adapter_chat_and_tool_calling(self):
        """Verify structured tool call generation during chat completions."""
        adapter = MockAdapter("qwen2.5-coder-14b", {"simulated_latency_sec": 0.001})
        messages = [{"role": "user", "content": "Please inspect and extract parameters from the equipment report"}]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "inspect_refinery_doc",
                    "description": "Extract parameters from inspection PDF",
                    "parameters": {"type": "object", "properties": {"tag": {"type": "string"}}},
                },
            }
        ]
        resp = adapter.generate_chat(messages, tools=tools)
        self.assertEqual(len(resp.tool_calls), 1)
        self.assertEqual(resp.tool_calls[0].name, "inspect_refinery_doc")
        self.assertIn("tag", resp.tool_calls[0].arguments)

    def test_mock_adapter_multimodal(self):
        """Verify multimodal processing of P&ID image bytes."""
        adapter = MockAdapter("qwen2.5-vl-7b-instruct", {"simulated_latency_sec": 0.001})
        fake_image_bytes = b"GIF89a_FAKE_PID_IMAGE_BYTES"
        resp = adapter.generate_multimodal(
            prompt="Extract valve identifiers",
            image_bytes=fake_image_bytes,
        )
        self.assertIn("P&ID", resp.text)
        self.assertIn("multimodal_source", resp.metadata)
        self.assertGreaterEqual(resp.confidence_score, 0.90)

    def test_mock_adapter_health_check(self):
        """Verify health check diagnostics."""
        adapter = MockAdapter("qwen2.5-7b-q4")
        health = adapter.health_check()
        self.assertTrue(health.is_healthy)
        self.assertEqual(health.status_code, 200)
        self.assertGreater(health.vram_total_mb, 0)


if __name__ == "__main__":
    unittest.main()
