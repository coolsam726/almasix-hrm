"""Pages for views that are not a single table."""

from __future__ import annotations

from typing import Any

from almasix.orbit.panels.page import Page

from app.domain.access import grant_for, user_can_read


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
    navigation_group = "PIM"
    navigation_subgroup = ""
    navigation_icon = "heroicon-o-share"
    navigation_sort = 20
    data_group = "pim"

    @classmethod
    def can_access(cls, user: Any) -> bool:
        if not user_can_read(user, cls.data_group):
            return False
        if getattr(user, "is_admin", False):
            return True
        scope = str((grant_for(user, cls.data_group) or {}).get("scope") or "self")
        return scope in {"subordinates", "all"}

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Organization chart</h1>'
            "<p>The reporting tree is built from each employee's supervisor. "
            "GET /api/hrm/org-chart returns the same tree as nested reports.</p></div>"
        )


class MaintenancePage(Guard, Page):
    slug = "maintenance"
    title = "Purge records"
    navigation_label = "Purge records"
    navigation_group = "Maintenance"
    navigation_icon = "heroicon-o-trash"
    navigation_sort = 1
    data_group = "maintenance"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        return (
            '<div class="or-page"><h1 class="or-page-title">Purge records</h1>'
            "<p>An administrator can purge an employee who has no one reporting to them. "
            "That removes the person and the rows that belong to them.</p></div>"
        )


class LeaveCalendarPage(Guard, Page):
    slug = "leave-calendar"
    title = "Leave calendar"
    navigation_label = "Calendar"
    navigation_group = "Leave"
    navigation_subgroup = "Requests"
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


class MyInfoPage(Guard, Page):
    """ESS entry. OrangeHRM labels this side module My Info."""

    slug = "my-info"
    title = "My Info"
    navigation_label = "Personal details"
    navigation_group = "My Info"
    navigation_subgroup = "Personal"
    navigation_icon = "heroicon-o-user"
    navigation_sort = 1
    data_group = "pim"

    @classmethod
    def render(cls, **ctx: Any) -> str:
        del ctx
        from almasix.orbit.panels.pages.resource_pages import _auth_user

        user = _auth_user()
        employee_id = getattr(user, "employee_id", None) if user is not None else None
        if not employee_id:
            return (
                '<div class="or-page"><h1 class="or-page-title">My Info</h1>'
                "<p>This account is not linked to an employee record.</p></div>"
            )
        return (
            '<div class="or-page"><h1 class="or-page-title">My Info</h1>'
            "<p>This is your own employee record. Contacts, dependents, and "
            "immigration for you are in the menu beside this page.</p>"
            f'<p><a href="/employees/{employee_id}">Open your record</a></p></div>'
        )


class DirectoryPage(Guard, Page):
    slug = "directory"
    title = "Directory"
    navigation_label = "Directory"
    navigation_group = "Directory"
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
    navigation_group = "Buzz"
    navigation_subgroup = ""
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
    navigation_group = "Recruitment"
    navigation_subgroup = ""
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
    navigation_subgroup = "Attendance"
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
    navigation_subgroup = "Roster"
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
    navigation_subgroup = "Career"
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
    navigation_subgroup = "Company"
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
