"""
Working Memory and Scratchpad for Sovereign Agentic Core.
Maintains plan state, execution history, observation cache, and token limits.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import time


class PlanStep(BaseModel):
    step_number: int
    description: str
    status: str = "pending"  # "pending", "in_progress", "completed", "failed", "skipped"
    tool_required: Optional[str] = None
    observation: Optional[str] = None


class ToolInvocation(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    timestamp: float = Field(default_factory=time.time)
    duration_seconds: float = 0.0
    status: str = "success"  # "success", "error", "paused_by_gate"


class AgentMemory:
    """
    Stateful memory tracking the life-cycle of an agentic workflow.
    """

    def __init__(self, task_objective: str, max_history_items: int = 50):
        self.task_objective: str = task_objective
        self.max_history_items: int = max_history_items
        self.plan: List[PlanStep] = []
        self.tool_invocations: List[ToolInvocation] = []
        self.scratchpad: List[Dict[str, Any]] = []
        self.final_answer: Optional[str] = None
        self.total_tokens_used: int = 0
        self.created_at: float = time.time()

    def set_plan(self, steps: List[str]):
        """Sets the initial decomposition plan."""
        self.plan = [
            PlanStep(step_number=idx + 1, description=desc)
            for idx, desc in enumerate(steps)
        ]

    def update_step_status(self, step_number: int, status: str, observation: Optional[str] = None):
        for s in self.plan:
            if s.step_number == step_number:
                s.status = status
                if observation:
                    s.observation = observation
                break

    def get_current_pending_step(self) -> Optional[PlanStep]:
        for s in self.plan:
            if s.status in ("pending", "in_progress"):
                return s
        return None

    def record_thought(self, thought: str):
        self.scratchpad.append({
            "type": "thought",
            "content": thought,
            "timestamp": time.time()
        })

    def record_tool_call(self, tool_name: str, arguments: Dict[str, Any], 
                         output: Any, duration: float = 0.0, status: str = "success"):
        invocation = ToolInvocation(
            tool_name=tool_name,
            arguments=arguments,
            output=output,
            duration_seconds=duration,
            status=status
        )
        self.tool_invocations.append(invocation)
        self.scratchpad.append({
            "type": "tool_call",
            "tool": tool_name,
            "arguments": arguments,
            "output": str(output)[:500],  # truncated for scratchpad
            "status": status,
            "timestamp": time.time()
        })

    def get_formatted_context(self) -> str:
        """Serializes current memory state into prompt context for local models."""
        lines = [f"=== OBJECTIVE ===", self.task_objective, "\n=== PLAN ==="]
        for s in self.plan:
            status_icon = "✓" if s.status == "completed" else "→" if s.status == "in_progress" else " "
            obs_suffix = f" [Observation: {s.observation}]" if s.observation else ""
            lines.append(f"[{status_icon}] Step {s.step_number}: {s.description}{obs_suffix}")

        lines.append("\n=== RECENT ACTIONS & OBSERVATIONS ===")
        # Keep recent scratchpad items to fit local context limits
        recent_items = self.scratchpad[-self.max_history_items:]
        for item in recent_items:
            if item["type"] == "thought":
                lines.append(f"Thought: {item['content']}")
            elif item["type"] == "tool_call":
                lines.append(f"Action: {item['tool']}({item['arguments']})")
                lines.append(f"Observation: {item['output']}")

        return "\n".join(lines)
