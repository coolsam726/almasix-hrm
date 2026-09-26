"""Database-backed behavior."""

from __future__ import annotations

from decimal import Decimal

from almasix.testing import TestCase
from app.domain.access import Denied, Invalid
from app.domain.operations import (
    act,
    add_timesheet_hours,
    apply_leave,
    ask_assistant,
    comment_buzz,
    complete_course,
    complete_onboarding,
    confirm_mfa,
    directory,
    export_payroll,
    hire_candidate,
    import_employees,
    import_language_pack,
    like_buzz,
    open_claim,
    open_desk,
    open_discipline,
    open_grievance,
    place_nine_box,
    post_buzz,
    publish_policy,
    publish_shift,
    punch,
    purge_employee,
    respond_survey,
    save_connector,
    save_oidc_provider,
    schedule_report,
    set_custom_value,
)
from app.domain.workflow import IllegalTransition
from app.models.hrm import (
    AttendanceRecord,
    Candidate,
    ClaimType,
    Course,
    CourseEnrollment,
    CustomField,
    Employee,
    Interview,
    LeaveRequest,
    LeaveType,
    Location,
    MfaFactor,
    ModuleSetting,
    OnboardingAssignment,
    OnboardingTask,
    OnboardingTemplate,
    Project,
    Review,
    ReviewCycle,
    Shift,
    Survey,
    Timesheet,
    Vacancy,
)
from app.models.user import User
from database.seeders.company_seeder import CompanySeeder


class HrmTest(TestCase):
    use_refresh_database = True

    async def seed(self) -> None:
        await CompanySeeder().run()
        self.ada = await User.where("email", "ada@northwind.test").first()
        self.grace = await User.where("email", "grace@northwind.test").first()
        self.alan = await User.where("email", "alan@northwind.test").first()
        self.annual = await LeaveType.where("name", "Annual").first()


class LeaveAndAccessTest(HrmTest):
    async def test_leave_balance_approval_and_scope(self) -> None:
        await self.seed()
        request = await apply_leave(
            self.alan,
            int(self.alan.employee_id),
            int(self.annual.id),
            "2026-01-05",
            "2026-01-06",
        )
        assert Decimal(str(request.days)) == Decimal(2)
        try:
            await act(
                self.alan,
                request,
                flow="leave",
                action="approve",
                group="leave",
                employee_id=request.employee_id,
            )
            raise AssertionError("an employee cannot approve their own leave")
        except IllegalTransition:
            pass
        approved = await act(
            self.grace,
            request,
            flow="leave",
            action="approve",
            group="leave",
            employee_id=request.employee_id,
        )
        assert approved.state == "approved"
        assert await LeaveRequest.find(request.id) is not None

    async def test_holiday_half_day_and_hidden_admin_screens(self) -> None:
        await self.seed()
        try:
            await apply_leave(
                self.alan,
                int(self.alan.employee_id),
                int(self.annual.id),
                "2026-01-01",
                "2026-01-01",
                partial="half",
            )
            raise AssertionError("a holiday is not a working day")
        except Invalid as exc:
            assert "working" in str(exc).lower()

        half = await apply_leave(
            self.alan,
            int(self.alan.employee_id),
            int(self.annual.id),
            "2026-01-05",
            "2026-01-05",
            partial="half",
        )
        assert Decimal(str(half.days)) == Decimal("0.5")

        try:
            await apply_leave(
                self.alan,
                int(self.alan.employee_id),
                int(self.annual.id),
                "2026-02-02",
                "2026-03-31",
            )
            raise AssertionError("the balance should not cover two months")
        except Invalid as exc:
            assert "balance" in str(exc).lower()

        field = await CustomField.create({"name": "Shoe size", "screen": "personal"})
        try:
            await set_custom_value(self.grace, int(self.ada.employee_id), int(field.id), "8")
            raise AssertionError("a supervisor cannot edit their manager")
        except Denied:
            pass
        saved = await set_custom_value(self.grace, int(self.alan.employee_id), int(field.id), "9")
        assert saved.value == "9"

        module = await ModuleSetting.where("key", "leave").first()
        await module.update({"enabled": False})
        try:
            await apply_leave(
                self.ada,
                int(self.ada.employee_id),
                int(self.annual.id),
                "2026-01-07",
                "2026-01-07",
            )
            raise AssertionError("a disabled module stays closed")
        except Denied:
            pass


