"""
Ollama Model Adapter
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer

Connects to local on-premise Ollama instance.
Supports quantized GGUF models (4-bit, 8-bit) optimized for GPU/CPU constrained refinery nodes.
"""

import json
import time
import base64
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


class OllamaAdapter(BaseModelAdapter):
    """Adapter for local Ollama serving GGUF models."""

    def __init__(self, model_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_id, config)
        self.endpoint = self.config.get("endpoint", "http://127.0.0.1:11434")
        self.ollama_model_tag = self.config.get("ollama_model_tag", model_id)

    def get_adapter_type(self) -> str:
        return "ollama"

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
            if "out of memory" in err_body.lower() or "cuda" in err_body.lower() or e.code == 503:
                raise OutOfMemoryError(
                    f"Ollama Out-of-Memory: {err_body}",
                    self.model_id,
                    self.get_adapter_type(),
                    status_code=e.code,
                )
            raise ModelInferenceError(
                f"Ollama API HTTP {e.code}: {err_body}",
                self.model_id,
                self.get_adapter_type(),
                status_code=e.code,
            )
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            raise ModelUnavailableError(
                f"Ollama server unreachable at {self.endpoint}: {e}",
                self.model_id,
                self.get_adapter_type(),
            )

    def generate(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> ModelResponse:
        opts = {**self.config, **(options or {})}
        payload = {
            "model": self.ollama_model_tag,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": opts.get("temperature", self.temperature),
                "num_predict": opts.get("max_tokens", self.max_tokens),
            },
        }

        start_time = time.perf_counter()
        data = self._post("api/generate", payload)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        prompt_eval_count = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)
        eval_duration_ns = data.get("eval_duration", 0)
        tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0.0

        return ModelResponse(
            text=data.get("response", ""),
            model_id=self.model_id,
            adapter_type=self.get_adapter_type(),
            latency_ms=latency_ms,
            usage=TokenUsage(
                prompt_tokens=prompt_eval_count,
                completion_tokens=eval_count,
                total_tokens=prompt_eval_count + eval_count,
                tokens_per_second=tps,
            ),
            finish_reason="stop" if data.get("done") else "length",
            confidence_score=0.94,
        )

    def generate_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        opts = {**self.config, **(options or {})}
        payload: Dict[str, Any] = {
            "model": self.ollama_model_tag,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": opts.get("temperature", self.temperature),
                "num_predict": opts.get("max_tokens", self.max_tokens),
            },
        }
        if tools:
            payload["tools"] = tools

        start_time = time.perf_counter()
        data = self._post("api/chat", payload)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        msg = data.get("message", {})
        text = msg.get("content", "")

        tool_calls: List[ToolCallRequest] = []
        if "tool_calls" in msg and msg["tool_calls"]:
            for tc in msg["tool_calls"]:
                func = tc.get("function", {})
                tool_calls.append(
                    ToolCallRequest(
                        id=f"ollama_{int(time.time()*1000)}",
                        name=func.get("name", ""),
                        arguments=func.get("arguments", {}),
                    )
                )

        prompt_eval_count = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)
        eval_duration_ns = data.get("eval_duration", 0)
        tps = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0.0

        return ModelResponse(
            text=text,
            model_id=self.model_id,
            adapter_type=self.get_adapter_type(),
            latency_ms=latency_ms,
            usage=TokenUsage(
                prompt_tokens=prompt_eval_count,
                completion_tokens=eval_count,
                total_tokens=prompt_eval_count + eval_count,
                tokens_per_second=tps,
            ),
            tool_calls=tool_calls,
            finish_reason="stop" if data.get("done") else "length",
            confidence_score=0.94,
        )

    def generate_multimodal(
        self,
        prompt: str,
        image_bytes: Optional[bytes] = None,
        image_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        b64_image = ""
        if image_bytes:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
        elif image_path:
            with open(image_path, "rb") as f:
                b64_image = base64.b64encode(f.read()).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": prompt,
                "images": [b64_image] if b64_image else [],
            }
        ]
        return self.generate_chat(messages, options=options)

    def health_check(self) -> HealthStatus:
        start_time = time.perf_counter()
        try:
            url = f"{self.endpoint.rstrip('/')}/api/tags"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                models = [m.get("name") for m in data.get("models", [])]
                is_available = any(self.ollama_model_tag in m for m in models)
                return HealthStatus(
                    is_healthy=resp.status == 200 and (is_available or len(models) > 0),
                    status_code=resp.status,
                    message=f"Ollama healthy, models present: {models}",
                    latency_ms=latency_ms,
                    details={"installed_models": models},
                )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return HealthStatus(
                is_healthy=False,
                status_code=503,
                message=f"Ollama service probe failed: {e}",
                latency_ms=latency_ms,
            )
