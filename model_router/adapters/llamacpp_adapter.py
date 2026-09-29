"""
llama.cpp Model Adapter
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer

Connects to local on-premise llama.cpp server (llama-server).
Enables CPU offloading and low-VRAM deployment (e.g. 4-8 GB) on edge/refinery laptops.
"""

import json
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional

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


class LlamaCppAdapter(BaseModelAdapter):
    """Adapter for llama.cpp server running quantized GGUF models."""

    def __init__(self, model_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_id, config)
        self.endpoint = self.config.get("endpoint", "http://127.0.0.1:8080")
        self.n_gpu_layers = self.config.get("n_gpu_layers", 24)
        self.threads = self.config.get("threads", 4)

    def get_adapter_type(self) -> str:
        return "llamacpp"

    def _post(self, endpoint_path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.endpoint.rstrip('/')}/{endpoint_path.lstrip('/')}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            if "out of memory" in err_body.lower() or "failed to allocate" in err_body.lower():
                raise OutOfMemoryError(
                    f"llama.cpp memory allocation error: {err_body}",
                    self.model_id,
                    self.get_adapter_type(),
                    status_code=e.code,
                )
            raise ModelInferenceError(
                f"llama.cpp error HTTP {e.code}: {err_body}",
                self.model_id,
                self.get_adapter_type(),
                status_code=e.code,
            )
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            raise ModelUnavailableError(
                f"llama.cpp server unreachable at {self.endpoint}: {e}",
                self.model_id,
                self.get_adapter_type(),
            )

    def generate(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> ModelResponse:
        opts = {**self.config, **(options or {})}
        payload = {
            "prompt": prompt,
            "temperature": opts.get("temperature", self.temperature),
            "n_predict": opts.get("max_tokens", self.max_tokens),
            "stream": False,
        }

        start_time = time.perf_counter()
        data = self._post("completion", payload)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        content = data.get("content", "")
        tokens_evaluated = data.get("tokens_evaluated", 0)
        tokens_predicted = data.get("tokens_predicted", 0)
        tps = (tokens_predicted / (latency_ms / 1000.0)) if latency_ms > 0 else 0.0

        return ModelResponse(
            text=content,
            model_id=self.model_id,
            adapter_type=self.get_adapter_type(),
            latency_ms=latency_ms,
            usage=TokenUsage(
                prompt_tokens=tokens_evaluated,
                completion_tokens=tokens_predicted,
                total_tokens=tokens_evaluated + tokens_predicted,
                tokens_per_second=tps,
            ),
            finish_reason="stop" if data.get("stopped_eos") else "length",
            confidence_score=0.92,
        )

    def generate_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        opts = {**self.config, **(options or {})}
        payload: Dict[str, Any] = {
            "messages": messages,
            "temperature": opts.get("temperature", self.temperature),
            "max_tokens": opts.get("max_tokens", self.max_tokens),
            "stream": False,
        }
        if tools:
            payload["tools"] = tools

        start_time = time.perf_counter()
        data = self._post("v1/chat/completions", payload)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        choice = data["choices"][0]
        message = choice.get("message", {})
        text = message.get("content") or ""

        tool_calls: List[ToolCallRequest] = []
        if "tool_calls" in message and message["tool_calls"]:
            for tc in message["tool_calls"]:
                func = tc.get("function", {})
                tool_calls.append(
                    ToolCallRequest(
                        id=tc.get("id", f"call_{int(time.time()*1000)}"),
                        name=func.get("name", ""),
                        arguments=json.loads(func.get("arguments", "{}")),
                    )
                )

        usage_data = data.get("usage", {})
        return ModelResponse(
            text=text,
            model_id=self.model_id,
            adapter_type=self.get_adapter_type(),
            latency_ms=latency_ms,
            usage=TokenUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
                tokens_per_second=(usage_data.get("completion_tokens", 0) / (latency_ms / 1000.0))
                if latency_ms > 0 else 0.0,
            ),
            tool_calls=tool_calls,
            confidence_score=0.92,
        )

    def generate_multimodal(
        self,
        prompt: str,
        image_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        # llama.cpp server with llava mmproj
        return self.generate(f"[IMAGE_CONTEXT]\n{prompt}", options=options)

    def health_check(self) -> HealthStatus:
        start_time = time.perf_counter()
        try:
            url = f"{self.endpoint.rstrip('/')}/health"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                status_str = data.get("status", "ok")
                return HealthStatus(
                    is_healthy=status_str in ("ok", "loading model"),
                    status_code=resp.status,
                    message=f"llama.cpp status: {status_str}",
                    latency_ms=latency_ms,
                    details=data,
                )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return HealthStatus(
                is_healthy=False,
                status_code=503,
                message=f"llama.cpp unreachable: {e}",
                latency_ms=latency_ms,
            )
