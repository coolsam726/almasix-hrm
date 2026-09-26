"""Pages for views that are not a single table."""

from __future__ import annotations

from typing import Any

from almasix.orbit.panels.page import Page

from app.domain.access import user_can_read


class Guard:
    """Navigation check that is not itself a page."""

    data_group = "dashboard"

    @classmethod
    def can_access(cls, user: Any) -> bool:
        return user_can_read(user, cls.data_group)


class OrgChartPage(Guard, Page):
    slug = "org-chart"
    title = "Organization chart"
    navigation_label = "Org chart"
    navigation_group = "People"
    navigation_icon = "heroicon-o-share"
    navigation_sort = 20
    data_group = "pim"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Organization chart</h1>'
            "<p>The reporting tree is built from each employee's supervisor. "
            "GET /api/hrm/org-chart returns the same tree as nested reports.</p></div>"
        )


class LeaveCalendarPage(Guard, Page):
    slug = "leave-calendar"
    title = "Leave calendar"
    navigation_label = "Calendar"
    navigation_group = "Leave"
    navigation_icon = "heroicon-o-calendar"
    navigation_sort = 20
    data_group = "leave"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Leave calendar</h1>'
            "<p>Working days skip weekends configured on the work week and any holiday. "
            "A half day counts as 0.5 and must start and end on the same date.</p></div>"
        )


class DirectoryPage(Guard, Page):
    slug = "directory"
    title = "Directory"
    navigation_label = "Directory"
    navigation_group = "Workplace"
    navigation_icon = "heroicon-o-book-open"
    navigation_sort = 1
    data_group = "directory"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Directory</h1>'
            "<p>Names, jobs, and locations for people who are still employed. "
            "Salary and personal contact details are not on this page.</p></div>"
        )


class BuzzPage(Guard, Page):
    slug = "buzz"
    title = "Buzz"
    navigation_label = "Buzz"
    navigation_group = "Workplace"
    navigation_icon = "heroicon-o-chat-bubble-left-ellipsis"
    navigation_sort = 4
    data_group = "buzz"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Buzz</h1>'
            "<p>Posts, comments, and one like per person. Upcoming work anniversaries "
            "are listed from GET /api/hrm/anniversaries.</p></div>"
        )


class PipelinePage(Guard, Page):
    slug = "pipeline"
    title = "Candidate pipeline"
    navigation_label = "Pipeline"
    navigation_group = "Talent"
    navigation_icon = "heroicon-o-queue-list"
    navigation_sort = 8
    data_group = "recruitment"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Candidate pipeline</h1>'
            "<p>Applied, shortlisted, interview, then hire. Hiring creates an employee "
            "record and keeps the candidate linked to it.</p></div>"
        )


class TimesheetPage(Guard, Page):
    slug = "timesheet"
    title = "Timesheet"
    navigation_label = "My timesheet"
    navigation_group = "Time"
    navigation_icon = "heroicon-o-table-cells"
    navigation_sort = 10
    data_group = "time"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Timesheet</h1>'
            "<p>Add hours to an open timesheet, submit it, then a supervisor approves "
            "or sends it back. Each entry is between 0 and 24 hours.</p></div>"
        )


class RosterPage(Guard, Page):
    slug = "roster"
    title = "Roster"
    navigation_label = "Roster"
    navigation_group = "Advanced"
    navigation_icon = "heroicon-o-calendar-days"
    navigation_sort = 20
    data_group = "roster"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Roster</h1>'
            "<p>A shift can be published only after it has a person, a location, "
            "and an end that is later than its start.</p></div>"
        )


class NineBoxPage(Guard, Page):
    slug = "nine-box"
    title = "9-box"
    navigation_label = "9-box"
    navigation_group = "Advanced"
    navigation_icon = "heroicon-o-squares-2x2"
    navigation_sort = 21
    data_group = "career"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">9-box</h1>'
            "<p>Performance and potential are each scored 1, 2, or 3.</p></div>"
        )


class AssistantPage(Guard, Page):
    slug = "assistant"
    title = "Assistant"
    navigation_label = "Assistant"
    navigation_group = "Advanced"
    navigation_icon = "heroicon-o-sparkles"
    navigation_sort = 30
    data_group = "assistant"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Assistant</h1>'
            "<p>Answers questions about headcount, leave balances, reporting lines, "
            "and payroll summaries you are allowed to see. It does not change records.</p></div>"
        )
