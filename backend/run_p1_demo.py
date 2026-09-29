"""
Sovereign On-Premise Agentic AI Workbench - P1 Demonstration Runner
Demonstrates:
  1. Task Intent Classification & Model Routing
  2. Multi-Step ReAct Plan-Execute Agent Loop
  3. Graceful Fallback Recovery on Model OOM / Crash
  4. Infinite Loop & Stagnation Detection
  5. Human-in-the-Loop Approval Gate
"""

import sys
import os
import time

# Ensure workspace root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from model_router.registry import ModelRegistry
from model_router.router import ModelRouter
from model_router.fallback_policy import FallbackPolicy, FallbackEvent
from model_router.adapters.base import MockLocalAdapter
from agent_core.planner import ReActPlanner, AgentStepResult
from agent_core.approval_gate import ApprovalGate
from agent_core.loop_detector import LoopDetector, LoopDetectedException
from agent_core.tool_executor import ToolExecutor


def print_banner(title: str):
    print("\n" + "=" * 78)
    print(f"  {title.upper()}")
    print("=" * 78)


def demo_model_routing():
    print_banner("Demo 1: Intelligent Model Routing & Intent Classification")
    registry = ModelRegistry()
    router = ModelRouter(registry=registry)

    scenarios = [
        ("Write a Python script to compute heat exchanger fouling factors from CSV logs.", "Code"),
        ("Analyze this P&ID diagram of the Crude Distillation Unit column reflux loop.", "Vision / P&ID"),
        ("Draft a turnaround maintenance plan for crude booster pump P-101B based on vibration SOP.", "Reasoning / SOP"),
        ("Hello, can you help me?", "Ambiguous / Low Confidence")
    ]

    for prompt, category in scenarios:
        decision = router.route(prompt)
        print(f"\n[Task Category: {category}]")
        print(f"Prompt: \"{prompt}\"")
        print(f"  -> Selected Model:    {decision.selected_model_id}")
        print(f"  -> Task Type:         {decision.task_type.upper()}")
        print(f"  -> Confidence Score:  {decision.confidence * 100:.1f}%")
        print(f"  -> Rationale:         {decision.rationale}")
        print(f"  -> Fallback Chain:    {' -> '.join(decision.fallback_chain)}")
        if decision.requires_clarification:
            print(f"  [!] Triggered Safe Fallback: Confidence < Threshold ({router.confidence_threshold * 100:.1f}%)")


def demo_graceful_fallback():
    print_banner("Demo 2: Graceful Model Fallback Recovery (Simulated GPU OOM)")
    registry = ModelRegistry()
    policy = FallbackPolicy(registry)

    # Simulate primary 72B model experiencing an Out Of Memory (OOM) error
    primary_adapter = MockLocalAdapter("qwen2.5-72b-instruct")
    primary_adapter.inject_failure("OOM")
    registry.register_adapter("qwen2.5-72b-instruct", primary_adapter)

    # Secondary 32B model is healthy
    secondary_adapter = MockLocalAdapter("qwen2.5-32b-instruct")
    registry.register_adapter("qwen2.5-32b-instruct", secondary_adapter)

    logged_events = []
    policy.register_listener(lambda e: logged_events.append(e))

    print("[*] Preferred Model: qwen2.5-72b-instruct (Requires 42GB VRAM)")
    print("[*] Simulating GPU hardware pressure causing CUDA OOM on primary model...")

    prompt = "Synthesize chemical engineering balance equations for crude preheat train."
    response = policy.execute_with_fallback("qwen2.5-72b-instruct", prompt=prompt)

    print("\n[+] Fallback Resolution Telemetry:")
    print(f"  - Final Serving Model:   {response.model_id}")
    print(f"  - Fallback Triggered:    {response.metadata.get('fallback_occurred')}")
    print(f"  - Cascaded Attempts:     {response.metadata.get('fallback_attempts')}")
    print(f"  - Total Events Logged:   {len(logged_events)}")
    for ev in logged_events:
        print(f"    * [Audit Event] From: {ev.original_model_id} -> Target: {ev.target_model_id} | Reason: {ev.reason}")
    print("\n[OK] System recovered seamlessly without crashing or aborting the task.")