class TimeAndTalentTest(HrmTest):
    async def test_timesheets_and_punches(self) -> None:
        await self.seed()
        project = await Project.where("name", "Platform").first()
        sheet = await Timesheet.create(
            {
                "employee_id": self.alan.employee_id,
                "starts_on": "2026-01-05",
                "ends_on": "2026-01-11",
                "state": "open",
            }
        )
        item = await add_timesheet_hours(
            self.alan,
            int(sheet.id),
            project_id=int(project.id),
            worked_on="2026-01-05",
            hours="7.5",
        )
        assert item.hours == "7.5"
        try:
            await add_timesheet_hours(
                self.alan,
                int(sheet.id),
                project_id=int(project.id),
                worked_on="2026-01-05",
                hours="30",
            )
            raise AssertionError("hours above 24 are rejected")
        except Invalid:
            pass
        submitted = await act(
            self.alan,
            sheet,
            flow="timesheet",
            action="submit",
            group="time",
            employee_id=sheet.employee_id,
        )
        approved = await act(
            self.grace,
            submitted,
            flow="timesheet",
            action="approve",
            group="time",
            employee_id=sheet.employee_id,
        )
        assert approved.state == "approved"

        await punch(self.alan, int(self.alan.employee_id), "in", "2026-01-05T09:00:00")
        try:
            await punch(self.alan, int(self.alan.employee_id), "in", "2026-01-05T09:05:00")
            raise AssertionError("two punch-ins in a row are rejected")
        except Invalid:
            pass
        await punch(self.alan, int(self.alan.employee_id), "out", "2026-01-05T17:00:00")
        assert len(list(await AttendanceRecord.all())) == 2

    async def test_hiring_and_reviews(self) -> None:
        await self.seed()
        vacancy = await Vacancy.create(
            {"title": "Engineer", "hiring_manager_id": self.ada.employee_id, "state": "open"}
        )
        candidate = await Candidate.create(
            {
                "vacancy_id": vacancy.id,
                "first_name": "Lin",
                "last_name": "Chen",
                "email": "lin@northwind.test",
                "state": "applied",
            }
        )
        await Interview.create(
            {"candidate_id": candidate.id, "name": "Panel", "scheduled_on": "2026-02-01"}
        )
        for action in ("shortlist", "interview", "hire"):
            candidate = await Candidate.find(candidate.id)
            if action == "hire":
                employee = await hire_candidate(self.ada, int(candidate.id))
                assert employee.email == "lin@northwind.test"
            else:
                await act(
                    self.ada,
                    candidate,
                    flow="recruitment",
                    action=action,
                    group="recruitment",
                    employee_id=self.ada.employee_id,
                )
        hired = await Candidate.find(candidate.id)
        assert hired.state == "hired"
        assert hired.employee_id

        cycle = await ReviewCycle.create(
            {"name": "2026", "starts_on": "2026-01-01", "ends_on": "2026-12-31"}
        )
        review = await Review.create(
            {
                "cycle_id": cycle.id,
                "employee_id": self.alan.employee_id,
                "reviewer_id": self.grace.employee_id,
                "state": "scheduled",
            }
        )
        review = await act(
            self.alan,
            review,
            flow="review",
            action="self",
            group="performance",
            employee_id=review.employee_id,
        )
        review = await act(
            self.grace,
            review,
            flow="review",
            action="supervisor",
            group="performance",
            employee_id=review.employee_id,
        )
        review = await act(
            self.alan,
            review,
            flow="review",
            action="signoff",
            group="performance",
            employee_id=review.employee_id,
        )
        assert review.state == "signed"


