"""
Speculative Model Cascading Engine
Part of SIH26117 — Sovereign On-Premise Agentic AI Workbench (MRPL Smart Automation)
P2 — Model Infrastructure Engineer (Stretch Feature)

Draft-model -> escalate-to-large-model latency and GPU compute optimization.
Executes rapid draft model (e.g. 7B Q4) for quick extraction or straightforward requests;
automatically escalates to flagship model (e.g. 32B/72B) if confidence drops below threshold
or if high domain complexity is detected.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .adapters.base import BaseModelAdapter, ModelResponse
from .registry_manager import ModelRegistryManager

logger = logging.getLogger("sovereign.cascade")


@dataclass
class CascadeResult:
    """Outcome of a cascaded inference execution."""
    response: ModelResponse
    escalated: bool
    draft_confidence: float
    decision_reason: str
    tokens_saved: int = 0
    estimated_latency_saved_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "response": self.response.to_dict(),
            "escalated": self.escalated,
            "draft_confidence": round(self.draft_confidence, 3),
            "decision_reason": self.decision_reason,
            "tokens_saved": self.tokens_saved,
            "estimated_latency_saved_ms": round(self.estimated_latency_saved_ms, 2),
        }


class ModelCascader:
    """Manages draft-to-flagship model cascading to maximize refinery edge throughput."""

    # Keywords signaling high risk or complex engineering calculations requiring escalation
    HIGH_COMPLEXITY_TRIGGERS = [
        "turnaround schedule",
        "emergency shutdown",
        "stoichiometric ratio",
        "hydrocracker high-pressure alarm",
        "p&id tag reconciliation",
        "safety integrity level",
        "sil-3",
        "asme section viii",
    ]

    def __init__(
        self,
        registry_manager: ModelRegistryManager,
        draft_model_id: str = "qwen2.5-7b-q4",
        flagship_model_id: str = "qwen2.5-32b-awq",
        confidence_threshold: float = 0.88,
        fallback_engine: Optional[Any] = None,
    ):
        self.registry = registry_manager
        self.draft_model_id = draft_model_id
        self.flagship_model_id = flagship_model_id
        self.confidence_threshold = confidence_threshold
        self.fallback_engine = fallback_engine

        self.total_requests = 0
        self.escalation_count = 0
        self.total_tokens_saved = 0

    def _assess_prompt_complexity(self, prompt: str) -> Tuple[bool, str]:
        """Check for industrial safety-critical patterns requiring immediate flagship attention."""
        p_lower = prompt.lower()
        for trigger in self.HIGH_COMPLEXITY_TRIGGERS:
            if trigger in p_lower:
                return True, f"Trigger keyword detected: '{trigger}' (Safety-Critical Policy)"
        return False, "Standard operational complexity"

    def _call_flagship(self, prompt: str, task_type: str, options: Optional[Dict[str, Any]] = None) -> ModelResponse:
        if self.fallback_engine:
            resp, _ = self.fallback_engine.execute_with_fallback(
                task_type=task_type,
                inference_callable=lambda ad: ad.generate(prompt, options=options),
                preferred_model=self.flagship_model_id,
            )
            return resp
        flagship_adapter = self.registry.get_adapter(self.flagship_model_id)
        return flagship_adapter.generate(prompt, options=options)

    def run_cascaded(
        self,
        prompt: str,
        task_type: str = "general",
        options: Optional[Dict[str, Any]] = None,
    ) -> CascadeResult:
        """Run through draft model first; escalate if confidence is insufficient."""
        self.total_requests += 1

        # Check prompt complexity upfront
        must_escalate, trigger_reason = self._assess_prompt_complexity(prompt)
        if must_escalate:
            self.escalation_count += 1
            resp = self._call_flagship(prompt, task_type=task_type, options=options)
            resp.metadata["cascade_mode"] = "direct_flagship_escalation"
            return CascadeResult(
                response=resp,
                escalated=True,
                draft_confidence=0.0,
                decision_reason=trigger_reason,
                tokens_saved=0,
                estimated_latency_saved_ms=0.0,
            )

        # Run draft model
        draft_adapter = self.registry.get_adapter(self.draft_model_id)
        draft_resp = draft_adapter.generate(prompt, options=options)

        # Evaluate draft output quality & confidence
        draft_conf = draft_resp.confidence_score
        text_lower = draft_resp.text.lower()
        if "uncertain" in text_lower or "unknown" in text_lower or len(draft_resp.text.strip()) < 15:
            draft_conf *= 0.70

        if draft_conf >= self.confidence_threshold:
            # Draft model succeeded! High efficiency gain
            estimated_tokens_saved = max(0, draft_resp.usage.total_tokens * 2)
            self.total_tokens_saved += estimated_tokens_saved
            draft_resp.metadata["cascade_mode"] = "draft_served"
            return CascadeResult(
                response=draft_resp,
                escalated=False,
                draft_confidence=draft_conf,
                decision_reason="Draft model confidence met threshold",
                tokens_saved=estimated_tokens_saved,
                estimated_latency_saved_ms=250.0,
            )

        # Low confidence -> Escalate to flagship model
        self.escalation_count += 1
        flagship_resp = self._call_flagship(prompt, task_type=task_type, options=options)
        flagship_resp.metadata["cascade_mode"] = "escalated_after_draft_evaluation"
        flagship_resp.metadata["draft_confidence"] = draft_conf

        return CascadeResult(
            response=flagship_resp,
            escalated=True,
            draft_confidence=draft_conf,
            decision_reason=f"Draft confidence {draft_conf:.2f} below threshold {self.confidence_threshold:.2f}",
            tokens_saved=0,
            estimated_latency_saved_ms=0.0,
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Return cumulative cascading performance metrics."""
        esc_rate = (self.escalation_count / self.total_requests) if self.total_requests > 0 else 0.0
        return {
            "total_requests": self.total_requests,
            "escalation_count": self.escalation_count,
            "escalation_rate": round(esc_rate, 3),
            "fast_path_served": self.total_requests - self.escalation_count,
            "total_tokens_saved": self.total_tokens_saved,
        }
