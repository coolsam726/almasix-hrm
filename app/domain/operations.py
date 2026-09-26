"""Persistence for the rules in the rest of this package."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Any
from xml.etree.ElementTree import ParseError

from app.domain.access import Denied, Invalid, require_scope, user_can_read, user_can_write
from app.domain.advanced import (
    can_publish_shift,
    certificate_code,
    nine_box_cell,
    payroll_export,
    valid_cadence,
    valid_connector_endpoint,
)
from app.domain.assistant import AssistantReply, answer
from app.domain.i18n import authorize_url, parse_xliff
from app.domain.leave import WEEKDAYS, as_date, count_leave_days, summarize
from app.domain.mfa import confirm_totp
from app.domain.notify import WorkflowNotification
from app.domain.people import (
    dashboard_snapshot,
    directory_rows,
    next_employee_number,
    org_tree,
    parse_employee_csv,
    subordinate_set,
    upcoming_anniversaries,
)
from app.domain.timekeeping import next_punch, validate_hours
from app.domain.workflow import resolve_transition
from app.models.hrm import (
    Asset,
    AttendanceRecord,
    AuditEvent,
    BuzzComment,
    BuzzLike,
    BuzzPost,
    Candidate,
    ClaimRequest,
    CourseEnrollment,
    CustomFieldValue,
    Dependent,
    DeskRequest,
    DevelopmentPlan,
    DisciplineCase,
    DocumentTemplate,
    EmergencyContact,
    Employee,
    EmployeeContact,
    EmployeeSalary,
    EmployeeSkill,
    Grievance,
    Holiday,
    ImmigrationRecord,
    LanguagePack,
    LeaveEntitlement,
    LeaveRequest,
    MfaFactor,
    ModuleSetting,
    NineBoxPlacement,
    OidcProvider,
    OnboardingAssignment,
    OnboardingTask,
    PayrollConnector,
    PolicyPost,
    Review,
    ScheduledReport,
    Shift,
    SurveyResponse,
    Timesheet,
    TimesheetItem,
    Vacancy,
    WorkflowTransition,
    WorkWeek,
)
from app.models.user import User


async def _rows(model: type[Any], **filters: Any) -> list[Any]:
    query = model.query()
    for key, value in filters.items():
        query = query.where(key, value)
    return list(await query.get())


async def load_modules() -> dict[str, bool]:
    return {row.key: bool(row.enabled) for row in await ModuleSetting.all()}


async def subordinate_ids_for(actor: Any) -> set[int]:
    employee_id = getattr(actor, "employee_id", None)
    if not employee_id:
        return set()
    pairs = []
    for person in await Employee.all():
        supervisor = person.supervisor_id
        pairs.append((int(person.id), int(supervisor) if supervisor else None))
    return subordinate_set(pairs, int(employee_id))


async def _notify(employee_id: Any, message: str) -> None:
    employee = await Employee.find(employee_id)
    if employee is None or not employee.user_id:
        return
    user = await User.find(employee.user_id)
    if user is not None:
        await user.notify(WorkflowNotification(message))


async def act(
    actor: Any,
    record: Any,
    *,
    flow: str,
    action: str,
    group: str,
    employee_id: Any,
) -> Any:
    modules = await load_modules()
    require_scope(
        actor,
        group,
        employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=modules,
    )
    nxt = resolve_transition(
        await _rows(WorkflowTransition, flow=flow),
        flow=flow,
        state=str(record.state),
        role=str(actor.role_slug),
        action=action,
    )
    await record.update({"state": nxt})
    await _notify(employee_id, f"{flow} is now {nxt}.")
    return record


async def _work_week() -> dict[str, bool]:
    weeks = list(await WorkWeek.all())
    if not weeks:
        return {day: day not in {"saturday", "sunday"} for day in WEEKDAYS}
    week = weeks[0]
    return {day: bool(getattr(week, day)) for day in WEEKDAYS}


async def _holidays() -> set[date]:
    return {as_date(row.observed_on) for row in await Holiday.all()}


async def apply_leave(
    actor: Any,
    employee_id: int,
    leave_type_id: int,
    starts_on: Any,
    ends_on: Any,
    *,
    partial: str = "full",
    comment: str = "",
) -> LeaveRequest:
    modules = await load_modules()
    require_scope(
        actor,
        "leave",
        employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=modules,
    )
    start = as_date(starts_on)
    end = as_date(ends_on)
    try:
        days = count_leave_days(start, end, await _work_week(), await _holidays(), partial=partial)
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    if days <= 0:
        raise Invalid("That range has no working days.")
    entitlements = await _rows(
        LeaveEntitlement, employee_id=employee_id, leave_type_id=leave_type_id
    )
    if not entitlements:
        raise Invalid("This employee has no entitlement for that leave type.")
    existing = await _rows(LeaveRequest, employee_id=employee_id, leave_type_id=leave_type_id)
    pairs = [(str(row.state), Decimal(str(row.days))) for row in existing]
    _, _, remaining = summarize(Decimal(str(entitlements[0].days)), pairs)
    if days > remaining:
        raise Invalid("Insufficient leave balance.")
    return await LeaveRequest.create(
        {
            "employee_id": employee_id,
            "leave_type_id": leave_type_id,
            "starts_on": start.isoformat(),
            "ends_on": end.isoformat(),
            "partial": partial,
            "days": str(days),
            "state": "pending",
            "comment": comment,
        }
    )


async def leave_balance(employee_id: int, leave_type_id: int) -> Decimal:
    entitlements = await _rows(
        LeaveEntitlement, employee_id=employee_id, leave_type_id=leave_type_id
    )
    entitled = Decimal(str(entitlements[0].days)) if entitlements else Decimal(0)
    existing = await _rows(LeaveRequest, employee_id=employee_id, leave_type_id=leave_type_id)
    pairs = [(str(row.state), Decimal(str(row.days))) for row in existing]
    _, _, remaining = summarize(entitled, pairs)
    return remaining


async def add_timesheet_hours(
    actor: Any,
    timesheet_id: int,
    *,
    project_id: int,
    worked_on: str,
    hours: str,
    activity_id: int | None = None,
) -> TimesheetItem:
    sheet = await Timesheet.find(timesheet_id)
    if sheet is None:
        raise Invalid("Timesheet not found.")
    if str(sheet.state) != "open":
        raise Invalid("Hours can only be added to an open timesheet.")
    try:
        amount = validate_hours(Decimal(str(hours)))
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    require_scope(
        actor,
        "time",
        sheet.employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    return await TimesheetItem.create(
        {
            "timesheet_id": timesheet_id,
            "project_id": project_id,
            "activity_id": activity_id,
            "worked_on": worked_on,
            "hours": str(amount),
        }
    )


async def punch(actor: Any, employee_id: int, kind: str, punched_at: str) -> AttendanceRecord:
    require_scope(
        actor,
        "time",
        employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    existing = await _rows(AttendanceRecord, employee_id=employee_id)
    try:
        next_punch([str(row.kind) for row in existing], kind)
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    return await AttendanceRecord.create(
        {
            "employee_id": employee_id,
            "punched_at": punched_at,
            "kind": kind,
            "state": "open",
        }
    )


async def hire_candidate(actor: Any, candidate_id: int) -> Employee:
    candidate = await Candidate.find(candidate_id)
    if candidate is None:
        raise Invalid("Candidate not found.")
    await act(
        actor,
        candidate,
        flow="recruitment",
        action="hire",
        group="recruitment",
        employee_id=actor.employee_id,
    )
    numbers = [str(row.employee_number) for row in await Employee.all()]
    employee = await Employee.create(
        {
            "employee_number": next_employee_number(numbers),
            "first_name": candidate.first_name,
            "last_name": candidate.last_name,
            "email": candidate.email,
            "supervisor_id": actor.employee_id,
            "joined_on": datetime.now(UTC).date().isoformat(),
        }
    )
    await candidate.update({"employee_id": employee.id, "state": "hired"})
    await AuditEvent.create(
        {
            "actor_id": actor.id,
            "action": "hire",
            "subject": f"employee:{employee.id}",
        }
    )
    return employee


async def post_buzz(actor: Any, body: str) -> BuzzPost:
    text = body.strip()
    if not text:
        raise Invalid("A post needs text.")
    require_scope(
        actor,
        "buzz",
        actor.employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    return await BuzzPost.create({"employee_id": actor.employee_id, "body": text})


async def comment_buzz(actor: Any, post_id: int, body: str) -> BuzzComment:
    text = body.strip()
    if not text:
        raise Invalid("A comment needs text.")
    if not user_can_write(actor, "buzz", await load_modules()):
        raise Denied("Not allowed to comment.")
    return await BuzzComment.create(
        {"post_id": post_id, "employee_id": actor.employee_id, "body": text}
    )


async def like_buzz(actor: Any, post_id: int) -> BuzzLike:
    if not user_can_read(actor, "buzz", await load_modules()):
        raise Denied("Not allowed to like posts.")
    existing = await _rows(BuzzLike, post_id=post_id, employee_id=actor.employee_id)
    if existing:
        raise Invalid("You already liked this post.")
    return await BuzzLike.create({"post_id": post_id, "employee_id": actor.employee_id})


async def open_claim(actor: Any, employee_id: int, claim_type_id: int, amount: str) -> ClaimRequest:
    value = Decimal(str(amount))
    if value <= 0:
        raise Invalid("Claim amount must be greater than zero.")
    require_scope(
        actor,
        "claim",
        employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    return await ClaimRequest.create(
        {
            "employee_id": employee_id,
            "claim_type_id": claim_type_id,
            "amount": str(value),
            "state": "draft",
            "note": "",
        }
    )


async def purge_employee(actor: Any, employee_id: int) -> None:
    if not user_can_write(actor, "maintenance", await load_modules()):
        raise Denied("Not allowed to purge employee data.")
    employee = await Employee.find(employee_id)
    if employee is None:
        raise Invalid("Employee not found.")
    pairs = []
    for person in await Employee.all():
        supervisor = person.supervisor_id
        pairs.append((int(person.id), int(supervisor) if supervisor else None))
    if subordinate_set(pairs, int(employee_id)):
        raise Invalid("Reassign or remove people who report here before purging.")
    for sheet in await _rows(Timesheet, employee_id=employee_id):
        for item in await _rows(TimesheetItem, timesheet_id=sheet.id):
            await item.delete()
        await sheet.delete()
    for post in await _rows(BuzzPost, employee_id=employee_id):
        for comment in await _rows(BuzzComment, post_id=post.id):
            await comment.delete()
        for like in await _rows(BuzzLike, post_id=post.id):
            await like.delete()
        await post.delete()
    for model in (
        EmployeeContact,
        EmergencyContact,
        Dependent,
        ImmigrationRecord,
        EmployeeSalary,
        EmployeeSkill,
        CustomFieldValue,
        LeaveEntitlement,
        LeaveRequest,
        AttendanceRecord,
        BuzzComment,
        BuzzLike,
        ClaimRequest,
        DeskRequest,
        DevelopmentPlan,
        Grievance,
        DisciplineCase,
        Asset,
        OnboardingAssignment,
        Shift,
        NineBoxPlacement,
        CourseEnrollment,
        SurveyResponse,
        Review,
    ):
        for row in await _rows(model, employee_id=employee_id):
            await row.delete()
    await employee.delete()
    await AuditEvent.create(
        {
            "actor_id": getattr(actor, "id", None),
            "action": "purge",
            "subject": f"employee:{employee_id}",
        }
    )


async def import_employees(actor: Any, csv_text: str) -> list[Employee]:
    if not user_can_write(actor, "pim", await load_modules()):
        raise Denied("Not allowed to import employees.")
    try:
        parsed = parse_employee_csv(csv_text)
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    created: list[Employee] = []
    for row in parsed:
        if await _rows(Employee, email=row["email"]):
            continue
        created.append(
            await Employee.create(
                {
                    **row,
                    "joined_on": datetime.now(UTC).date().isoformat(),
                }
            )
        )
    return created


async def import_language_pack(actor: Any, xml_text: str, name: str) -> LanguagePack:
    if not user_can_write(actor, "admin", await load_modules()):
        raise Denied("Not allowed to import languages.")
    try:
        code, catalog = parse_xliff(xml_text)
    except (ValueError, ParseError) as exc:
        raise Invalid("The language file could not be read.") from exc
    return await LanguagePack.create({"code": code, "name": name or code, "catalog": catalog})


async def save_oidc_provider(
    actor: Any, *, name: str, issuer: str, client_id: str, redirect_uri: str
) -> tuple[Any, str]:
    if not user_can_write(actor, "admin", await load_modules()):
        raise Denied("Not allowed to configure login providers.")
    try:
        url = authorize_url(
            issuer=issuer,
            client_id=client_id,
            redirect_uri=redirect_uri,
            state="setup",
        )
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    provider = await OidcProvider.create(
        {"name": name, "issuer": issuer, "client_id": client_id, "enabled": True}
    )
    return provider, url


async def set_custom_value(
    actor: Any, employee_id: int, custom_field_id: int, value: str
) -> CustomFieldValue:
    require_scope(
        actor,
        "pim",
        employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    return await CustomFieldValue.create(
        {"employee_id": employee_id, "custom_field_id": custom_field_id, "value": value}
    )


async def complete_onboarding(actor: Any, assignment_id: int) -> OnboardingAssignment:
    assignment = await OnboardingAssignment.find(assignment_id)
    if assignment is None:
        raise Invalid("Onboarding assignment not found.")
    tasks = await _rows(OnboardingTask, template_id=assignment.template_id)
    raw_done = assignment.completed_task_ids or []
    if isinstance(raw_done, str):
        raw_done = json.loads(raw_done or "[]")
    done = {int(item) for item in raw_done}
    if any(int(task.id) not in done for task in tasks):
        raise Invalid("Finish every task before completing onboarding.")
    return await act(
        actor,
        assignment,
        flow="onboarding",
        action="complete",
        group="onboarding",
        employee_id=assignment.employee_id,
    )


async def publish_shift(actor: Any, shift_id: int) -> Shift:
    if not user_can_write(actor, "roster", await load_modules()):
        raise Denied("Not allowed to publish shifts.")
    shift = await Shift.find(shift_id)
    if shift is None:
        raise Invalid("Shift not found.")
    if not can_publish_shift(
        employee_id=shift.employee_id,
        location_id=shift.location_id,
        starts_at=str(shift.starts_at),
        ends_at=str(shift.ends_at),
    ):
        raise Invalid("Assign a person and a location, and end the shift after it starts.")
    await shift.update({"published": True})
    return shift


async def place_nine_box(actor: Any, employee_id: int, performance: int, potential: int) -> Any:
    require_scope(
        actor,
        "career",
        employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    try:
        performance, potential = nine_box_cell(performance, potential)
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    return await NineBoxPlacement.create(
        {
            "employee_id": employee_id,
            "performance": performance,
            "potential": potential,
        }
    )


async def add_development_goal(actor: Any, employee_id: int, goal: str) -> DevelopmentPlan:
    text = goal.strip()
    if not text:
        raise Invalid("A development plan needs a goal.")
    require_scope(
        actor,
        "career",
        employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    return await DevelopmentPlan.create({"employee_id": employee_id, "goal": text})


async def complete_course(actor: Any, enrollment_id: int) -> CourseEnrollment:
    enrollment = await CourseEnrollment.find(enrollment_id)
    if enrollment is None:
        raise Invalid("Enrollment not found.")
    require_scope(
        actor,
        "training",
        enrollment.employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    code = certificate_code(int(enrollment.course_id), int(enrollment.employee_id))
    await enrollment.update({"completed": True, "certificate_code": code})
    return enrollment


async def respond_survey(actor: Any, survey_id: int, answer_text: str) -> SurveyResponse:
    text = answer_text.strip()
    if not text:
        raise Invalid("A survey response needs an answer.")
    require_scope(
        actor,
        "surveys",
        actor.employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    existing = await _rows(SurveyResponse, survey_id=survey_id, employee_id=actor.employee_id)
    if existing:
        raise Invalid("You already answered this survey.")
    return await SurveyResponse.create(
        {"survey_id": survey_id, "employee_id": actor.employee_id, "answer": text}
    )


async def confirm_mfa(actor: Any, factor_id: int, code: str, at: int) -> MfaFactor:
    factor = await MfaFactor.find(factor_id)
    if factor is None or int(factor.user_id) != int(actor.id):
        raise Denied("That authenticator does not belong to you.")
    if factor.kind != "totp":
        raise Invalid("Only authenticator codes can be confirmed here.")
    if not confirm_totp(str(factor.secret).encode(), code, at):
        raise Invalid("That code is not valid.")
    await factor.update({"confirmed": True})
    return factor


async def schedule_report(actor: Any, name: str, cadence: str) -> ScheduledReport:
    if not user_can_write(actor, "reports", await load_modules()):
        raise Denied("Not allowed to schedule reports.")
    try:
        cadence = valid_cadence(cadence)
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    return await ScheduledReport.create({"name": name, "cadence": cadence})


async def save_connector(actor: Any, name: str, endpoint: str) -> PayrollConnector:
    if not user_can_write(actor, "payroll", await load_modules()):
        raise Denied("Not allowed to configure payroll connectors.")
    try:
        endpoint = valid_connector_endpoint(endpoint)
    except ValueError as exc:
        raise Invalid(str(exc)) from exc
    connector = await PayrollConnector.create(
        {"name": name, "endpoint": endpoint, "enabled": True}
    )
    await AuditEvent.create(
        {"actor_id": actor.id, "action": "payroll-connector", "subject": f"connector:{connector.id}"}
    )
    return connector


async def export_payroll(actor: Any) -> list[dict[str, Any]]:
    if not user_can_read(actor, "payroll", await load_modules()):
        raise Denied("Not allowed to read payroll data.")
    include_salary = user_can_read(actor, "payroll", await load_modules())
    rows = []
    for employee in await Employee.all():
        if employee.terminated_on:
            continue
        salaries = await _rows(EmployeeSalary, employee_id=employee.id)
        amount = salaries[0].amount if salaries else None
        rows.append(
            {
                "employee_number": employee.employee_number,
                "name": employee.full_name,
                "amount": amount,
            }
        )
    return payroll_export(rows, include_salary=include_salary)


async def assign_asset(actor: Any, name: str, serial: str, employee_id: int) -> Asset:
    if not user_can_write(actor, "assets", await load_modules()):
        raise Denied("Not allowed to assign assets.")
    return await Asset.create({"name": name, "serial": serial, "employee_id": employee_id})


async def publish_policy(actor: Any, title: str, body: str) -> PolicyPost:
    if not user_can_write(actor, "policies", await load_modules()):
        raise Denied("Not allowed to publish policies.")
    if not title.strip() or not body.strip():
        raise Invalid("A policy needs a title and a body.")
    return await PolicyPost.create({"title": title.strip(), "body": body.strip()})


async def save_template(actor: Any, name: str, body: str) -> DocumentTemplate:
    if not user_can_write(actor, "documents", await load_modules()):
        raise Denied("Not allowed to edit document templates.")
    if not name.strip() or not body.strip():
        raise Invalid("A template needs a name and a body.")
    return await DocumentTemplate.create({"name": name.strip(), "body": body.strip()})


async def ask_assistant(actor: Any, question: str, *, leave_type_id: int | None = None) -> AssistantReply:
    if not user_can_read(actor, "assistant", await load_modules()):
        raise Denied("The assistant is not available to you.")
    context: dict[str, Any] = {"headcount": 0, "reports_to": None, "leave_balance": None}
    active = [row for row in await Employee.all() if not row.terminated_on]
    context["headcount"] = len(active)
    if actor.employee_id and leave_type_id:
        context["leave_balance"] = str(await leave_balance(int(actor.employee_id), leave_type_id))
    if actor.employee_id:
        person = await Employee.find(actor.employee_id)
        if person and person.supervisor_id:
            manager = await Employee.find(person.supervisor_id)
            if manager:
                context["reports_to"] = manager.full_name
    if user_can_read(actor, "payroll"):
        exported = await export_payroll(actor)
        context["payroll_summary"] = f"{len(exported)} people in the payroll export."
    return answer(question, actor, context)


async def directory() -> list[dict[str, Any]]:
    rows = []
    for employee in await Employee.all():
        rows.append(
            {
                "id": employee.id,
                "name": employee.full_name,
                "job_title": "",
                "location": "",
                "terminated_on": employee.terminated_on,
            }
        )
    return directory_rows(rows)


async def organization_chart() -> list[dict[str, Any]]:
    rows = []
    for employee in await Employee.all():
        if employee.terminated_on:
            continue
        rows.append(
            {
                "id": employee.id,
                "name": employee.full_name,
                "supervisor_id": employee.supervisor_id,
            }
        )
    return org_tree(rows)


async def dashboard() -> dict[str, int]:
    people = list(await Employee.all())
    pending = [row for row in await LeaveRequest.all() if str(row.state) == "pending"]
    open_roles = [row for row in await Vacancy.all() if str(row.state) == "open"]
    return dashboard_snapshot(
        headcount=len([person for person in people if not person.terminated_on]),
        pending_leave=len(pending),
        open_vacancies=len(open_roles),
    )


async def anniversaries(today: date | None = None) -> list[dict[str, Any]]:
    today = today or datetime.now(UTC).date()
    rows = [
        {
            "id": employee.id,
            "name": employee.full_name,
            "joined_on": employee.joined_on,
            "terminated_on": employee.terminated_on,
        }
        for employee in await Employee.all()
    ]
    return upcoming_anniversaries(rows, today)


async def open_desk(actor: Any, kind: str, subject: str) -> DeskRequest:
    if not subject.strip():
        raise Invalid("A request needs a subject.")
    require_scope(
        actor,
        "desk",
        actor.employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    return await DeskRequest.create(
        {
            "employee_id": actor.employee_id,
            "kind": kind,
            "subject": subject.strip(),
            "state": "open",
        }
    )


async def open_grievance(actor: Any, kind: str, body: str) -> Grievance:
    if not body.strip():
        raise Invalid("A grievance needs a description.")
    require_scope(
        actor,
        "voice",
        actor.employee_id,
        await subordinate_ids_for(actor),
        write=True,
        modules=await load_modules(),
    )
    return await Grievance.create(
        {
            "employee_id": actor.employee_id,
            "kind": kind,
            "body": body.strip(),
            "state": "open",
        }
    )


async def open_discipline(actor: Any, employee_id: int, summary: str, investigator_id: int) -> Any:
    if not summary.strip():
        raise Invalid("A case needs a summary.")
    if not user_can_write(actor, "discipline", await load_modules()):
        raise Denied("Not allowed to open discipline cases.")
    return await DisciplineCase.create(
        {
            "employee_id": employee_id,
            "investigator_id": investigator_id,
            "summary": summary.strip(),
            "state": "open",
        }
    )
