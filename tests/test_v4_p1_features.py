"""
Unit tests for P1 v4 Features:
- Schema-Constrained Tool Validation
- Explainability Layer (Decision Cards & One-Line Rationales)
- Cross-Model Consistency Verification
- Role-Based Access Control (RBAC) & Two-Person Safety Gate
- Multi-Agent Specialization (Extraction -> Drafting -> Verification)
- Retrieval-Augmented Tool Selection from Audit Traces
"""

import pytest
from pydantic import BaseModel
from agent_core.schema_validator import SchemaValidator
from agent_core.tool_executor import ToolExecutor
from agent_core.approval_gate import ApprovalGate, ActionRiskLevel
from agent_core.explainability import ExplainabilityEngine, DecisionCard
from agent_core.consistency_check import CrossModelConsistencyChecker
from auth.rbac import RBACManager, UserRole, Permission, UserProfile
from agent_core.multi_agent.sub_agents import (
    MultiAgentCoordinator, ExtractionAgent, DraftingAgent, VerificationAgent, ExtractionPayload
)
from agent_core.trace_tool_selector import TraceToolSelector
from model_router.registry import ModelRegistry
from model_router.adapters.base import MockLocalAdapter


# ==========================================
# 1. Schema-Constrained Tool Validation
# ==========================================

class MockToolArgs(BaseModel):
    query: str
    max_results: int = 5


def test_schema_validator_success_and_failure():
    validator = SchemaValidator()
    validator.register_tool_schema("test_search", MockToolArgs)

    # Valid arguments
    res_valid = validator.validate("test_search", {"query": "CDU pump", "max_results": 3})
    assert res_valid.is_valid is True
    assert res_valid.validated_args["max_results"] == 3

    # Invalid arguments (missing required 'query')
    res_invalid = validator.validate("test_search", {"max_results": 10})
    assert res_invalid.is_valid is False
    assert "query" in res_invalid.error_message
    assert res_invalid.remediation_hint is not None


def test_tool_executor_schema_enforcement():
    executor = ToolExecutor()
    # Tool 'calculate_values' expects 'expression: str'
    # Test valid
    res_ok = executor.execute("calculate_values", {"expression": "100 / 4"})
    assert res_ok.is_error is False
    assert "Result: 25.0" in str(res_ok.output)

    # Test invalid schema (missing expression, passing bogus key)
    res_bad = executor.execute("calculate_values", {"bogus_param": 123})
    assert res_bad.is_error is True
    assert "SCHEMA_VALIDATION_ERROR" in str(res_bad.output)
    assert res_bad.validation_error is not None


# ==========================================
# 2. Explainability Layer
# ==========================================

def test_explainability_engine():
    card = ExplainabilityEngine.generate_step_rationale(
        step_number=1,
        thought="Need to check pump vibration limits.",
        tool_name="read_scanned_ocr_text",
        tool_args={"file_path": "cdu_pump.pdf"},
        observation="Observed vibration: 6.8 mm/s RMS."
    )

    assert card.step_number == 1
    assert "cdu_pump.pdf" in card.action_intent
    assert "6.8 mm/s" in card.evidence_grounding
    assert "Ingested physical inspection telemetry" in card.one_line_rationale

    summary = ExplainabilityEngine.generate_task_summary_rationale(
        objective="Pump vibration analysis",
        decision_cards=[card],
        final_deliverable="Complete"
    )
    assert "read_scanned_ocr_text" in summary
    assert "Pump vibration analysis" in summary


# ==========================================
# 3. Cross-Model Consistency Check
# ==========================================

def test_cross_model_consistency_agreement():
    registry = ModelRegistry()
    # Both models return concurring shutdown recommendations
    adapter_a = MockLocalAdapter("qwen2.5-72b-instruct")
    adapter_a.register_response(
        "diagnostic context",
        "Recommended action: Emergency shutdown and bearing overhaul. Observed vibration: 6.8 mm/s. Critical urgency."
    )
    registry.register_adapter("qwen2.5-72b-instruct", adapter_a)

    adapter_b = MockLocalAdapter("qwen2.5-32b-instruct")
    adapter_b.register_response(
        "diagnostic context",
        "Immediate isolation and shutdown required. Observed vibration: 6.8 mm/s. Critical urgency."
    )
    registry.register_adapter("qwen2.5-32b-instruct", adapter_b)

    checker = CrossModelConsistencyChecker(registry=registry)
    report = checker.verify_consistency("Diagnostic context for CDU booster pump.")

    assert report.is_consistent is True
    assert report.agreement_score >= 0.85
    assert report.flagged_for_supervisor_review is False