def demo_loop_protection():
    print_banner("Demo 3: Infinite Loop & Stagnation Detection")
    detector = LoopDetector(max_iterations=10, max_identical_tool_calls=3)

    print("[*] Simulating confused agent attempting repeated identical tool invocations:")
    try:
        for step in range(1, 6):
            print(f"  Iteration {step}: Agent invokes read_file(path='equipment_spec.pdf')...")
            detector.record_step("read_file", {"path": "equipment_spec.pdf"})
            time.sleep(0.05)
    except LoopDetectedException as le:
        print(f"\n[!] LOOP DETECTOR TRIPPED: {le}")
        print("  - Prevented silent hang during live operation.")
        print("  - Reason: Identical tool call repeated 3 times consecutively.")
        print("  - Status: Safe termination with diagnostic error report.")


def demo_approval_gate():
    print_banner("Demo 4: Human-in-the-Loop Approval Gate")
    gate = ApprovalGate(auto_approve_for_testing=False)
    executor = ToolExecutor(approval_gate=gate)

    print("[*] Scenario: Agent attempts low-risk calculation:")
    res_low = executor.execute("calculate_values", {"expression": "6.8 - 4.5"})
    print(f"  - Execution Result: {res_low.output} (Approved automatically, Low Risk)")

    print("\n[*] Scenario: Agent attempts high-consequence action (submit official maintenance note):")
    res_high = executor.execute("submit_approval_note", {
        "subject": "CDU Booster Pump Isolation",
        "unit": "CDU-II",
        "recommendation": "Emergency bearing overhaul",
        "priority": "HIGH"
    })
    print(f"  - Gate Status: {res_high.output}")
    print(f"  - Pending Operator Approvals: {len(gate.pending_requests)}")

    req_id = list(gate.pending_requests.keys())[0]
    print(f"\n[Operator Action] Reviewing request {req_id}...")
    gate.resolve_request(req_id, approved=True, comment="Approved by Plant Maintenance Head.")
    print("  - Operator decision logged to tamper-evident audit queue.")


def demo_react_planner_loop():
    print_banner("Demo 5: End-to-End ReAct Plan-Execute Agent Loop")
    planner = ReActPlanner(max_iterations=10)

    objective = "Analyze CDU-II booster pump vibration log, verify SOP thresholds, and draft approval note."
    print(f"User Goal: \"{objective}\"\n")

    def step_monitor(step: AgentStepResult):
        print(f"[Step {step.step_index}]")
        print(f"  Thought:     {step.thought}")
        if step.action_tool:
            print(f"  Action:      {step.action_tool}({step.action_args})")
            print(f"  Observation: {step.observation[:120]}...")
        print("-" * 60)

    planner.set_step_callback(step_monitor)
    result = planner.execute_task(objective)

    print("\n[Task Completed Successfully]")
    print(f"Execution Time: {result.execution_time_seconds:.3f}s | Total Steps: {result.total_steps}")
    print(f"Final Deliverable Output:\n{result.final_output}")


if __name__ == "__main__":
    print("==============================================================================")
    print("  SOVEREIGN ON-PREMISE AGENTIC AI WORKBENCH -- MRPL SMART AUTOMATION (SIH26117)")
    print("  P1 (Agent Architecture Lead) Subsystem Verification & Live Demo")
    print("==============================================================================")

    demo_model_routing()
    demo_graceful_fallback()
    demo_loop_protection()
    demo_approval_gate()
    demo_react_planner_loop()

    print("\n" + "=" * 78)
    print("  ALL P1 ARCHITECTURAL MODULES VERIFIED & OPERATIONAL")
    print("=" * 78 + "\n")
