"""
Unit tests for Agent Core: Planner, LoopDetector, ApprovalGate, and Memory.
"""

import pytest
from agent_core.memory import AgentMemory
from agent_core.loop_detector import LoopDetector, LoopDetectedException
from agent_core.approval_gate import ApprovalGate, ActionRiskLevel
from agent_core.tool_executor import ToolExecutor
from agent_core.planner import ReActPlanner
from model_router.router import ModelRouter


def test_agent_memory():
    mem = AgentMemory(task_objective="Test pump diagnostics")
    mem.set_plan(["Step 1: Check logs", "Step 2: Compare thresholds"])

    assert len(mem.plan) == 2
    step1 = mem.get_current_pending_step()
    assert step1.step_number == 1

    mem.update_step_status(1, "completed", observation="Logs verified.")
    step2 = mem.get_current_pending_step()
    assert step2.step_number == 2

    context = mem.get_formatted_context()
    assert "Test pump diagnostics" in context
    assert "Logs verified." in context


def test_loop_detector_iteration_cap():
    detector = LoopDetector(max_iterations=5)
    for i in range(5):
        detector.record_step(f"tool_{i}", {"arg": i})

    with pytest.raises(LoopDetectedException) as exc:
        detector.record_step("tool_overflow", {"arg": 99})

    assert "Iteration cap reached" in str(exc.value)


def test_loop_detector_identical_tool_calls():
    detector = LoopDetector(max_iterations=15, max_identical_tool_calls=3)

    detector.record_step("read_file", {"path": "sop.txt"})
    detector.record_step("read_file", {"path": "sop.txt"})

    with pytest.raises(LoopDetectedException) as exc:
        detector.record_step("read_file", {"path": "sop.txt"})

    assert "Repetitive tool call detected" in str(exc.value)


def test_loop_detector_cycle_detection():
    detector = LoopDetector(max_iterations=15)

    detector.record_step("tool_A", {"x": 1})
    detector.record_step("tool_B", {"y": 2})
    detector.record_step("tool_A", {"x": 1})

    with pytest.raises(LoopDetectedException) as exc:
        detector.record_step("tool_B", {"y": 2})

    assert "Cyclical alternating execution detected" in str(exc.value)


def test_approval_gate_high_consequence_pausing():
    gate = ApprovalGate(auto_approve_for_testing=False)
    executor = ToolExecutor(approval_gate=gate)

    # Low risk tool: should execute immediately
    low_res = executor.execute("calculate_values", {"expression": "10 + 20"})
    assert low_res.is_error is False
    assert low_res.approval_required is False
    assert "Result: 30" in str(low_res.output)

    # High risk tool: submit_approval_note should pause execution
    high_res = executor.execute("submit_approval_note", {
        "subject": "Overhaul approval",
        "unit": "CDU-1",
        "recommendation": "Shut down"
    })
    assert high_res.approval_required is True
    assert "ACTION_PAUSED" in high_res.output
    assert len(gate.pending_requests) == 1

    # Operator approves
    req_id = list(gate.pending_requests.keys())[0]
    gate.resolve_request(req_id, approved=True, comment="Approved by Plant In-Charge")
    assert len(gate.pending_requests) == 0


def test_react_planner_end_to_end():
    planner = ReActPlanner(max_iterations=10)
    result = planner.execute_task("Analyze CDU pump vibration log and prepare maintenance approval note.")

    assert result.status == "completed"
    assert result.total_steps >= 2
    assert "SOVEREIGN AGENT DELIVERABLE" in result.final_output
    assert result.execution_time_seconds > 0.0
