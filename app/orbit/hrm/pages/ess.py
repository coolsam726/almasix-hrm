"""Employee self service. These screens belong to one person, not a shared table."""

from __future__ import annotations

from html import escape
from typing import Any

from almasix.orbit.panels.page import Page

from app.domain.access import employee_in_scope
from app.models.hrm import (
    Dependent,
    EmergencyContact,
    Employee,
    EmployeeContact,
    EmployeeSalary,
    EmployeeSkill,
    EmploymentStatus,
    ImmigrationRecord,
    JobTitle,
    Skill,
)
from app.orbit.hrm.pages.places import Guard


def _text(value: Any) -> str:
    if value is None or value == "":
        return "Not set"
    return escape(str(value))


def _page(title: str, intro: str, body: str) -> str:
    return (
        f'<div class="or-page"><h1 class="or-page-title">{escape(title)}</h1>'
        f"<p>{escape(intro)}</p>{body}</div>"
    )


def _pairs(rows: list[tuple[str, Any]]) -> str:
    items = "".join(f"<dt>{escape(label)}</dt><dd>{_text(value)}</dd>" for label, value in rows)
    return f'<dl class="or-infolist">{items}</dl>'


def _table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        return "<p>Nothing is on file for this section.</p>"
    head = "".join(f"<th>{escape(name)}</th>" for name in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_text(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return f'<table class="or-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def _unlinked(title: str) -> str:
    return _page(title, "Employee self service is your own record.", "<p>This account is not linked to an employee.</p>")


async def _self(user: Any) -> Any:
    employee_id = getattr(user, "employee_id", None) if user is not None else None
    if not employee_id:
        return None
    return await Employee.find(employee_id)


async def _owned(model: type[Any], employee_id: Any) -> list[Any]:
    return list(await model.where("employee_id", employee_id).get())


async def _names(model: type[Any]) -> dict[Any, str]:
    return {row.id: str(row.name) for row in await model.all()}


class EssPage(Guard, Page):
    """A section of the signed-in employee's record."""

    navigation_group = "ESS"
    data_group = "pim"


class MyInfoPage(EssPage):
    slug = "my-info"
    title = "My Info"
    navigation_label = "Personal details"
    navigation_subgroup = "Personal"
    navigation_icon = "heroicon-o-user"
    navigation_sort = 1

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("My Info")
        return _page(
            "My Info",
            "Employee self service. This is your record, not the employee list.",
            _pairs(
                [
                    ("Employee number", person.employee_number),
                    ("Name", person.full_name),
                    ("Email", person.email),
                    ("Joined", person.joined_on),
                ]
            ),
        )


class ContactDetailsPage(EssPage):
    slug = "contact-details"
    title = "Contact details"
    navigation_label = "Contact details"
    navigation_subgroup = "Personal"
    navigation_icon = "heroicon-o-phone"
    navigation_sort = 2

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Contact details")
        rows = [
            [row.street, row.city, row.mobile, row.work_email]
            for row in await _owned(EmployeeContact, person.id)
        ]
        return _page(
            "Contact details",
            "Addresses and phone numbers on your employee record.",
            _table(["Street", "City", "Mobile", "Work email"], rows),
        )


class EmergencyContactsPage(EssPage):
    slug = "emergency-contacts"
    title = "Emergency contacts"
    navigation_label = "Emergency contacts"
    navigation_subgroup = "Personal"
    navigation_icon = "heroicon-o-heart"
    navigation_sort = 3

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Emergency contacts")
        rows = [
            [row.name, row.relationship, row.phone]
            for row in await _owned(EmergencyContact, person.id)
        ]
        return _page(
            "Emergency contacts",
            "People to call for you.",
            _table(["Name", "Relationship", "Phone"], rows),
        )


class DependentsPage(EssPage):
    slug = "dependents"
    title = "Dependents"
    navigation_label = "Dependents"
    navigation_subgroup = "Personal"
    navigation_icon = "heroicon-o-users"
    navigation_sort = 4

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Dependents")
        rows = [
            [row.name, row.relationship, row.date_of_birth]
            for row in await _owned(Dependent, person.id)
        ]
        return _page(
            "Dependents",
            "People who depend on you.",
            _table(["Name", "Relationship", "Date of birth"], rows),
        )


class ImmigrationPage(EssPage):
    slug = "immigration"
    title = "Immigration"
    navigation_label = "Immigration"
    navigation_subgroup = "Personal"
    navigation_icon = "heroicon-o-identification"
    navigation_sort = 5

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Immigration")
        rows = [
            [row.document_type, row.number, row.expires_on]
            for row in await _owned(ImmigrationRecord, person.id)
        ]
        return _page(
            "Immigration",
            "Passports and visas on your record.",
            _table(["Document", "Number", "Expires"], rows),
        )


class JobPage(EssPage):
    slug = "my-job"
    title = "Job"
    navigation_label = "Job"
    navigation_subgroup = "Job"
    navigation_icon = "heroicon-o-briefcase"
    navigation_sort = 10

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Job")
        titles = await _names(JobTitle)
        statuses = await _names(EmploymentStatus)
        supervisor = await Employee.find(person.supervisor_id) if person.supervisor_id else None
        end = person.terminated_on or "Open"
        return _page(
            "Job",
            "Your job and the contract attached to it. You can read this screen. HR changes the contract.",
            _pairs(
                [
                    ("Job title", titles.get(person.job_title_id)),
                    ("Employment status", statuses.get(person.employment_status_id)),
                    ("Reports to", supervisor.full_name if supervisor else None),
                    ("Contract start", person.joined_on),
                    ("Contract end", end),
                ]
            ),
        )


class SalaryPage(EssPage):
    slug = "my-salary"
    title = "Salary"
    navigation_label = "Salary"
    navigation_subgroup = "Job"
    navigation_icon = "heroicon-o-banknotes"
    navigation_sort = 11
    data_group = "payroll"

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Salary")
        rows = [
            [row.amount, row.currency] for row in await _owned(EmployeeSalary, person.id)
        ]
        return _page(
            "Salary",
            "Pay assigned to your employee record.",
            _table(["Amount", "Currency"], rows),
        )


class ReportToPage(EssPage):
    slug = "report-to"
    title = "Report-to"
    navigation_label = "Report-to"
    navigation_subgroup = "Job"
    navigation_icon = "heroicon-o-share"
    navigation_sort = 12

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Report-to")
        supervisor = await Employee.find(person.supervisor_id) if person.supervisor_id else None
        reports = [
            row.full_name
            for row in await Employee.all()
            if row.supervisor_id and int(row.supervisor_id) == int(person.id)
        ]
        body = _pairs([("Supervisor", supervisor.full_name if supervisor else None)])
        body += "<h2>Direct reports</h2>"
        if reports:
            body += "<ul>" + "".join(f"<li>{escape(name)}</li>" for name in reports) + "</ul>"
        else:
            body += "<p>You have no direct reports.</p>"
        return _page("Report-to", "Who you report to, and who reports to you.", body)


class QualificationsPage(EssPage):
    slug = "qualifications"
    title = "Qualifications"
    navigation_label = "Qualifications"
    navigation_subgroup = "Qualifications"
    navigation_icon = "heroicon-o-academic-cap"
    navigation_sort = 20

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        person = await _self(ctx.get("user"))
        if person is None:
            return _unlinked("Qualifications")
        skills = await _names(Skill)
        rows = [
            [skills.get(row.skill_id), row.years]
            for row in await _owned(EmployeeSkill, person.id)
        ]
        return _page(
            "Qualifications",
            "Skills recorded on your employee profile.",
            _table(["Skill", "Years"], rows),
        )


class ContractManagementPage(Guard, Page):
    """PIM contract list. An employee sees only their own contract."""

    slug = "contracts"
    title = "Contract management"
    navigation_label = "Contract management"
    navigation_group = "Contracts"
    navigation_icon = "heroicon-o-document-text"
    navigation_sort = 1
    data_group = "pim"

    @classmethod
    async def render(cls, **ctx: Any) -> str:
        user = ctx.get("user")
        from app.domain.operations import subordinate_ids_for

        subs = await subordinate_ids_for(user) if user is not None else set()
        statuses = await _names(EmploymentStatus)
        rows = []
        for person in await Employee.all():
            if not employee_in_scope(user, "pim", person.id, subs, write=False):
                continue
            rows.append(
                [
                    person.employee_number,
                    person.full_name,
                    statuses.get(person.employment_status_id),
                    person.joined_on,
                    person.terminated_on or "Open",
                ]
            )
        rows.sort(key=lambda row: str(row[0] or ""))
        return _page(
            "Contract management",
            "Employment contracts for people you are allowed to see. The start date is the join date.",
            _table(
                ["Employee number", "Name", "Status", "Contract start", "Contract end"],
                rows,
            ),
        )
