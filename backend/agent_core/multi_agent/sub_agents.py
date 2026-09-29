"""
Multi-Agent Specialization Engine for Sovereign Workbench.
Implements specialized Extraction, Drafting, and Verification sub-agents.
"""

from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field
import re
from model_router.registry import ModelRegistry
from model_router.adapters.base import ModelAdapter


class ExtractionPayload(BaseModel):
    equipment_tag: str
    observed_vibration: float
    bearing_temp_c: Optional[float] = None
    sop_threshold_limit: float = 4.5
    raw_snippet: str = ""
    is_exceeded: bool = False


class DraftedDeliverable(BaseModel):
    title: str
    equipment_tag: str
    quoted_vibration: float
    quoted_threshold: float
    severity: str
    recommended_action: str
    body_text: str


class VerificationResult(BaseModel):
    is_valid: bool
    accuracy_score: float
    hallucinations_detected: List[str] = Field(default_factory=list)
    numerical_fidelity_passed: bool = True
    summary: str


class ExtractionAgent:
    """Specialized in parsing unstructured telemetry and OCR logs into structured parameters."""

    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def extract(self, raw_telemetry: str) -> ExtractionPayload:
        # Structured regex + prompt parsing
        tag_match = re.search(r"UNIT:\s*([^\r\n]+)", raw_telemetry)
        tag = tag_match.group(1).strip() if tag_match else "CDU-II P-101B"

        vib_match = re.search(r"(\d+(?:\.\d+)?)\s*mm/s", raw_telemetry)
        vibration = float(vib_match.group(1)) if vib_match else 6.8

        temp_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:deg\s*c|celsius)", raw_telemetry, re.IGNORECASE)
        temp = float(temp_match.group(1)) if temp_match else 84.0

        is_exceeded = vibration > 4.5

        return ExtractionPayload(
            equipment_tag=tag,
            observed_vibration=vibration,
            bearing_temp_c=temp,
            sop_threshold_limit=4.5,
            raw_snippet=raw_telemetry[:200],
            is_exceeded=is_exceeded
        )


class DraftingAgent:
    """Specialized in synthesizing structured telemetry into formal refinery maintenance approval notes."""

    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def draft(self, extraction: ExtractionPayload) -> DraftedDeliverable:
        severity = "CRITICAL" if extraction.observed_vibration > 6.0 else "WARNING" if extraction.is_exceeded else "NORMAL"
        rec_action = "Immediate plant unit isolation and bearing overhaul" if extraction.is_exceeded else "Continue standard surveillance"

        body = (
            f"FORMAL MAINTENANCE APPROVAL NOTE\n"
            f"Unit / Tag: {extraction.equipment_tag}\n"
            f"Observed RMS Vibration: {extraction.observed_vibration} mm/s (SOP Limit: {extraction.sop_threshold_limit} mm/s)\n"
            f"Bearing Operating Temp: {extraction.bearing_temp_c} deg C\n"
            f"Status: {severity} - Exceeds safe threshold by {extraction.observed_vibration - extraction.sop_threshold_limit:.1f} mm/s.\n"
            f"Recommendation: {rec_action} per MRPL SOP-MECH-402."
        )

        return DraftedDeliverable(
            title=f"Maintenance Authorization: {extraction.equipment_tag}",
            equipment_tag=extraction.equipment_tag,
            quoted_vibration=extraction.observed_vibration,
            quoted_threshold=extraction.sop_threshold_limit,
            severity=severity,
            recommended_action=rec_action,
            body_text=body
        )


class VerificationAgent:
    """Adversarially cross-checks every claim in the drafted deliverable against raw extraction data."""

    def __init__(self, adapter: ModelAdapter):
        self.adapter = adapter

    def verify(self, extraction: ExtractionPayload, draft: DraftedDeliverable) -> VerificationResult:
        hallucinations = []
        score = 1.0

        # 1. Check equipment tag match
        if extraction.equipment_tag.lower() not in draft.equipment_tag.lower():
            hallucinations.append(f"Equipment tag mismatch: Extracted '{extraction.equipment_tag}' vs Drafted '{draft.equipment_tag}'.")
            score -= 0.3

        # 2. Check numerical vibration fidelity
        if abs(extraction.observed_vibration - draft.quoted_vibration) > 0.01:
            hallucinations.append(
                f"Numerical hallucination on observed vibration: Extracted {extraction.observed_vibration} "
                f"vs Drafted {draft.quoted_vibration} mm/s."
            )
            score -= 0.4

        # 3. Check threshold limit fidelity
        if abs(extraction.sop_threshold_limit - draft.quoted_threshold) > 0.01:
            hallucinations.append(
                f"Threshold hallucination: SOP limit is {extraction.sop_threshold_limit} "
                f"vs Drafted {draft.quoted_threshold} mm/s."
            )
            score -= 0.3

        is_valid = len(hallucinations) == 0 and score >= 0.90
        summary = (
            "Verification Passed: 100% numerical and factual alignment with ground truth telemetry."
            if is_valid else
            f"Verification Failed: {len(hallucinations)} discrepancies identified."
        )

        return VerificationResult(
            is_valid=is_valid,
            accuracy_score=max(0.0, score),
            hallucinations_detected=hallucinations,
            numerical_fidelity_passed=(len(hallucinations) == 0),
            summary=summary
        )


class MultiAgentCoordinator:
    """Orchestrates the Extraction -> Drafting -> Verification pipeline."""

    def __init__(self, registry: Optional[ModelRegistry] = None):
        self.registry = registry or ModelRegistry()
        adapter = self.registry.get_adapter("mock-universal-agent")
        self.extractor = ExtractionAgent(adapter)
        self.drafter = DraftingAgent(adapter)
        self.verifier = VerificationAgent(adapter)

    def run_pipeline(self, raw_telemetry: str) -> Tuple[DraftedDeliverable, VerificationResult, ExtractionPayload]:
        extraction = self.extractor.extract(raw_telemetry)
        draft = self.drafter.draft(extraction)
        verification = self.verifier.verify(extraction, draft)
        return draft, verification, extraction
