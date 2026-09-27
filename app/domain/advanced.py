"""Rules for modules that sit on top of the workflow engine."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlparse


def can_publish_shift(
    *,
    employee_id: Any,
    location_id: Any,
    starts_at: str,
    ends_at: str,
) -> bool:
    if employee_id is None or location_id is None:
        return False
    start = datetime.fromisoformat(starts_at)
    end = datetime.fromisoformat(ends_at)
    return end > start


def nine_box_cell(performance: int, potential: int) -> tuple[int, int]:
    if performance not in {1, 2, 3} or potential not in {1, 2, 3}:
        raise ValueError("Performance and potential must be 1, 2, or 3.")
    return performance, potential


def certificate_code(course_id: int, employee_id: int) -> str:
    return f"HRM-{course_id}-{employee_id}"


def payroll_export(rows: list[dict[str, Any]], *, include_salary: bool) -> list[dict[str, Any]]:
    exported = []
    for row in rows:
        item = {"employee_number": row["employee_number"], "name": row["name"]}
        if include_salary:
            item["amount"] = row.get("amount")
        exported.append(item)
    return exported


def valid_connector_endpoint(endpoint: str) -> str:
    parsed = urlparse(endpoint)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("A payroll connector endpoint must be an https URL.")
    return endpoint


def valid_cadence(cadence: str) -> str:
    if cadence not in {"daily", "weekly", "monthly"}:
        raise ValueError("Cadence must be daily, weekly, or monthly.")
    return cadence
