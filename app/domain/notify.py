"""In-app and mail notice sent when a workflow moves."""

from __future__ import annotations

from typing import Any

from almasix.notifications import MailMessage, Notification


class WorkflowNotification(Notification):
    def __init__(self, message: str) -> None:
        self.message = message

    def via(self, notifiable: Any) -> list[str]:
        return ["database", "mail"]

    def to_database(self, notifiable: Any) -> dict[str, str]:
        del notifiable
        return {"message": self.message}

    def to_mail(self, notifiable: Any) -> MailMessage:
        del notifiable
        return MailMessage().subject("HR update").line(self.message)
