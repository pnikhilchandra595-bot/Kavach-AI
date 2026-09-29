"""
Cross-Model Consistency Checker for Critical Refinery Deliverables.
Executes dual-model inference and verifies agreement on safety-critical recommendations.
"""

from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
import re
from model_router.registry import ModelRegistry
from model_router.adapters.base import ModelAdapter, ModelResponse


class ModelFinding(BaseModel):
    model_id: str
    recommended_action: str
    vibration_observed: Optional[float] = None
    vibration_threshold: Optional[float] = None
    urgency: str = "NORMAL"
    raw_text: str = ""


class ConsistencyReport(BaseModel):
    is_consistent: bool
    agreement_score: float
    primary_finding: ModelFinding
    secondary_finding: ModelFinding
    discrepancy_details: Optional[str] = None
    flagged_for_supervisor_review: bool = False
    resolution_advisory: str


class CrossModelConsistencyChecker:
    """
    Validates high-consequence outputs by querying two independent local models
    and comparing their domain recommendations and extracted telemetry.
    """

    def __init__(self, registry: Optional[ModelRegistry] = None, threshold: float = 0.85):
        self.registry = registry or ModelRegistry()
        self.threshold = threshold

    def _extract_telemetry_and_action(self, model_id: str, text: str) -> ModelFinding:
        """Parses recommended action and numerical values from model text."""
        text_lower = text.lower()

        # Extract action
        if any(w in text_lower for w in ["shutdown", "isolate", "emergency", "overhaul", "replace bearing"]):
            action = "SHUTDOWN_AND_MAINTAIN"
        elif any(w in text_lower for w in ["continue", "monitor", "normal", "acceptable"]):
            action = "CONTINUE_MONITORING"
        else:
            action = "FURTHER_INSPECTION"

        # Extract urgency
        if any(w in text_lower for w in ["critical", "emergency", "immediate", "urgent"]):
            urgency = "CRITICAL"
        elif "high" in text_lower:
            urgency = "HIGH"
        else:
            urgency = "NORMAL"

        # Extract numbers (vibration values)
        vib_matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:mm/s|rms)", text_lower)
        vibration_observed = float(vib_matches[0]) if len(vib_matches) > 0 else None
        vibration_threshold = float(vib_matches[1]) if len(vib_matches) > 1 else None

        return ModelFinding(
            model_id=model_id,
            recommended_action=action,
            vibration_observed=vibration_observed,
            vibration_threshold=vibration_threshold,
            urgency=urgency,
            raw_text=text[:300]
        )

    def verify_consistency(
        self,
        diagnostic_context: str,
        primary_model_id: str = "qwen2.5-72b-instruct",
        secondary_model_id: str = "qwen2.5-32b-instruct"
    ) -> ConsistencyReport:
        """
        Executes dual inference across primary and secondary models,
        comparing domain decisions and extracting consensus metrics.
        """
        primary_adapter = self.registry.get_adapter(primary_model_id)
        secondary_adapter = self.registry.get_adapter(secondary_model_id)

        prompt = (
            f"DIAGNOSTIC CONTEXT:\n{diagnostic_context}\n\n"
            f"INSTRUCTION: Provide the recommended maintenance action, "
            f"vibration readings observed, and urgency level."
        )

        resp_a = primary_adapter.generate(prompt)
        resp_b = secondary_adapter.generate(prompt)

        finding_a = self._extract_telemetry_and_action(primary_model_id, resp_a.content)
        finding_b = self._extract_telemetry_and_action(secondary_model_id, resp_b.content)

        # Calculate consensus agreement score
        score = 1.0
        discrepancies = []

        # 1. Action agreement (weight: 0.5)
        if finding_a.recommended_action != finding_b.recommended_action:
            score -= 0.50
            discrepancies.append(
                f"Action mismatch: {finding_a.model_id} recommended '{finding_a.recommended_action}' "
                f"vs {finding_b.model_id} recommended '{finding_b.recommended_action}'."
            )

        # 2. Urgency agreement (weight: 0.25)
        if finding_a.urgency != finding_b.urgency:
            score -= 0.25
            discrepancies.append(
                f"Urgency mismatch: {finding_a.model_id} flagged '{finding_a.urgency}' "
                f"vs {finding_b.model_id} flagged '{finding_b.urgency}'."
            )

        # 3. Numerical telemetry agreement (weight: 0.25)
        if finding_a.vibration_observed and finding_b.vibration_observed:
            if abs(finding_a.vibration_observed - finding_b.vibration_observed) > 0.1:
                score -= 0.25
                discrepancies.append(
                    f"Numerical variance in observed vibration: {finding_a.vibration_observed} mm/s "
                    f"vs {finding_b.vibration_observed} mm/s."
                )

        score = max(0.0, score)
        is_consistent = score >= self.threshold

        if is_consistent:
            resolution_advisory = (
                f"Dual-model consensus verified ({score * 100:.0f}% agreement). "
                f"Both models concur on {finding_a.recommended_action}."
            )
            flagged = False
        else:
            resolution_advisory = (
                f"CONFLICT DETECTED ({score * 100:.0f}% agreement < {self.threshold * 100:.0f}% threshold). "
                "Automatic execution blocked; mandatory human review required."
            )
            flagged = True

        return ConsistencyReport(
            is_consistent=is_consistent,
            agreement_score=score,
            primary_finding=finding_a,
            secondary_finding=finding_b,
            discrepancy_details="; ".join(discrepancies) if discrepancies else None,
            flagged_for_supervisor_review=flagged,
            resolution_advisory=resolution_advisory
        )
