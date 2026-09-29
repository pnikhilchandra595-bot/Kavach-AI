"""
Base Model Adapter Interface
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer

Defines the contract for all local inference runtimes:
- vLLM (OpenAI-compatible server)
- Ollama (Local quantized REST API)
- llama.cpp (GGUF server/subprocess)
- Mock / Air-Gapped Simulation Adapter
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
import time


@dataclass
class ToolCallRequest:
    """Represents a structured tool invocation requested by the model."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class TokenUsage:
    """Token consumption and memory metrics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    tokens_per_second: float = 0.0


@dataclass
class ModelResponse:
    """Normalized response envelope returned by any adapter."""
    text: str
    model_id: str
    adapter_type: str
    latency_ms: float
    usage: TokenUsage = field(default_factory=TokenUsage)
    tool_calls: List[ToolCallRequest] = field(default_factory=list)
    confidence_score: float = 1.0
    finish_reason: str = "stop"
    is_fallback: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "model_id": self.model_id,
            "adapter_type": self.adapter_type,
            "latency_ms": round(self.latency_ms, 2),
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
                "tokens_per_second": round(self.usage.tokens_per_second, 2),
            },
            "tool_calls": [
                {"id": tc.id, "name": tc.name, "arguments": tc.arguments}
                for tc in self.tool_calls
            ],
            "confidence_score": round(self.confidence_score, 3),
            "finish_reason": self.finish_reason,
            "is_fallback": self.is_fallback,
            "metadata": self.metadata,
        }


@dataclass
class HealthStatus:
    """Health check diagnostics for local inference backends."""
    is_healthy: bool
    status_code: int
    message: str
    latency_ms: float
    vram_used_mb: Optional[float] = None
    vram_total_mb: Optional[float] = None
    active_requests: int = 0
    details: Dict[str, Any] = field(default_factory=dict)


class ModelInferenceError(Exception):
    """Base exception for all model inference errors."""
    def __init__(self, message: str, model_id: str, adapter_type: str, status_code: int = 500):
        super().__init__(f"[{adapter_type}:{model_id}] {message}")
        self.message = message
        self.model_id = model_id
        self.adapter_type = adapter_type
        self.status_code = status_code


class OutOfMemoryError(ModelInferenceError):
    """Raised when GPU/RAM allocation fails (OOM). Triggers immediate fallback."""
    pass


class ModelUnavailableError(ModelInferenceError):
    """Raised when the local serving backend is unreachable or crashed."""
    pass


class BaseModelAdapter(ABC):
    """Abstract interface that all local serving adapters must implement."""

    def __init__(self, model_id: str, config: Optional[Dict[str, Any]] = None):
        self.model_id = model_id
        self.config = config or {}
        self.endpoint = self.config.get("endpoint", "")
        self.temperature = self.config.get("temperature", 0.1)
        self.max_tokens = self.config.get("max_tokens", 2048)
        self.timeout = self.config.get("timeout", 90.0)

    @abstractmethod
    def generate(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> ModelResponse:
        """Run text completion for a raw prompt."""
        pass

    @abstractmethod
    def generate_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        """Run chat completion with optional schema-constrained tool calls."""
        pass

    @abstractmethod
    def generate_multimodal(
        self,
        prompt: str,
        image_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        """Run multimodal inference (e.g., P&ID diagram, scanned log sheet, inspection photo)."""
        pass

    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Probe local backend liveness and resource consumption."""
        pass

    def get_model_id(self) -> str:
        return self.model_id

    @abstractmethod
    def get_adapter_type(self) -> str:
        return "base"
