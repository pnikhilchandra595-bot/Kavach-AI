"""
Role-Based Access Control (RBAC) Engine for Sovereign Workbench.
Defines roles (Operator, Engineer, Supervisor), permissions, and gate authorization.
"""

from enum import Enum
from typing import Dict, List, Set, Optional
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    OPERATOR = "operator"
    ENGINEER = "engineer"
    SUPERVISOR = "supervisor"


class Permission(str, Enum):
    READ_DATA = "read_data"
    SEARCH_SOP = "search_sop"
    TRIGGER_AGENT = "trigger_agent"
    EXECUTE_SANDBOX = "execute_sandbox"
    DRAFT_DELIVERABLE = "draft_deliverable"
    APPROVE_STANDARD_ACTION = "approve_standard_action"
    APPROVE_SAFETY_CRITICAL = "approve_safety_critical"


class UserProfile(BaseModel):
    username: str
    role: UserRole
    department: str = "Refinery Operations"
    full_name: Optional[str] = None


class RBACManager:
    """
    Evaluates role permissions and enforces access policies across the workbench.
    """

    ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
        UserRole.OPERATOR: {
            Permission.READ_DATA,
            Permission.SEARCH_SOP,
            Permission.TRIGGER_AGENT,
            Permission.DRAFT_DELIVERABLE,
        },
        UserRole.ENGINEER: {
            Permission.READ_DATA,
            Permission.SEARCH_SOP,
            Permission.TRIGGER_AGENT,
            Permission.EXECUTE_SANDBOX,
            Permission.DRAFT_DELIVERABLE,
        },
        UserRole.SUPERVISOR: {
            Permission.READ_DATA,
            Permission.SEARCH_SOP,
            Permission.TRIGGER_AGENT,
            Permission.EXECUTE_SANDBOX,
            Permission.DRAFT_DELIVERABLE,
            Permission.APPROVE_STANDARD_ACTION,
            Permission.APPROVE_SAFETY_CRITICAL,
        },
    }

    def __init__(self):
        self._users: Dict[str, UserProfile] = {}
        self._register_default_users()

    def _register_default_users(self):
        self.register_user(UserProfile(username="op_rajesh", role=UserRole.OPERATOR, full_name="Rajesh Kumar (Field Operator)"))
        self.register_user(UserProfile(username="eng_priya", role=UserRole.ENGINEER, full_name="Priya Sharma (Reliability Engineer)"))
        self.register_user(UserProfile(username="sup_anand", role=UserRole.SUPERVISOR, full_name="Anand Rao (Shift Supervisor)"))
        self.register_user(UserProfile(username="sup_mehta", role=UserRole.SUPERVISOR, full_name="Deepak Mehta (Plant Safety In-Charge)"))

    def register_user(self, user: UserProfile):
        self._users[user.username] = user

    def get_user(self, username: str) -> Optional[UserProfile]:
        return self._users.get(username)

    def has_permission(self, username: str, permission: Permission) -> bool:
        user = self.get_user(username)
        if not user:
            return False
        perms = self.ROLE_PERMISSIONS.get(user.role, set())
        return permission in perms

    def can_approve_action(self, username: str, is_safety_critical: bool = False) -> bool:
        req_perm = Permission.APPROVE_SAFETY_CRITICAL if is_safety_critical else Permission.APPROVE_STANDARD_ACTION
        return self.has_permission(username, req_perm)
