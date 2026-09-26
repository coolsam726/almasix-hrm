"""Timesheet hours and attendance punch order."""

from __future__ import annotations

from decimal import Decimal


def validate_hours(hours: Decimal) -> Decimal:
    if hours < 0 or hours > Decimal(24):
        raise ValueError("Hours must be between 0 and 24.")
    return hours


def next_punch(existing_kinds: list[str], kind: str) -> str:
    """Punches alternate in, out, in, out. The first punch of a day is in."""
    if kind not in {"in", "out"}:
        raise ValueError("Punch kind must be in or out.")
    expected = "in" if len(existing_kinds) % 2 == 0 else "out"
    if kind != expected:
        raise ValueError(f"Expected an '{expected}' punch.")
    return kind
