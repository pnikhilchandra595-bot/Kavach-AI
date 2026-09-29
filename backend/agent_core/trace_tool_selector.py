"""
Retrieval-Augmented Tool Selector for Sovereign Workbench.
Uses historical audit-log traces to recommend proven tool sequences for incoming tasks.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import re


class TaskExecutionTrace(BaseModel):
    trace_id: str
    task_category: str
    objective_pattern: str
    keywords: List[str]
    proven_tool_sequence: List[str]
    success_rate: float = 1.0
    average_iterations: int = 4


class TraceToolSelector:
    """
    Indexes past successful audit log traces and retrieves the most relevant
    tool execution sequence to prime the ReAct planner with few-shot guidance.
    """

    def __init__(self):
        self._historical_traces: List[TaskExecutionTrace] = []
        self._seed_default_traces()

    def _seed_default_traces(self):
        self._historical_traces.extend([
            TaskExecutionTrace(
                trace_id="trace-mech-001",
                task_category="equipment_maintenance",
                objective_pattern="vibration threshold check and maintenance note",
                keywords=["vibration", "pump", "sop", "maintenance", "threshold", "cdu"],
                proven_tool_sequence=[
                    "read_scanned_ocr_text",
                    "local_knowledge_search",
                    "calculate_values",
                    "submit_approval_note"
                ],
                success_rate=0.98,
                average_iterations=4
            ),
            TaskExecutionTrace(
                trace_id="trace-code-002",
                task_category="code_sandboxing",
                objective_pattern="python script calculation in sandbox",
                keywords=["python", "script", "code", "sandbox", "algorithm"],
                proven_tool_sequence=[
                    "local_knowledge_search",
                    "execute_sandboxed_code"
                ],
                success_rate=0.95,
                average_iterations=2
            ),
            TaskExecutionTrace(
                trace_id="trace-vision-003",
                task_category="pid_inspection",
                objective_pattern="p&id schematic line tracing",
                keywords=["p&id", "diagram", "schematic", "drawing", "valve"],
                proven_tool_sequence=[
                    "inspect_pid_diagram",
                    "local_knowledge_search"
                ],
                success_rate=0.92,
                average_iterations=3
            ),
        ])

    def register_trace(self, trace: TaskExecutionTrace):
        self._historical_traces.append(trace)

    def retrieve_exemplar_trace(self, objective: str) -> Optional[TaskExecutionTrace]:
        """Finds the best matching historical trace based on keyword overlap."""
        tokens = set(re.findall(r"\b[a-z0-9_#&.-]+\b", objective.lower()))
        best_trace = None
        highest_overlap = 0

        for trace in self._historical_traces:
            overlap = len(tokens.intersection(set(trace.keywords)))
            if overlap > highest_overlap:
                highest_overlap = overlap
                best_trace = trace

        return best_trace if highest_overlap > 0 else None

    def recommend_tool_plan(self, objective: str) -> List[str]:
        """Returns the recommended sequence of tools or empty list if no match."""
        trace = self.retrieve_exemplar_trace(objective)
        return trace.proven_tool_sequence if trace else []
