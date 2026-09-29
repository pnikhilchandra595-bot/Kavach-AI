"""
Tool Executor and Dispatcher for Sovereign Agentic Core.
Validates parameters, integrates with the ApprovalGate, and standardizes observations.
"""

from typing import Dict, Any, Callable, Optional, List
import time
import inspect
from pydantic import BaseModel, Field
from agent_core.approval_gate import ApprovalGate, ApprovalRequest, ActionRiskLevel
from agent_core.schema_validator import SchemaValidator, SchemaValidationResult


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    risk_level: str = "low"


class ToolResult(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    output: Any
    is_error: bool = False
    duration_seconds: float = 0.0
    approval_required: bool = False
    approval_request: Optional[ApprovalRequest] = None
    validation_error: Optional[str] = None


class ToolExecutor:
    """
    Manages registration, schema validation, authorization, and safe execution of tools.
    """

    def __init__(self, approval_gate: Optional[ApprovalGate] = None, validator: Optional[SchemaValidator] = None):
        self.approval_gate = approval_gate or ApprovalGate(auto_approve_for_testing=True)
        self.validator = validator or SchemaValidator()
        self.tools: Dict[str, Callable] = {}
        self.tool_metadata: Dict[str, ToolDefinition] = {}
        self._register_default_tools()

    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        risk_level: str = "low",
        pydantic_schema: Optional[type[BaseModel]] = None
    ):
        """Registers a Python function as an agent-callable tool with schema validation."""
        self.tools[name] = func
        self.tool_metadata[name] = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters or {},
            risk_level=risk_level
        )
        if pydantic_schema:
            self.validator.register_tool_schema(name, pydantic_schema)
        else:
            self.validator.derive_schema_from_callable(name, func)

    def get_tool_definitions(self) -> List[ToolDefinition]:
        return list(self.tool_metadata.values())

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        Executes a registered tool with approval gate screening and error handling.
        """
        start_time = time.time()

        if tool_name not in self.tools:
            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                output=f"Error: Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}",
                is_error=True,
                duration_seconds=time.time() - start_time
            )

        # 1. Schema Validation Check
        val_result = self.validator.validate(tool_name, arguments)
        if not val_result.is_valid:
            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                output=f"SCHEMA_VALIDATION_ERROR: {val_result.error_message}. Remediation: {val_result.remediation_hint}",
                is_error=True,
                validation_error=val_result.error_message,
                duration_seconds=time.time() - start_time
            )
        valid_args = val_result.validated_args

        # 2. Gate Check
        approved, req = self.approval_gate.check_and_request_approval(tool_name, valid_args)
        if not approved:
            return ToolResult(
                tool_name=tool_name,
                arguments=valid_args,
                output=f"ACTION_PAUSED: High-consequence tool '{tool_name}' requires operator approval [Request ID: {req.request_id}].",
                is_error=False,
                duration_seconds=time.time() - start_time,
                approval_required=True,
                approval_request=req
            )

        # 3. Safe Execution
        try:
            func = self.tools[tool_name]
            output = func(**valid_args)
            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                output=output,
                is_error=False,
                duration_seconds=time.time() - start_time
            )
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                arguments=arguments,
                output=f"Tool Execution Error ({type(e).__name__}): {str(e)}",
                is_error=True,
                duration_seconds=time.time() - start_time
            )

    def _register_default_tools(self):
        """Registers essential starter tools for immediate offline operation."""
        def local_knowledge_search(query: str) -> str:
            # Starter local SOP retrieval simulation
            q = query.lower()
            if "pump" in q or "crude" in q or "vibration" in q:
                return (
                    "[MRPL SOP-MECH-402] Crude Distillation Unit (CDU) Booster Pump Maintenance:\n"
                    "- Vibration threshold: Limit is 4.5 mm/s RMS. Beyond 6.0 mm/s requires immediate shutdown.\n"
                    "- Seal pressure: Must be maintained at minimum 2.1 bar gauge.\n"
                    "- Required approval: Shift in-charge sign-off required on Form MRPL-MNT-12."
                )
            return f"[Local SOP Search] Query '{query}' yielded standard operating guideline for unit inspection."

        def read_scanned_ocr_text(file_path: str) -> str:
            # Starter mock OCR extraction
            return (
                f"[OCR Output for {file_path}]\n"
                "DATE: 12-SEP-2026\n"
                "UNIT: CDU-II P-101B Booster Pump\n"
                "OBSERVED VIBRATION: 6.8 mm/s RMS (CRITICAL - EXCEEDS LIMIT OF 4.5 mm/s)\n"
                "OPERATOR NOTES: Bearing temperature 84 deg C. Noise observed on DE bearing.\n"
                "ACTION REQUIRED: Immediate isolation and draft approval note for replacement."
            )

        def calculate_values(expression: str) -> str:
            try:
                # Safe math eval
                allowed = set("0123456789+-*/(). ")
                if not set(expression).issubset(allowed):
                    return "Error: Expression contains unpermitted characters."
                val = eval(expression, {"__builtins__": None}, {})
                return f"Result: {val}"
            except Exception as e:
                return f"Math Error: {e}"

        def submit_approval_note(subject: str, unit: str, recommendation: str, priority: str = "HIGH") -> str:
            return (
                f"APPROVAL NOTE DRAFTED (Pending Sign-off):\n"
                f"Subject: {subject}\n"
                f"Unit: {unit}\n"
                f"Priority: {priority}\n"
                f"Recommendation: {recommendation}\n"
                f"Reference Form: MRPL-MNT-12"
            )

        self.register_tool(
            "local_knowledge_search",
            local_knowledge_search,
            "Search local MRPL synthetic SOPs and maintenance manuals.",
            parameters={"query": "Search string"},
            risk_level="low"
        )
        self.register_tool(
            "read_scanned_ocr_text",
            read_scanned_ocr_text,
            "Extract structured text from a local scanned document or inspection sheet.",
            parameters={"file_path": "Absolute or relative path to file"},
            risk_level="low"
        )
        self.register_tool(
            "calculate_values",
            calculate_values,
            "Evaluate mathematical expressions accurately.",
            parameters={"expression": "Arithmetic string e.g. '6.8 - 4.5'"},
            risk_level="low"
        )
        self.register_tool(
            "submit_approval_note",
            submit_approval_note,
            "Draft and submit a formal refinery maintenance approval note (High consequence).",
            parameters={"subject": "Note subject", "unit": "Plant unit", "recommendation": "Text", "priority": "Level"},
            risk_level="high"
        )
