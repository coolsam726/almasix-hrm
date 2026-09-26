"""Org tree, employee numbers, directory projection, anniversaries, CSV."""

from __future__ import annotations

import csv
from datetime import date, timedelta
from io import StringIO
from typing import Any


def subordinate_set(pairs: list[tuple[int, int | None]], root_id: int) -> set[int]:
    children: dict[int, list[int]] = {}
    for employee_id, supervisor_id in pairs:
        if supervisor_id is not None:
            children.setdefault(int(supervisor_id), []).append(int(employee_id))
    seen: set[int] = set()
    stack = list(children.get(int(root_id), []))
    while stack:
        current = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        stack.extend(children.get(current, []))
    return seen


def next_employee_number(existing: list[str]) -> str:
    numbers = [int(value) for value in existing if str(value).isdigit()]
    return f"{(max(numbers) if numbers else 0) + 1:04d}"


def org_tree(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Supervisor tree. Each node is {id, name, reports: [...]}."""
    nodes = {
        int(row["id"]): {
            "id": int(row["id"]),
            "name": row["name"],
            "reports": [],
        }
        for row in rows
    }
    roots: list[dict[str, Any]] = []
    for row in rows:
        node = nodes[int(row["id"])]
        supervisor = row.get("supervisor_id")
        if supervisor is None or int(supervisor) not in nodes:
            roots.append(node)
        else:
            nodes[int(supervisor)]["reports"].append(node)
    return roots


def directory_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Public directory fields. Salary and contact details stay off this list."""
    visible = []
    for row in rows:
        if row.get("terminated_on"):
            continue
        visible.append(
            {
                "id": row["id"],
                "name": row["name"],
                "job_title": row.get("job_title") or "",
                "location": row.get("location") or "",
            }
        )
    return visible


def upcoming_anniversaries(
    rows: list[dict[str, Any]],
    today: date,
    *,
    within_days: int = 30,
) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    horizon = today + timedelta(days=within_days)
    for row in rows:
        if row.get("terminated_on") or not row.get("joined_on"):
            continue
        joined = row["joined_on"]
        if not isinstance(joined, date):
            joined = date.fromisoformat(str(joined)[:10])
        anniversary = _anniversary_on_or_after(joined, today)
        if today <= anniversary <= horizon:
            found.append({"id": row["id"], "name": row["name"], "on": anniversary.isoformat()})
    return found


def _anniversary_on_or_after(joined: date, today: date) -> date:
    year = today.year
    anniversary = _safe_anniversary(joined, year)
    if anniversary < today:
        anniversary = _safe_anniversary(joined, year + 1)
    return anniversary


def _safe_anniversary(joined: date, year: int) -> date:
    try:
        return joined.replace(year=year)
    except ValueError:
        return date(year, 2, 28)


def parse_employee_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(StringIO(text))
    required = {"first_name", "last_name", "email", "employee_number"}
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise ValueError("CSV must include first_name, last_name, email, employee_number.")
    rows = []
    for raw in reader:
        email = (raw.get("email") or "").strip()
        if not email:
            continue
        rows.append(
            {
                "first_name": (raw.get("first_name") or "").strip(),
                "last_name": (raw.get("last_name") or "").strip(),
                "email": email,
                "employee_number": (raw.get("employee_number") or "").strip(),
            }
        )
    return rows


def dashboard_snapshot(
    *,
    headcount: int,
    pending_leave: int,
    open_vacancies: int,
) -> dict[str, int]:
    return {
        "headcount": headcount,
        "pending_leave": pending_leave,
        "open_vacancies": open_vacancies,
    }
