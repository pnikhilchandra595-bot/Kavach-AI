"""
Inference Adapters Package
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer
"""

from typing import Any, Dict
from .base import (
    BaseModelAdapter,
    ModelResponse,
    ToolCallRequest,
    TokenUsage,
    HealthStatus,
    ModelInferenceError,
    OutOfMemoryError,
    ModelUnavailableError,
)
from .vllm_adapter import VLLMAdapter
from .ollama_adapter import OllamaAdapter
from .llamacpp_adapter import LlamaCppAdapter
from .mock_adapter import MockAdapter


def create_adapter(model_id: str, config: Dict[str, Any]) -> BaseModelAdapter:
    """Factory function creating the appropriate adapter based on config."""
    adapter_type = config.get("adapter", "mock").lower()
    if adapter_type == "vllm":
        return VLLMAdapter(model_id, config)
    elif adapter_type == "ollama":
        return OllamaAdapter(model_id, config)
    elif adapter_type in ("llamacpp", "llama.cpp"):
        return LlamaCppAdapter(model_id, config)
    elif adapter_type == "mock":
        return MockAdapter(model_id, config)
    else:
        raise ValueError(f"Unknown adapter type '{adapter_type}' for model '{model_id}'")


__all__ = [
    "BaseModelAdapter",
    "ModelResponse",
    "ToolCallRequest",
    "TokenUsage",
    "HealthStatus",
    "ModelInferenceError",
    "OutOfMemoryError",
    "ModelUnavailableError",
    "VLLMAdapter",
    "OllamaAdapter",
    "LlamaCppAdapter",
    "MockAdapter",
    "create_adapter",
]
