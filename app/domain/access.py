"""Role, data-group, and employee-scope decisions."""

from __future__ import annotations

import json
from typing import Any

from app.domain.catalog import ALWAYS_AVAILABLE


class Denied(Exception):
    """The actor is not allowed to touch this record."""


class Invalid(Exception):
    """The request is well-formed enough to refuse with a reason."""


def _grant_map(user: Any) -> dict[str, Any]:
    raw = getattr(user, "grants", None) or {}
    if isinstance(raw, str):
        parsed = json.loads(raw or "{}")
        return parsed if isinstance(parsed, dict) else {}
    if isinstance(raw, dict):
        return raw
    return {}


def grant_for(user: Any, group: str) -> dict[str, Any] | None:
    item = _grant_map(user).get(group)
    return item if isinstance(item, dict) else None


def user_can_read(user: Any, group: str, modules: dict[str, bool] | None = None) -> bool:
    if user is None:
        return False
    if modules is not None and group not in ALWAYS_AVAILABLE and not modules.get(group, True):
        return False
    if getattr(user, "is_admin", False):
        return True
    grant = grant_for(user, group)
    return bool(grant and grant.get("read"))


def user_can_write(user: Any, group: str, modules: dict[str, bool] | None = None) -> bool:
    if user is None:
        return False
    if modules is not None and group not in ALWAYS_AVAILABLE and not modules.get(group, True):
        return False
    if getattr(user, "is_admin", False):
        return True
    grant = grant_for(user, group)
    return bool(grant and grant.get("write"))


def _same(left: Any, right: Any) -> bool:
    if left is None or right is None:
        return False
    return int(left) == int(right)


def employee_in_scope(
    user: Any,
    group: str,
    target_employee_id: Any,
    subordinate_ids: set[int],
    *,
    write: bool = False,
    modules: dict[str, bool] | None = None,
) -> bool:
    allowed = (
        user_can_write(user, group, modules) if write else user_can_read(user, group, modules)
    )
    if not allowed:
        return False
    if getattr(user, "is_admin", False):
        return True
    grant = grant_for(user, group) or {}
    scope = str(grant.get("scope") or "self")
    viewer = getattr(user, "employee_id", None)
    if scope == "all":
        return True
    if scope == "self":
        return _same(viewer, target_employee_id)
    if scope == "subordinates":
        if _same(viewer, target_employee_id):
            return True
        try:
            return int(target_employee_id) in {int(item) for item in subordinate_ids}
        except (TypeError, ValueError):
            return False
    return False


def require_scope(
    user: Any,
    group: str,
    target_employee_id: Any,
    subordinate_ids: set[int],
    *,
    write: bool = False,
    modules: dict[str, bool] | None = None,
) -> None:
    if not employee_in_scope(
        user,
        group,
        target_employee_id,
        subordinate_ids,
        write=write,
        modules=modules,
    ):
        raise Denied(f"Not allowed to access {group} for this employee.")
