"""A bounded assistant. It answers from data the caller already loaded.

It does not change records, and it will not discuss payroll unless the actor
can read that data group.
"""

from __future__ import annotations

from typing import Any

from app.domain.access import user_can_read

WRITE_WORDS = (
    "delete",
    "purge",
    "approve",
    "reject",
    "change ",
    "update ",
    "email everyone",
)


class AssistantReply:
    def __init__(self, text: str, *, refused: bool) -> None:
        self.text = text
        self.refused = refused

    def as_dict(self) -> dict[str, Any]:
        return {"text": self.text, "refused": self.refused}


def answer(question: str, user: Any, context: dict[str, Any]) -> AssistantReply:
    folded = " ".join(question.lower().split())
    if not folded:
        return AssistantReply("Ask a question about people, leave, or reporting lines.", refused=True)
    if any(word in folded for word in WRITE_WORDS):
        return AssistantReply(
            "The assistant only answers questions. It does not change records.",
            refused=True,
        )
    if "salary" in folded or "payroll" in folded:
        if not user_can_read(user, "payroll"):
            return AssistantReply("You cannot read payroll data.", refused=True)
        summary = context.get("payroll_summary") or "No payroll summary is loaded."
        return AssistantReply(str(summary), refused=False)
    if "leave" in folded:
        if not user_can_read(user, "leave"):
            return AssistantReply("You cannot read leave data.", refused=True)
        balance = context.get("leave_balance")
        if balance is None:
            return AssistantReply("No leave balance is loaded for that employee.", refused=False)
        return AssistantReply(f"Remaining leave days: {balance}.", refused=False)
    if "report" in folded or "manager" in folded:
        if not user_can_read(user, "pim"):
            return AssistantReply("You cannot read employee records.", refused=True)
        line = context.get("reports_to") or "No reporting line is loaded."
        return AssistantReply(str(line), refused=False)
    if "headcount" in folded or "how many" in folded:
        if not user_can_read(user, "dashboard"):
            return AssistantReply("You cannot read the dashboard.", refused=True)
        count = context.get("headcount")
        return AssistantReply(f"Active headcount: {count}.", refused=False)
    return AssistantReply(
        "I can answer headcount, leave balances, reporting lines, and payroll "
        "summaries you are allowed to see.",
        refused=False,
    )
