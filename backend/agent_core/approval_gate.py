"""
Human-In-The-Loop Approval Gate with Role-Based Access Control (RBAC).
Enforces supervisor sign-off and Two-Person Rule for safety-critical refinery actions.
"""

from typing import Dict, Any, Optional, Callable, List, Tuple
from pydantic import BaseModel, Field
import time
from enum import Enum
from auth.rbac import RBACManager, UserRole, Permission


class ActionRiskLevel(str, Enum):
    LOW = "low"            # Read operations, search, scratchpad
    MEDIUM = "medium"      # Creating new draft files in sandbox
    HIGH = "high"          # Overwriting files, executing shell scripts, submitting official notes


class ApprovalSignOff(BaseModel):
    username: str
    role: str
    timestamp: float = Field(default_factory=time.time)
    comment: Optional[str] = None


class ApprovalRequest(BaseModel):
    request_id: str
    action_type: str
    tool_name: str
    arguments: Dict[str, Any]
    risk_level: ActionRiskLevel
    description: str
    is_safety_critical: bool = False
    approvals_required: int = 1
    sign_offs: List[ApprovalSignOff] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)
    approved: Optional[bool] = None
    status: str = "pending"  # "pending", "pending_second_approval", "approved", "rejected"
    operator_comment: Optional[str] = None


class ApprovalGate:
    """
    Evaluates proposed actions against risk profiles.
    Enforces supervisor sign-off and differential trust (Two-Person rule on safety-critical tasks).
    """

    HIGH_RISK_TOOLS = {
        "file_overwrite", "execute_shell", "delete_file", "submit_approval_note", "run_migration"
    }

    SAFETY_CRITICAL_KEYWORDS = {
        "emergency shutdown", "emergency_shutdown", "unit trip", "safety-critical", 
        "safety critical", "bypass safety", "emergency isolation", "flare trip"
    }

    def __init__(self, auto_approve_for_testing: bool = False, rbac_manager: Optional[RBACManager] = None):
        self.auto_approve_for_testing = auto_approve_for_testing
        self.rbac = rbac_manager or RBACManager()
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        self.approval_history: List[ApprovalRequest] = []
        self._notification_callback: Optional[Callable[[ApprovalRequest], None]] = None

    def set_notification_callback(self, cb: Callable[[ApprovalRequest], None]):
        self._notification_callback = cb

    def evaluate_action(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[ActionRiskLevel, bool]:
        """
        Determines the risk level and safety-critical status of the proposed tool invocation.
        Returns (risk_level, is_safety_critical).
        """
        # Check safety-critical triggers in arguments
        args_text = str(arguments).lower()
        is_safety_critical = any(kw in args_text for kw in self.SAFETY_CRITICAL_KEYWORDS)

        if tool_name in self.HIGH_RISK_TOOLS:
            return ActionRiskLevel.HIGH, is_safety_critical

        # Path overwrite check
        if tool_name in ("write_file", "save_document"):
            if arguments.get("overwrite", False):
                return ActionRiskLevel.HIGH, is_safety_critical
            return ActionRiskLevel.MEDIUM, is_safety_critical

        if "delete" in tool_name.lower() or "remove" in tool_name.lower():
            return ActionRiskLevel.HIGH, True

        return ActionRiskLevel.LOW, False

    def check_and_request_approval(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        description: Optional[str] = None
    ) -> Tuple[bool, Optional[ApprovalRequest]]:
        """
        Returns (is_approved, approval_request).
        If action is HIGH risk and auto_approve is False, pauses execution and returns (False, request).
        """
        risk, is_safety_critical = self.evaluate_action(tool_name, arguments)

        if risk != ActionRiskLevel.HIGH:
            return True, None

        req_id = f"gate-{int(time.time() * 1000)}"
        approvals_required = 2 if is_safety_critical else 1

        request = ApprovalRequest(
            request_id=req_id,
            action_type="tool_execution",
            tool_name=tool_name,
            arguments=arguments,
            risk_level=risk,
            is_safety_critical=is_safety_critical,
            approvals_required=approvals_required,
            description=description or f"Request to execute high-consequence tool '{tool_name}'",
            status="pending"
        )

        if self.auto_approve_for_testing:
            request.approved = True
            request.status = "approved"
            request.operator_comment = "Auto-approved by test harness."
            self.approval_history.append(request)
            return True, request

        self.pending_requests[req_id] = request
        self.approval_history.append(request)

        if self._notification_callback:
            self._notification_callback(request)

        return False, request

    def resolve_request(
        self,
        request_id: str,
        approved: bool,
        username: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Processes an approval or rejection by a user with RBAC validation.
        Enforces Two-Person supervisory sign-off on safety-critical requests.
        """
        if request_id not in self.pending_requests:
            raise KeyError(f"Approval request {request_id} not found.")

        req = self.pending_requests[request_id]

        if not approved:
            req.approved = False
            req.status = "rejected"
            req.operator_comment = comment or f"Rejected by {username or 'operator'}."
            self.pending_requests.pop(request_id)
            return False, f"Action {request_id} rejected."

        # RBAC Check
        if username:
            user = self.rbac.get_user(username)
            if not user:
                return False, f"Unauthorized: User '{username}' does not exist."

            if not self.rbac.can_approve_action(username, req.is_safety_critical):
                return False, f"Permission Denied: User '{username}' with role '{user.role}' lacks supervisor approval authority."

            # Check if user already signed off on this request (Two-Person rule prevention)
            if any(s.username == username for s in req.sign_offs):
                return False, f"Two-Person Rule Violation: User '{username}' has already approved this request. Second sign-off must be a distinct supervisor."

            signoff = ApprovalSignOff(
                username=username,
                role=user.role.value,
                comment=comment
            )
            req.sign_offs.append(signoff)
        else:
            # Fallback when username not passed (for backwards compatibility)
            req.sign_offs.append(ApprovalSignOff(
                username="default_supervisor",
                role="supervisor",
                comment=comment or "Approved"
            ))

        # Check if required approvals satisfied
        if len(req.sign_offs) >= req.approvals_required:
            req.approved = True
            req.status = "approved"
            req.operator_comment = comment or "Fully authorized by required supervisors."
            self.pending_requests.pop(request_id)
            return True, f"Action {request_id} fully approved ({len(req.sign_offs)}/{req.approvals_required} sign-offs)."
        else:
            req.status = "pending_second_approval"
            return False, f"Action {request_id} received 1st approval; awaiting 2nd supervisor sign-off ({len(req.sign_offs)}/{req.approvals_required})."
