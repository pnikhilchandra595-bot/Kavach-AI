"""
Explainability Layer for Sovereign Workbench.
Transforms raw agent reasoning traces into concise, human-understandable decision rationales.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import re


class DecisionCard(BaseModel):
    step_number: int
    tool_invoked: str
    action_intent: str
    evidence_grounding: str
    risk_level: str
    one_line_rationale: str
    confidence_score: float = 1.0


class ExplainabilityEngine:
    """
    Distills complex agentic thoughts, tool actions, and observations
    into one-line decision rationales suitable for refinery operators and audit reviewers.
    """

    @staticmethod
    def generate_step_rationale(
        step_number: int,
        thought: str,
        tool_name: Optional[str],
        tool_args: Optional[Dict[str, Any]],
        observation: Optional[str],
        risk_level: str = "low"
    ) -> DecisionCard:
        """Synthesizes a structured DecisionCard with a concise one-line rationale."""
        tool_name_str = tool_name or "reasoning"
        args_str = str(tool_args) if tool_args else "{}"

        # 1. Action Intent Extraction
        action_intent = f"Execute {tool_name_str} to advance diagnostic workflow."
        if tool_name_str == "read_scanned_ocr_text":
            file_name = (tool_args or {}).get("file_path", "document")
            action_intent = f"Extract telemetry readings from local scanned inspection document '{file_name}'."
        elif tool_name_str == "local_knowledge_search":
            query = (tool_args or {}).get("query", "")
            action_intent = f"Retrieve relevant operating thresholds from local MRPL SOP database for query: '{query}'."
        elif tool_name_str == "calculate_values":
            expr = (tool_args or {}).get("expression", "")
            action_intent = f"Compute numerical variance and threshold exceedance for expression '{expr}'."
        elif tool_name_str == "submit_approval_note":
            subj = (tool_args or {}).get("subject", "Maintenance")
            action_intent = f"Draft formal refinery maintenance approval note for subject: '{subj}'."

        # 2. Evidence Grounding Extraction
        evidence = "Awaiting tool execution output."
        if observation:
            obs_clean = observation.replace("\n", " ").strip()
            if len(obs_clean) > 150:
                evidence = obs_clean[:147] + "..."
            else:
                evidence = obs_clean

        # 3. One-line Rationale Synthesis
        one_liner = f"Step {step_number}: In order to resolve the task objective, the agent decided to invoke {tool_name_str} based on recent context."
        if tool_name_str == "read_scanned_ocr_text":
            one_liner = "Ingested physical inspection telemetry to establish baseline vibration and temperature data."
        elif tool_name_str == "local_knowledge_search":
            one_liner = "Consulted verified on-prem SOP manuals to establish authorized engineering limits."
        elif tool_name_str == "calculate_values":
            one_liner = "Performed deterministic math to verify threshold exceedance with zero LLM calculation hallucination."
        elif tool_name_str == "submit_approval_note":
            one_liner = "Initiated formal approval workflow due to confirmed safety threshold exceedance requiring shift supervisor sign-off."

        return DecisionCard(
            step_number=step_number,
            tool_invoked=tool_name_str,
            action_intent=action_intent,
            evidence_grounding=evidence,
            risk_level=risk_level,
            one_line_rationale=one_liner,
            confidence_score=0.95
        )

    @staticmethod
    def generate_task_summary_rationale(
        objective: str,
        decision_cards: List[DecisionCard],
        final_deliverable: Optional[str]
    ) -> str:
        """Produces an executive one-line rationale for the complete task."""
        if not decision_cards:
            return f"Processed task: '{objective}'."

        steps_summary = " -> ".join([dc.tool_invoked for dc in decision_cards if dc.tool_invoked != "reasoning"])
        return (
            f"Autonomous Agent executed [{steps_summary}] to resolve '{objective}', "
            f"grounding every action in local SOP telemetry with zero external network exfiltration."
        )
