"""
vLLM Model Adapter
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer

Connects to local on-premise vLLM high-throughput inference engine.
Communicates strictly via localhost/local IPC with zero outbound traffic.
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


class VLLMAdapter(BaseModelAdapter):
    """Adapter for local vLLM instances serving OpenAI-compatible REST APIs."""

    def __init__(self, model_id: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(model_id, config)
        self.endpoint = self.config.get("endpoint", "http://127.0.0.1:8000/v1")
        self.api_key = self.config.get("api_key", "sovereign-local-token")
        self.served_model_name = self.config.get("served_model_name", model_id)

    def get_adapter_type(self) -> str:
        return "vllm"

    def _make_request(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request to local vLLM server with error translation."""
        url = f"{self.endpoint.rstrip('/')}/{path.lstrip('/')}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            if "out of memory" in err_body.lower() or "cuda oom" in err_body.lower() or e.code == 503:
                raise OutOfMemoryError(
                    f"vLLM GPU Out-of-Memory detected: {err_body}",
                    self.model_id,
                    self.get_adapter_type(),
                    status_code=e.code,
                )
            raise ModelInferenceError(
                f"vLLM API returned HTTP {e.code}: {err_body}",
                self.model_id,
                self.get_adapter_type(),
                status_code=e.code,
            )
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            raise ModelUnavailableError(
                f"Failed to connect to local vLLM endpoint at {self.endpoint}: {e}",
                self.model_id,
                self.get_adapter_type(),
            )

    def generate(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> ModelResponse:
        opts = {**self.config, **(options or {})}
        payload = {
            "model": self.served_model_name,
            "prompt": prompt,
            "temperature": opts.get("temperature", self.temperature),
            "max_tokens": opts.get("max_tokens", self.max_tokens),
        }

        start_time = time.perf_counter()
        data = self._make_request("completions", payload)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        choice = data["choices"][0]
        text = choice.get("text", "")
        usage_data = data.get("usage", {})
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)
        tps = (completion_tokens / (latency_ms / 1000.0)) if latency_ms > 0 else 0.0

        return ModelResponse(
            text=text,
            model_id=self.model_id,
            adapter_type=self.get_adapter_type(),
            latency_ms=latency_ms,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                tokens_per_second=tps,
            ),
            finish_reason=choice.get("finish_reason", "stop"),
            confidence_score=0.95,
        )

    def generate_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> ModelResponse:
        opts = {**self.config, **(options or {})}
        payload: Dict[str, Any] = {
            "model": self.served_model_name,
            "messages": messages,
            "temperature": opts.get("temperature", self.temperature),
            "max_tokens": opts.get("max_tokens", self.max_tokens),
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = opts.get("tool_choice", "auto")

        start_time = time.perf_counter()
        data = self._make_request("chat/completions", payload)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        choice = data["choices"][0]
        message = choice.get("message", {})
        text = message.get("content") or ""

        tool_calls: List[ToolCallRequest] = []
        if "tool_calls" in message and message["tool_calls"]:
            for tc in message["tool_calls"]:
                func = tc.get("function", {})
                args_raw = func.get("arguments", "{}")
                args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
                tool_calls.append(
                    ToolCallRequest(
                        id=tc.get("id", f"call_{int(time.time()*1000)}"),
                        name=func.get("name", ""),
                        arguments=args,
                    )
                )

        usage_data = data.get("usage", {})
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        completion_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", prompt_tokens + completion_tokens)
        tps = (completion_tokens / (latency_ms / 1000.0)) if latency_ms > 0 else 0.0

        return ModelResponse(
            text=text,
            model_id=self.model_id,
            adapter_type=self.get_adapter_type(),
            latency_ms=latency_ms,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                tokens_per_second=tps,
            ),
            tool_calls=tool_calls,
            finish_reason=choice.get("finish_reason", "stop"),
            confidence_score=0.96,
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
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        ]
        return self.generate_chat(messages, options=options)

    def health_check(self) -> HealthStatus:
        start_time = time.perf_counter()
        try:
            url = f"{self.endpoint.rstrip('/')}/models"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.api_key}"})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                latency_ms = (time.perf_counter() - start_time) * 1000.0
                return HealthStatus(
                    is_healthy=resp.status == 200,
                    status_code=resp.status,
                    message="vLLM server online and serving",
                    latency_ms=latency_ms,
                    details={"models": [m.get("id") for m in data.get("data", [])]},
                )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            return HealthStatus(
                is_healthy=False,
                status_code=503,
                message=f"vLLM server unreachable: {e}",
                latency_ms=latency_ms,
            )