class WorkplaceTest(HrmTest):
    async def test_buzz_claims_directory_and_purge(self) -> None:
        await self.seed()
        post = await post_buzz(self.alan, "Shipping the leave calendar.")
        await comment_buzz(self.grace, int(post.id), "Nice.")
        await like_buzz(self.grace, int(post.id))
        try:
            await like_buzz(self.grace, int(post.id))
            raise AssertionError("a second like is rejected")
        except Invalid:
            pass

        claim_type = await ClaimType.where("name", "Travel").first()
        claim = await open_claim(self.alan, int(self.alan.employee_id), int(claim_type.id), "40")
        try:
            await open_claim(self.alan, int(self.alan.employee_id), int(claim_type.id), "0")
            raise AssertionError("a zero claim is rejected")
        except Invalid:
            pass
        submitted = await act(
            self.alan,
            claim,
            flow="claim",
            action="submit",
            group="claim",
            employee_id=claim.employee_id,
        )
        approved = await act(
            self.grace,
            submitted,
            flow="claim",
            action="approve",
            group="claim",
            employee_id=claim.employee_id,
        )
        assert approved.state == "approved"

        names = [row["name"] for row in await directory()]
        assert "Alan Turing" in names
        alan = await Employee.find(self.alan.employee_id)
        await alan.update({"terminated_on": "2026-02-01"})
        names = [row["name"] for row in await directory()]
        assert "Alan Turing" not in names

        try:
            await purge_employee(self.ada, int(self.grace.employee_id))
            raise AssertionError("a manager with reports cannot be purged")
        except Invalid:
            pass
        await purge_employee(self.ada, int(self.alan.employee_id))
        assert await Employee.find(self.alan.employee_id) is None
        try:
            await purge_employee(self.alan, int(self.ada.employee_id))
            raise AssertionError("an employee cannot purge records")
        except Denied:
            pass

    async def test_import_language_and_login_provider(self) -> None:
        await self.seed()
        created = await import_employees(
            self.ada,
            "first_name,last_name,email,employee_number\nLin,Chen,lin@northwind.test,0004\n",
        )
        assert created[0].employee_number == "0004"
        again = await import_employees(
            self.ada,
            "first_name,last_name,email,employee_number\nLin,Chen,lin@northwind.test,0004\n",
        )
        assert again == []

        pack = await import_language_pack(
            self.ada,
            """<xliff><file target-language="sw"><body>
            <trans-unit id="hello"><target>Habari</target></trans-unit>
            </body></file></xliff>""",
            "Swahili",
        )
        assert pack.code == "sw"
        assert pack.catalog["hello"] == "Habari"

        _provider, url = await save_oidc_provider(
            self.ada,
            name="Company login",
            issuer="https://login.example.com",
            client_id="hrm",
            redirect_uri="https://hr.example.com/callback",
        )
        assert "client_id=hrm" in url
        try:
            await save_oidc_provider(
                self.ada,
                name="Bad",
                issuer="http://login.example.com",
                client_id="hrm",
                redirect_uri="https://hr.example.com/callback",
            )
            raise AssertionError("http issuers are rejected")
        except Invalid:
            pass