def test_cross_model_consistency_conflict_detected():
    registry = ModelRegistry()
    # Model A says shutdown (critical); Model B says continue monitoring (normal)
    adapter_a = MockLocalAdapter("qwen2.5-72b-instruct")
    adapter_a.register_response("diagnostic context", "Emergency shutdown. Critical urgency.")
    registry.register_adapter("qwen2.5-72b-instruct", adapter_a)

    adapter_b = MockLocalAdapter("qwen2.5-32b-instruct")
    adapter_b.register_response("diagnostic context", "Continue monitoring. Normal vibration readings.")
    registry.register_adapter("qwen2.5-32b-instruct", adapter_b)

    checker = CrossModelConsistencyChecker(registry=registry)
    report = checker.verify_consistency("Diagnostic context for CDU booster pump.")

    assert report.is_consistent is False
    assert report.flagged_for_supervisor_review is True
    assert "Action mismatch" in report.discrepancy_details


# ==========================================
# 4. RBAC & Two-Person Approval Gate
# ==========================================

def test_rbac_permissions():
    rbac = RBACManager()
    assert rbac.can_approve_action("op_rajesh") is False   # Operator cannot approve
    assert rbac.can_approve_action("eng_priya") is False   # Engineer cannot approve
    assert rbac.can_approve_action("sup_anand") is True    # Supervisor can approve standard
    assert rbac.can_approve_action("sup_anand", is_safety_critical=True) is True


def test_approval_gate_rbac_denial():
    gate = ApprovalGate(auto_approve_for_testing=False)
    # Standard high-consequence action
    approved, req = gate.check_and_request_approval(
        "submit_approval_note",
        {"subject": "Overhaul approval", "unit": "CDU-1", "recommendation": "Standard note"}
    )
    assert approved is False
    req_id = req.request_id

    # Operator tries to approve -> Denied
    ok, msg = gate.resolve_request(req_id, approved=True, username="op_rajesh")
    assert ok is False
    assert "Permission Denied" in msg


def test_approval_gate_two_person_rule_for_safety_critical():
    gate = ApprovalGate(auto_approve_for_testing=False)
    # Safety critical action (contains "emergency" / "shutdown")
    approved, req = gate.check_and_request_approval(
        "submit_approval_note",
        {"subject": "Emergency unit shutdown", "recommendation": "Emergency isolation of CDU-II"}
    )
    assert req.is_safety_critical is True
    assert req.approvals_required == 2

    # First supervisor approves
    ok1, msg1 = gate.resolve_request(req.request_id, approved=True, username="sup_anand")
    assert ok1 is False
    assert "awaiting 2nd supervisor sign-off" in msg1

    # Same supervisor tries to approve again -> Blocked by Two-Person Rule
    ok_repeat, msg_repeat = gate.resolve_request(req.request_id, approved=True, username="sup_anand")
    assert ok_repeat is False
    assert "Two-Person Rule Violation" in msg_repeat

    # Second distinct supervisor approves -> Fully authorized
    ok2, msg2 = gate.resolve_request(req.request_id, approved=True, username="sup_mehta")
    assert ok2 is True
    assert "fully approved (2/2 sign-offs)" in msg2


# ==========================================
# 5. Multi-Agent Specialization
# ==========================================

def test_multi_agent_pipeline():
    coordinator = MultiAgentCoordinator()
    raw_telemetry = (
        "UNIT: CDU-II P-101B Booster Pump\n"
        "OBSERVED VIBRATION: 6.8 mm/s\n"
        "TEMPERATURE: 84.0 deg C\n"
        "SOP LIMIT: 4.5 mm/s"
    )

    draft, verification, extraction = coordinator.run_pipeline(raw_telemetry)

    assert extraction.equipment_tag == "CDU-II P-101B Booster Pump"
    assert extraction.observed_vibration == 6.8
    assert extraction.is_exceeded is True

    assert draft.quoted_vibration == 6.8
    assert draft.severity == "CRITICAL"

    assert verification.is_valid is True
    assert verification.accuracy_score == 1.0
    assert len(verification.hallucinations_detected) == 0


def test_multi_agent_adversarial_catch():
    adapter = MockLocalAdapter("mock-agent")
    verifier = VerificationAgent(adapter)

    # Ground truth extraction
    extraction = ExtractionPayload(
        equipment_tag="CDU-II P-101B",
        observed_vibration=6.8,
        sop_threshold_limit=4.5
    )

    # Hallucinated draft (claims 3.2 mm/s instead of 6.8 mm/s)
    drafter = DraftingAgent(adapter)
    corrupted_draft = drafter.draft(extraction)
    corrupted_draft.quoted_vibration = 3.2  # Corrupt value

    res = verifier.verify(extraction, corrupted_draft)
    assert res.is_valid is False
    assert any("Numerical hallucination" in h for h in res.hallucinations_detected)


# ==========================================
# 6. Retrieval-Augmented Tool Selection
# ==========================================

def test_trace_tool_selector():
    selector = TraceToolSelector()
    objective = "Verify CDU crude pump vibration reading against SOP threshold and file note."
    recommended_tools = selector.recommend_tool_plan(objective)

    assert len(recommended_tools) > 0
    assert "read_scanned_ocr_text" in recommended_tools
    assert "local_knowledge_search" in recommended_tools
    assert "submit_approval_note" in recommended_tools
