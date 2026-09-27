"""Home widgets. Live counts are on the JSON API; the shell stays readable without them."""

from __future__ import annotations

from almasix.orbit.widgets.widget import Widget


class WelcomeWidget(Widget):
    sort = 0
    heading = "Almasix HRM"
    description = "People operations"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "welcome")

    def render_body(self, state=None, **ctx) -> str:  # type: ignore[no-untyped-def]
        del state, ctx
        return (
            "<p>Keep the employee record, leave, time, hiring, and reviews in one panel. "
            "What you see depends on your role: everyone, the people who report to you, "
            "or only your own record.</p>"
        )


class HeadcountNote(Widget):
    sort = 1
    heading = "Where to look"
    column_span = "full"

    def __init__(self, name: str | None = None) -> None:
        super().__init__(name or "headcount-note")

    def render_body(self, state=None, **ctx) -> str:  # type: ignore[no-untyped-def]
        del state, ctx
        return (
            "<ul>"
            "<li>PIM — the employee list, for people you are allowed to manage</li>"
            "<li>Contracts — employment start and end for those same people</li>"
            "<li>ESS — your own record: personal details, contacts, job, and qualifications</li>"
            "<li>Leave — entitlements, requests, and the holiday calendar</li>"
            "<li>Time — timesheets and attendance punches</li>"
            "<li>Recruitment — vacancies and candidates</li>"
            "<li>Performance — goals and reviews</li>"
            "<li>Directory, Buzz, and Claim</li>"
            "</ul>"
        )