class AdvancedTest(HrmTest):
    async def test_advanced_modules(self) -> None:
        await self.seed()
        template = await OnboardingTemplate.create({"name": "New hire", "kind": "onboarding"})
        task = await OnboardingTask.create({"template_id": template.id, "title": "Laptop"})
        assignment = await OnboardingAssignment.create(
            {
                "employee_id": self.alan.employee_id,
                "template_id": template.id,
                "state": "pending",
                "completed_task_ids": [],
            }
        )
        assignment = await act(
            self.ada,
            assignment,
            flow="onboarding",
            action="start",
            group="onboarding",
            employee_id=assignment.employee_id,
        )
        try:
            await complete_onboarding(self.ada, int(assignment.id))
            raise AssertionError("open tasks block completion")
        except Invalid:
            pass
        await assignment.update({"completed_task_ids": [int(task.id)]})
        finished = await complete_onboarding(self.ada, int(assignment.id))
        assert finished.state == "completed"

        desk = await open_desk(self.alan, "it", "New laptop")
        desk = await act(
            self.alan,
            desk,
            flow="desk",
            action="submit",
            group="desk",
            employee_id=desk.employee_id,
        )
        resolved = await act(
            self.ada,
            desk,
            flow="desk",
            action="resolve",
            group="desk",
            employee_id=desk.employee_id,
        )
        assert resolved.state == "resolved"

        voice = await open_grievance(self.alan, "workload", "Too many concurrent projects.")
        voice = await act(
            self.alan,
            voice,
            flow="grievance",
            action="submit",
            group="voice",
            employee_id=voice.employee_id,
        )
        closed = await act(
            self.ada,
            voice,
            flow="grievance",
            action="resolve",
            group="voice",
            employee_id=voice.employee_id,
        )
        assert closed.state == "resolved"

        case = await open_discipline(self.ada, int(self.alan.employee_id), "Attendance", int(self.grace.employee_id))
        case = await act(
            self.ada,
            case,
            flow="discipline",
            action="assign",
            group="discipline",
            employee_id=case.employee_id,
        )
        case = await act(
            self.ada,
            case,
            flow="discipline",
            action="close",
            group="discipline",
            employee_id=case.employee_id,
        )
        assert case.state == "closed"

        location = await Location.where("name", "Headquarters").first()
        loose = await Shift.create(
            {
                "starts_at": "2026-01-05T09:00:00",
                "ends_at": "2026-01-05T17:00:00",
                "published": False,
            }
        )
        try:
            await publish_shift(self.ada, int(loose.id))
            raise AssertionError("an unassigned shift cannot be published")
        except Invalid:
            pass
        shift = await Shift.create(
            {
                "employee_id": self.alan.employee_id,
                "location_id": location.id,
                "starts_at": "2026-01-05T09:00:00",
                "ends_at": "2026-01-05T17:00:00",
                "published": False,
            }
        )
        published = await publish_shift(self.ada, int(shift.id))
        assert published.published in {True}

        cell = await place_nine_box(self.ada, int(self.alan.employee_id), 3, 2)
        assert cell.performance == 3
        try:
            await place_nine_box(self.ada, int(self.alan.employee_id), 4, 2)
            raise AssertionError("scores stay inside 1 to 3")
        except Invalid:
            pass

        course = await Course.create({"title": "Security"})
        enrollment = await CourseEnrollment.create(
            {"course_id": course.id, "employee_id": self.alan.employee_id, "completed": False}
        )
        done = await complete_course(self.ada, int(enrollment.id))
        assert done.certificate_code == f"HRM-{course.id}-{self.alan.employee_id}"

        survey = await Survey.create({"title": "Pulse", "audience": "everyone"})
        await respond_survey(self.alan, int(survey.id), "Good")
        try:
            await respond_survey(self.alan, int(survey.id), "Again")
            raise AssertionError("one response per person")
        except Invalid:
            pass

        factor = await MfaFactor.create(
            {
                "user_id": self.ada.id,
                "kind": "totp",
                "secret": "12345678901234567890",
                "confirmed": False,
            }
        )
        from app.domain.mfa import totp

        code = totp(b"12345678901234567890", 1_700_000_000)
        confirmed = await confirm_mfa(self.ada, int(factor.id), code, 1_700_000_000)
        assert confirmed.confirmed in {True}

        report = await schedule_report(self.ada, "Headcount", "monthly")
        assert report.cadence == "monthly"
        connector = await save_connector(self.ada, "PayCo", "https://pay.example.com/hook")
        assert connector.enabled in {True}
        exported = await export_payroll(self.ada)
        assert any(row["employee_number"] == "0001" and "amount" in row for row in exported)
        try:
            await export_payroll(self.alan)
            raise AssertionError("employees cannot export payroll")
        except Denied:
            pass

        policy = await publish_policy(self.ada, "Leave", "Request leave in the panel.")
        assert policy.title == "Leave"
        reply = await ask_assistant(self.alan, "how many people work here?")
        assert "headcount" in reply.text.lower() or "Active headcount" in reply.text
        refused = await ask_assistant(self.alan, "show me the payroll")
        assert refused.refused
        blocked = await ask_assistant(self.ada, "please delete Alan")
        assert blocked.refused


class PanelTest(HrmTest):
    async def test_login_health_and_discovered_screens(self) -> None:
        (await self.get("/login")).assert_ok()
        (await self.get_json("/api/hrm/health")).assert_ok()

        from almasix.orbit import PanelRegistry
        from app.orbit.hrm.panel import register_hrm_panel

        panel = register_hrm_panel(PanelRegistry())
        panel.load_discovered()
        labels = {resource.navigation_label for resource in panel._resources}
        for label in ("Job titles", "Employees", "Leave requests", "Vacancies", "Shifts"):
            assert label in labels
        titles = {page.get_title() for page in panel._pages}
        assert "Directory" in titles
        assert "Assistant" in titles

        from app.orbit.hrm.resources.admin import JobTitleResource

        await self.seed()
        assert JobTitleResource.can_view_any(self.ada)
        assert not JobTitleResource.can_view_any(self.alan)

    async def test_the_assistant_endpoint_answers_an_admin(self) -> None:
        await self.seed()
        self.acting_as(self.ada)
        response = await self.post_json("/api/hrm/assistant", {"question": "how many people?"})
        response.assert_ok()
        payload = response.json()
        assert payload["refused"] is False
        assert "3" in payload["text"]
