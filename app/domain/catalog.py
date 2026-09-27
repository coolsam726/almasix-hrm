"""Shared vocabulary for roles, data groups, and workflow rows."""

from __future__ import annotations

DATA_GROUPS: tuple[str, ...] = (
    "admin",
    "pim",
    "leave",
    "time",
    "recruitment",
    "performance",
    "directory",
    "dashboard",
    "buzz",
    "claim",
    "maintenance",
    "onboarding",
    "desk",
    "roster",
    "career",
    "training",
    "surveys",
    "voice",
    "discipline",
    "audit",
    "assets",
    "policies",
    "documents",
    "reports",
    "payroll",
    "assistant",
)

ROLE_ADMIN = "admin"
ROLE_SUPERVISOR = "supervisor"
ROLE_ESS = "ess"

ALWAYS_AVAILABLE = frozenset({"admin", "dashboard"})


def _grant(read: bool, write: bool, scope: str) -> dict[str, object]:
    return {"read": read, "write": write, "scope": scope}


def admin_grants() -> dict[str, dict[str, object]]:
    return {group: _grant(True, True, "all") for group in DATA_GROUPS}


def supervisor_grants() -> dict[str, dict[str, object]]:
    grants = {group: _grant(False, False, "self") for group in DATA_GROUPS}
    for group in ("pim", "leave", "time", "performance", "claim", "voice", "desk"):
        grants[group] = _grant(True, True, "subordinates")
    for group in ("recruitment", "directory", "dashboard", "buzz", "roster", "onboarding"):
        grants[group] = _grant(True, True, "all")
    grants["assistant"] = _grant(True, False, "subordinates")
    grants["payroll"] = _grant(False, False, "self")
    grants["admin"] = _grant(False, False, "self")
    grants["maintenance"] = _grant(False, False, "self")
    return grants


def ess_grants() -> dict[str, dict[str, object]]:
    grants = {group: _grant(False, False, "self") for group in DATA_GROUPS}
    for group in ("pim", "leave", "time", "claim", "buzz", "performance", "voice", "desk"):
        grants[group] = _grant(True, True, "self")
    grants["directory"] = _grant(True, False, "all")
    grants["dashboard"] = _grant(True, False, "self")
    grants["assistant"] = _grant(True, False, "self")
    grants["training"] = _grant(True, False, "self")
    grants["surveys"] = _grant(True, True, "self")
    return grants


# (flow, state, role, action, next_state)
DEFAULT_TRANSITIONS: tuple[tuple[str, str, str, str, str], ...] = (
    ("leave", "pending", ROLE_SUPERVISOR, "approve", "approved"),
    ("leave", "pending", ROLE_SUPERVISOR, "reject", "rejected"),
    ("leave", "pending", ROLE_ADMIN, "approve", "approved"),
    ("leave", "pending", ROLE_ADMIN, "reject", "rejected"),
    ("leave", "pending", ROLE_ESS, "cancel", "cancelled"),
    ("timesheet", "open", ROLE_ESS, "submit", "submitted"),
    ("timesheet", "submitted", ROLE_SUPERVISOR, "approve", "approved"),
    ("timesheet", "submitted", ROLE_SUPERVISOR, "reject", "open"),
    ("timesheet", "submitted", ROLE_ADMIN, "approve", "approved"),
    ("timesheet", "submitted", ROLE_ADMIN, "reject", "open"),
    ("attendance", "open", ROLE_ESS, "request", "pending"),
    ("attendance", "pending", ROLE_SUPERVISOR, "approve", "approved"),
    ("attendance", "pending", ROLE_ADMIN, "approve", "approved"),
    ("recruitment", "applied", ROLE_ADMIN, "shortlist", "shortlisted"),
    ("recruitment", "shortlisted", ROLE_ADMIN, "interview", "interview"),
    ("recruitment", "interview", ROLE_ADMIN, "hire", "hired"),
    ("recruitment", "applied", ROLE_ADMIN, "reject", "rejected"),
    ("recruitment", "shortlisted", ROLE_ADMIN, "reject", "rejected"),
    ("review", "scheduled", ROLE_ESS, "self", "self_reviewed"),
    ("review", "self_reviewed", ROLE_SUPERVISOR, "supervisor", "reviewed"),
    ("review", "reviewed", ROLE_ESS, "signoff", "signed"),
    ("review", "reviewed", ROLE_ADMIN, "signoff", "signed"),
    ("claim", "draft", ROLE_ESS, "submit", "submitted"),
    ("claim", "submitted", ROLE_SUPERVISOR, "approve", "approved"),
    ("claim", "submitted", ROLE_SUPERVISOR, "reject", "rejected"),
    ("claim", "submitted", ROLE_ADMIN, "approve", "approved"),
    ("claim", "submitted", ROLE_ADMIN, "reject", "rejected"),
    ("desk", "open", ROLE_ESS, "submit", "submitted"),
    ("desk", "submitted", ROLE_ADMIN, "resolve", "resolved"),
    ("grievance", "open", ROLE_ESS, "submit", "submitted"),
    ("grievance", "submitted", ROLE_ADMIN, "resolve", "resolved"),
    ("discipline", "open", ROLE_ADMIN, "assign", "investigating"),
    ("discipline", "investigating", ROLE_ADMIN, "close", "closed"),
    ("onboarding", "pending", ROLE_ADMIN, "start", "active"),
    ("onboarding", "active", ROLE_ADMIN, "complete", "completed"),
)
