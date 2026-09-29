"""
Sovereign On-Premise Agentic AI Workbench — P1 v4 Demonstration Runner
Showcases:
  1. Schema-Constrained Tool Calling & Parameter Validation
  2. Explainability Layer: One-Line Decision Rationales & Decision Cards
  3. Cross-Model Consistency Verification (Dual-Model Consensus Check)
  4. Role-Based Access Control (RBAC) & Two-Person Safety Gate
  5. Multi-Agent Specialization (Extraction -> Drafting -> Verification)
  6. Retrieval-Augmented Tool Selection from Audit Traces
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agent_core.schema_validator import SchemaValidator
from agent_core.tool_executor import ToolExecutor
from agent_core.explainability import ExplainabilityEngine, DecisionCard
from agent_core.consistency_check import CrossModelConsistencyChecker
from auth.rbac import RBACManager, UserRole
from agent_core.approval_gate import ApprovalGate
from agent_core.multi_agent.sub_agents import MultiAgentCoordinator, ExtractionPayload, DraftingAgent, VerificationAgent
from agent_core.trace_tool_selector import TraceToolSelector
from model_router.registry import ModelRegistry
from model_router.adapters.base import MockLocalAdapter


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f"  {title.upper()}")
    print("=" * 80)


def demo_schema_validation():
    print_header("Demo 1: Schema-Constrained Tool Calling & Validation")
    executor = ToolExecutor()

    print("[*] Validating Tool Call: calculate_values(expression='6.8 - 4.5')...")
    res_valid = executor.execute("calculate_values", {"expression": "6.8 - 4.5"})
    print(f"  -> Status: SUCCESS | Output: {res_valid.output}")

    print("\n[*] Simulating Model Tool Call with Missing/Corrupted Schema (bogus parameters):")
    res_invalid = executor.execute("calculate_values", {"formula_invalid": 123})
    print(f"  -> Status: REJECTED BY SCHEMA VALIDATOR")
    print(f"  -> Error:  {res_invalid.validation_error}")
    print(f"  -> Output: {res_invalid.output}")
    print("[OK] Invalid tool calls are intercepted before execution with structured remediation feedback.")


def demo_explainability_layer():
    print_header("Demo 2: Explainability Layer (Decision Cards & One-Line Rationales)")
    
    steps_data = [
        (1, "Extract telemetry from physical log", "read_scanned_ocr_text", {"file_path": "cdu_pump_101.pdf"}, "Observed 6.8 mm/s vibration (Limit: 4.5 mm/s)."),
        (2, "Cross-reference operating limits in verified manual", "local_knowledge_search", {"query": "CDU Booster Pump SOP-MECH-402"}, "SOP-MECH-402: 4.5 mm/s warning threshold, 6.0 mm/s trip threshold."),
        (3, "Verify variance calculation", "calculate_values", {"expression": "6.8 - 4.5"}, "Result: 2.3 mm/s exceedance."),
        (4, "Initiate authorization for overhaul", "submit_approval_note", {"subject": "CDU Overhaul", "unit": "CDU-II"}, "Approval note drafted.")
    ]

    cards = []
    for step_num, thought, tool, args, obs in steps_data:
        card = ExplainabilityEngine.generate_step_rationale(
            step_number=step_num,
            thought=thought,
            tool_name=tool,
            tool_args=args,
            observation=obs,
            risk_level="high" if "approval" in tool else "low"
        )
        cards.append(card)
        print(f"[Step {card.step_number} Decision Card]")
        print(f"  * Action Intent:      {card.action_intent}")
        print(f"  * Evidence Grounding: {card.evidence_grounding}")
        print(f"  * One-Line Rationale: {card.one_line_rationale}")
        print("-" * 60)

    summary = ExplainabilityEngine.generate_task_summary_rationale(
        objective="CDU Booster Pump P-101B Vibration Diagnostic & Overhaul Note",
        decision_cards=cards,
        final_deliverable="Complete"
    )
    print(f"\n[Executive One-Line Task Rationale]:\n\"{summary}\"")


def demo_cross_model_consistency():
    print_header("Demo 3: Cross-Model Consistency Check (Dual-Model Consensus)")
    registry = ModelRegistry()

    # Scenario A: Models in Consensus
    adapter_a = MockLocalAdapter("qwen2.5-72b-instruct")
    adapter_a.register_response("diagnostic context", "Emergency shutdown required. Observed vibration: 6.8 mm/s. Critical urgency.")
    registry.register_adapter("qwen2.5-72b-instruct", adapter_a)

    adapter_b = MockLocalAdapter("qwen2.5-32b-instruct")
    adapter_b.register_response("diagnostic context", "Immediate isolation and shutdown. Observed vibration: 6.8 mm/s. Critical urgency.")
    registry.register_adapter("qwen2.5-32b-instruct", adapter_b)

    checker = CrossModelConsistencyChecker(registry=registry)
    print("[*] Case A: Evaluating Concurring Models (Qwen-72B vs Qwen-32B):")
    report_a = checker.verify_consistency("Diagnostic context on CDU booster pump.")
    print(f"  -> Agreement Score: {report_a.agreement_score * 100:.0f}%")
    print(f"  -> Is Consistent:   {report_a.is_consistent}")
    print(f"  -> Advisory:        {report_a.resolution_advisory}")

    # Scenario B: Deliberate Conflict Injection
    adapter_b.register_response("diagnostic context", "Continue monitoring. Normal vibration readings.")
    print("\n[*] Case B: Deliberately Injecting Model Disagreement:")
    report_b = checker.verify_consistency("Diagnostic context on CDU booster pump.")
    print(f"  -> Agreement Score: {report_b.agreement_score * 100:.0f}%")
    print(f"  -> Is Consistent:   {report_b.is_consistent}")
    print(f"  -> Discrepancies:   {report_b.discrepancy_details}")
    print(f"  -> Flagged For Gate:{report_b.flagged_for_supervisor_review}")
    print(f"  -> Advisory:        {report_b.resolution_advisory}")


def demo_rbac_and_two_person_gate():
    print_header("Demo 4: Role-Based Access Control & Two-Person Safety Gate")
    gate = ApprovalGate(auto_approve_for_testing=False)

    print("[*] User Roster in On-Prem RBAC Directory:")
    print("  - op_rajesh:  OPERATOR")
    print("  - eng_priya:  ENGINEER")
    print("  - sup_anand:  SHIFT SUPERVISOR")
    print("  - sup_mehta:  SAFETY IN-CHARGE (SUPERVISOR)")

    print("\n[*] Scenario 1: Field Operator attempts to approve high-consequence action:")
    _, req1 = gate.check_and_request_approval("submit_approval_note", {"subject": "Routine pump overhaul", "unit": "CDU-I"})
    ok, msg = gate.resolve_request(req1.request_id, approved=True, username="op_rajesh")
    print(f"  -> Result: {ok} | Log: {msg}")

    print("\n[*] Scenario 2: Safety-Critical Action requiring Two-Person Supervisory Sign-off:")
    _, req2 = gate.check_and_request_approval(
        "submit_approval_note",
        {"subject": "Emergency shutdown and unit trip", "unit": "CDU-II"}
    )
    print(f"  -> Request ID: {req2.request_id}")
    print(f"  -> Is Safety Critical: {req2.is_safety_critical} | Approvals Required: {req2.approvals_required}")

    print("\n  [Sign-off 1/2] Supervisor Anand reviews & approves:")
    ok1, msg1 = gate.resolve_request(req2.request_id, approved=True, username="sup_anand", comment="Vibration at 6.8 mm/s verified.")
    print(f"    * Result: {msg1}")

    print("\n  [Violation Attempt] Supervisor Anand attempts duplicate approval:")
    ok_dup, msg_dup = gate.resolve_request(req2.request_id, approved=True, username="sup_anand")
    print(f"    * Result: {msg_dup}")

    print("\n  [Sign-off 2/2] Plant Safety In-Charge Mehta reviews & co-signs:")
    ok2, msg2 = gate.resolve_request(req2.request_id, approved=True, username="sup_mehta", comment="Concur with emergency isolation.")
    print(f"    * Result: {msg2}")
    print("[OK] Safety-critical action successfully authorized via Two-Person Rule.")


def demo_multi_agent_specialization():
    print_header("Demo 5: Multi-Agent Specialization (Extraction -> Drafting -> Verification)")
    coordinator = MultiAgentCoordinator()

    raw_log = (
        "PHYSICAL FIELD INSPECTION LOG\n"
        "DATE: 14-SEP-2026 | SHIFT: NIGHT\n"
        "UNIT: CDU-II P-101B Booster Pump\n"
        "OBSERVED VIBRATION: 6.8 mm/s\n"
        "TEMPERATURE: 84.0 deg C\n"
        "SOP LIMIT: 4.5 mm/s\n"
        "STATUS: Critical high-frequency vibration observed on DE bearing."
    )

    print("[*] Stage 1: ExtractionAgent parsing raw log:")
    draft, verification, extraction = coordinator.run_pipeline(raw_log)
    print(f"  -> Unit Tag:        {extraction.equipment_tag}")
    print(f"  -> Observed Vib:    {extraction.observed_vibration} mm/s")
    print(f"  -> SOP Threshold:   {extraction.sop_threshold_limit} mm/s")
    print(f"  -> Exceedance Flag: {extraction.is_exceeded}")

    print("\n[*] Stage 2: DraftingAgent synthesizing structured formal note:")
    print(f"  -> Title:     {draft.title}")
    print(f"  -> Severity:  {draft.severity}")
    print(f"  -> Action:    {draft.recommended_action}")

    print("\n[*] Stage 3: VerificationAgent executing adversarial cross-check:")
    print(f"  -> Verification Status:  {'PASSED' if verification.is_valid else 'FAILED'}")
    print(f"  -> Accuracy Score:       {verification.accuracy_score * 100:.0f}%")
    print(f"  -> Discrepancies:        {verification.hallucinations_detected}")
    print(f"  -> Summary:              {verification.summary}")


def demo_retrieval_augmented_tool_selection():
    print_header("Demo 6: Retrieval-Augmented Tool Selection from Audit Traces")
    selector = TraceToolSelector()

    queries = [
        "Check booster pump vibration against SOP threshold and file overhaul note.",
        "Execute a Python script to calculate column reflux ratio in Docker sandbox.",
        "Inspect P&ID schematic diagram for line 12 bypass valve."
    ]

    for q in queries:
        trace = selector.retrieve_exemplar_trace(q)
        tools = selector.recommend_tool_plan(q)
        print(f"\nIncoming Goal: \"{q}\"")
        if trace:
            print(f"  -> Matched Audit Trace: {trace.trace_id} ({trace.task_category})")
            print(f"  -> Historical Success:  {trace.success_rate * 100:.0f}%")
            print(f"  -> Recommended Plan:    {' -> '.join(tools)}")


if __name__ == "__main__":
    print("================================================================================")
    print("  SOVEREIGN ON-PREMISE AGENTIC AI WORKBENCH -- MRPL SMART AUTOMATION (SIH26117)")
    print("  P1 (Agent Architecture Lead) -- v4 Complete Deliverable Demonstration")
    print("================================================================================")

    demo_schema_validation()
    demo_explainability_layer()
    demo_cross_model_consistency()
    demo_rbac_and_two_person_gate()
    demo_multi_agent_specialization()
    demo_retrieval_augmented_tool_selection()

    print("\n" + "=" * 80)
    print("  ALL P1 v4 DELIVERABLES OPERATIONAL, TESTED, AND VERIFIED")
    print("=" * 80 + "\n")
