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
            "<li>People — employee profiles, contacts, and custom fields</li>"
            "<li>Leave — entitlements, requests, and the holiday calendar</li>"
            "<li>Time — timesheets and attendance punches</li>"
            "<li>Talent — vacancies, candidates, and reviews</li>"
            "<li>Workplace — directory, posts, and claims</li>"
            "</ul>"
        )
