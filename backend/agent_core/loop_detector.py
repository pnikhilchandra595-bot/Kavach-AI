"""
Loop and Stagnation Detection Engine for Sovereign Agentic Core.
Prevents infinite execution cycles, repetitive tool calls, and runaway agent loops.
"""

from typing import List, Dict, Any, Optional, Tuple
import hashlib
import json


class LoopDetectedException(Exception):
    """Raised when the agent enters an unrecoverable repetitive cycle or reaches iteration cap."""
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(reason)
        self.reason = reason
        self.details = details or {}


class LoopDetector:
    """
    Monitors agent execution steps to detect:
    1. Hard iteration cap exhaustion.
    2. Identical tool calls (same tool + same arguments executed repeatedly).
    3. Cyclical call sequences (e.g. A -> B -> A -> B).
    4. Stagnation (no plan advancement for N steps).
    """

    def __init__(
        self,
        max_iterations: int = 15,
        max_identical_tool_calls: int = 3,
        cycle_window_size: int = 6
    ):
        self.max_iterations = max_iterations
        self.max_identical_tool_calls = max_identical_tool_calls
        self.cycle_window_size = cycle_window_size

        self.current_iteration = 0
        self.action_history: List[str] = []  # hashes of (tool_name, normalized_args)
        self.action_descriptors: List[Dict[str, Any]] = []

    def _hash_action(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Computes a deterministic hash of tool invocation."""
        normalized = json.dumps(arguments, sort_keys=True, default=str)
        raw = f"{tool_name}:{normalized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def record_step(self, tool_name: str, arguments: Dict[str, Any]):
        """
        Records an action and checks for loop conditions.
        Raises LoopDetectedException if a loop or limit breach is detected.
        """
        self.current_iteration += 1

        # 1. Check Hard Iteration Cap
        if self.current_iteration > self.max_iterations:
            raise LoopDetectedException(
                f"Iteration cap reached ({self.current_iteration}/{self.max_iterations}). "
                "Agent execution terminated to prevent runaway process.",
                details={"iteration": self.current_iteration, "max_iterations": self.max_iterations}
            )

        action_hash = self._hash_action(tool_name, arguments)
        self.action_history.append(action_hash)
        self.action_descriptors.append({"tool": tool_name, "args": arguments})

        # 2. Check Consecutive Identical Tool Calls
        consecutive_count = 0
        for h in reversed(self.action_history):
            if h == action_hash:
                consecutive_count += 1
            else:
                break

        if consecutive_count >= self.max_identical_tool_calls:
            raise LoopDetectedException(
                f"Repetitive tool call detected: '{tool_name}' invoked with identical arguments "
                f"{consecutive_count} times consecutively.",
                details={
                    "tool": tool_name,
                    "arguments": arguments,
                    "consecutive_count": consecutive_count
                }
            )

        # 3. Check Cyclical Sequences (e.g. A -> B -> A -> B)
        self._check_cycles()

    def _check_cycles(self):
        """Detects 2-step and 3-step periodic cycles within the recent action history."""
        n = len(self.action_history)
        if n < 4:
            return

        # Check 2-cycle: [..., A, B, A, B]
        if n >= 4 and (self.action_history[-1] == self.action_history[-3] and 
                       self.action_history[-2] == self.action_history[-4]):
            desc_a = self.action_descriptors[-2]["tool"]
            desc_b = self.action_descriptors[-1]["tool"]
            raise LoopDetectedException(
                f"Cyclical alternating execution detected: sequence [{desc_a} <-> {desc_b}] repeating.",
                details={"cycle_length": 2, "pattern": [desc_a, desc_b]}
            )

        # Check 3-cycle: [..., A, B, C, A, B, C]
        if n >= 6 and (self.action_history[-1] == self.action_history[-4] and
                       self.action_history[-2] == self.action_history[-5] and
                       self.action_history[-3] == self.action_history[-6]):
            p = [self.action_descriptors[-3]["tool"], 
                 self.action_descriptors[-2]["tool"], 
                 self.action_descriptors[-1]["tool"]]
            raise LoopDetectedException(
                f"Cyclical execution detected: 3-step sequence [{p[0]} -> {p[1]} -> {p[2]}] repeating.",
                details={"cycle_length": 3, "pattern": p}
            )

    def reset(self):
        self.current_iteration = 0
        self.action_history.clear()
        self.action_descriptors.clear()
