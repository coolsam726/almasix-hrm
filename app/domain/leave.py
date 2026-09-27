"""Working-day leave math. Holidays and non-working weekdays are excluded."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

WEEKDAYS = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

PARTIALS = frozenset({"full", "half", "half_morning", "half_afternoon"})


def as_date(value: Any) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def count_leave_days(
    start: date,
    end: date,
    work_week: dict[str, bool],
    holidays: set[date],
    *,
    partial: str = "full",
) -> Decimal:
    if partial not in PARTIALS:
        raise ValueError(f"Unknown partial duration {partial!r}.")
    if end < start:
        raise ValueError("The end date is before the start date.")
    if partial != "full" and start != end:
        raise ValueError("A partial day must start and end on the same date.")
    total = Decimal("0")
    cursor = start
    while cursor <= end:
        working = bool(work_week.get(WEEKDAYS[cursor.weekday()], True))
        if working and cursor not in holidays:
            total += Decimal("0.5") if partial != "full" else Decimal("1")
        cursor += timedelta(days=1)
    return total


def summarize(entitled: Decimal, requests: list[tuple[str, Decimal]]) -> tuple[Decimal, Decimal, Decimal]:
    """Return used, pending, remaining from (state, days) pairs."""
    used = sum((days for state, days in requests if state == "approved"), Decimal("0"))
    pending = sum((days for state, days in requests if state == "pending"), Decimal("0"))
    return used, pending, entitled - used - pending
