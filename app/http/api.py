"""JSON API for the same actions the panel records go through."""

from __future__ import annotations

from typing import Any

from almasix.auth import auth
from almasix.http import json

from app.domain.access import Denied, Invalid
from app.domain.operations import (
    act,
    anniversaries,
    apply_leave,
    ask_assistant,
    dashboard,
    directory,
    organization_chart,
)
from app.domain.workflow import IllegalTransition
from app.models.hrm import LeaveRequest


def _error(exc: Exception) -> Any:
    status = 403 if isinstance(exc, Denied) else 422
    return json({"ok": False, "error": str(exc)}, status=status)


def _user() -> Any:
    return auth().user()


async def health(_request: Any = None) -> Any:
    return json({"ok": True, "service": "almasix-hrm"})


async def dashboard_route(_request: Any = None) -> Any:
    user = _user()
    if user is None:
        return json({"ok": False, "error": "unauthenticated"}, status=401)
    return json({"ok": True, **await dashboard()})


async def directory_route(_request: Any = None) -> Any:
    user = _user()
    if user is None:
        return json({"ok": False, "error": "unauthenticated"}, status=401)
    return json({"ok": True, "employees": await directory()})


async def org_chart_route(_request: Any = None) -> Any:
    user = _user()
    if user is None:
        return json({"ok": False, "error": "unauthenticated"}, status=401)
    return json({"ok": True, "tree": await organization_chart()})


async def leave_apply(request: Any) -> Any:
    user = _user()
    if user is None:
        return json({"ok": False, "error": "unauthenticated"}, status=401)
    body = request.json() or {}
    try:
        record = await apply_leave(
            user,
            int(body["employee_id"]),
            int(body["leave_type_id"]),
            body["starts_on"],
            body["ends_on"],
            partial=str(body.get("partial") or "full"),
            comment=str(body.get("comment") or ""),
        )
    except (Denied, Invalid, IllegalTransition, KeyError, ValueError) as exc:
        return _error(exc if not isinstance(exc, (KeyError, ValueError)) else Invalid(str(exc)))
    return json({"ok": True, "id": record.id, "days": str(record.days), "state": record.state})


async def leave_act(request: Any, leave_id: str) -> Any:
    user = _user()
    if user is None:
        return json({"ok": False, "error": "unauthenticated"}, status=401)
    record = await LeaveRequest.find(leave_id)
    if record is None:
        return json({"ok": False, "error": "not found"}, status=404)
    body = request.json() or {}
    try:
        updated = await act(
            user,
            record,
            flow="leave",
            action=str(body.get("action") or ""),
            group="leave",
            employee_id=record.employee_id,
        )
    except (Denied, Invalid, IllegalTransition) as exc:
        return _error(exc)
    return json({"ok": True, "state": updated.state})


async def assistant_route(request: Any) -> Any:
    user = _user()
    if user is None:
        return json({"ok": False, "error": "unauthenticated"}, status=401)
    body = request.json() or {}
    leave_type = body.get("leave_type_id")
    try:
        reply = await ask_assistant(
            user,
            str(body.get("question") or ""),
            leave_type_id=int(leave_type) if leave_type else None,
        )
    except (Denied, Invalid) as exc:
        return _error(exc)
    return json({"ok": True, **reply.as_dict()})


async def anniversaries_route(_request: Any = None) -> Any:
    user = _user()
    if user is None:
        return json({"ok": False, "error": "unauthenticated"}, status=401)
    return json({"ok": True, "anniversaries": await anniversaries()})
