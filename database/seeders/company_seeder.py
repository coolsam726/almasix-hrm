"""Northwind People — a small Nairobi company for local development.

Sign in as ada@northwind.test (administrator), grace@northwind.test (supervisor),
or alan@northwind.test (employee). The password is secret. Alan has no direct
reports, so maintenance checks can still remove his record.
"""

from __future__ import annotations

from almasix.hashing import Hash
from almasix.orm import Seeder
from app.domain.catalog import (
    DATA_GROUPS,
    DEFAULT_TRANSITIONS,
    ROLE_ADMIN,
    ROLE_ESS,
    ROLE_SUPERVISOR,
    admin_grants,
    ess_grants,
    supervisor_grants,
)
from app.models.hrm import (
    Asset,
    BrandingSetting,
    BuzzComment,
    BuzzLike,
    BuzzPost,
    Candidate,
    ClaimRequest,
    ClaimType,
    Course,
    CourseEnrollment,
    Customer,
    CustomField,
    CustomFieldValue,
    Dependent,
    DeskRequest,
    DevelopmentPlan,
    DocumentTemplate,
    EducationLevel,
    EmailSetting,
    EmergencyContact,
    Employee,
    EmployeeContact,
    EmployeeSalary,
    EmployeeSkill,
    EmploymentStatus,
    Holiday,
    Interview,
    JobCategory,
    JobTitle,
    Kpi,
    Language,
    LanguagePack,
    LeaveEntitlement,
    LeavePeriod,
    LeaveRequest,
    LeaveType,
    LicenseType,
    LocalizationSetting,
    Location,
    Membership,
    ModuleSetting,
    Nationality,
    NineBoxPlacement,
    OidcProvider,
    OnboardingAssignment,
    OnboardingTask,
    OnboardingTemplate,
    OrgUnit,
    PayGrade,
    PayrollConnector,
    PolicyPost,
    Project,
    ProjectActivity,
    Review,
    ReviewCycle,
    Role,
    ScheduledReport,
    Shift,
    Skill,
    Survey,
    SurveyResponse,
    TerminationReason,
    Timesheet,
    TimesheetItem,
    Tracker,
    Vacancy,
    WorkflowTransition,
    WorkShift,
    WorkWeek,
)
from app.models.user import User


class CompanySeeder(Seeder):
    async def run(self) -> None:
        if await User.where("email", "ada@northwind.test").first():
            return

        await self._platform()
        catalog = await self._catalog()
        people = await self._people(catalog)
        await self._accounts(people)
        await self._operations(catalog, people)

    async def _platform(self) -> None:
        for name, slug in (
            ("Administrator", ROLE_ADMIN),
            ("Supervisor", ROLE_SUPERVISOR),
            ("Employee", ROLE_ESS),
        ):
            await Role.create({"name": name, "slug": slug})

        for flow, state, role, action, nxt in DEFAULT_TRANSITIONS:
            await WorkflowTransition.create(
                {
                    "flow": flow,
                    "state": state,
                    "role_slug": role,
                    "action": action,
                    "next_state": nxt,
                }
            )

        for key in DATA_GROUPS:
            await ModuleSetting.create({"key": key, "enabled": True})

        await LocalizationSetting.create({"date_format": "Y-m-d", "language": "en"})
        await BrandingSetting.create({"brand_name": "Northwind People", "primary_color": "#0f766e"})
        await EmailSetting.create(
            {
                "host": "smtp.northwind.test",
                "port": "587",
                "username": "hr@northwind.test",
                "from_address": "hr@northwind.test",
            }
        )
        await OidcProvider.create(
            {
                "name": "Northwind IdP",
                "issuer": "https://login.northwind.test",
                "client_id": "almasix-hrm",
                "enabled": False,
            }
        )
        await WorkWeek.create(
            {
                "monday": True,
                "tuesday": True,
                "wednesday": True,
                "thursday": True,
                "friday": True,
                "saturday": False,
                "sunday": False,
            }
        )

    async def _catalog(self) -> dict[str, object]:
        titles = await _named(
            JobTitle,
            (
                "Chief Executive",
                "Engineering Manager",
                "Engineer",
                "People Partner",
                "Accountant",
                "Designer",
            ),
        )
        grades = await _named(PayGrade, ("L1", "L2", "L3", "L4"))
        statuses = await _named(EmploymentStatus, ("Full-time", "Contract", "Intern"))
        await _named(JobCategory, ("Engineering", "People", "Finance", "Design"))
        await WorkShift.create({"name": "General", "start_time": "09:00", "end_time": "17:00"})
        await WorkShift.create({"name": "Early", "start_time": "07:00", "end_time": "15:00"})

        hq = await Location.create({"name": "Headquarters", "city": "Nairobi", "country": "Kenya"})
        coast = await Location.create({"name": "Coast studio", "city": "Mombasa", "country": "Kenya"})
        company = await OrgUnit.create({"name": "Northwind People"})
        engineering = await OrgUnit.create({"name": "Engineering", "parent_id": company.id})
        people_unit = await OrgUnit.create({"name": "People", "parent_id": company.id})
        finance = await OrgUnit.create({"name": "Finance", "parent_id": company.id})

        skills = await _named(Skill, ("Python", "SQL", "Facilitation", "Design systems"))
        await _named(EducationLevel, ("Bachelor", "Master"))
        await _named(LicenseType, ("Driving", "First aid"))
        await _named(Language, ("English", "Swahili"))
        await _named(Membership, ("IEEE", "Association for Computing Machinery"))
        nationalities = await _named(Nationality, ("Kenyan", "British", "American"))
        reasons = await _named(TerminationReason, ("Resignation", "End of contract"))

        for name, observed_on in (
            ("New Year", "2026-01-01"),
            ("Good Friday", "2026-04-03"),
            ("Labour Day", "2026-05-01"),
            ("Madaraka Day", "2026-06-01"),
            ("Mashujaa Day", "2026-10-20"),
            ("Jamhuri Day", "2026-12-12"),
            ("Christmas", "2026-12-25"),
            ("Boxing Day", "2026-12-26"),
        ):
            await Holiday.create({"name": name, "observed_on": observed_on})

        annual = await LeaveType.create({"name": "Annual"})
        sick = await LeaveType.create({"name": "Sick"})
        await LeaveType.create({"name": "Parental"})
        await LeavePeriod.create({"starts_on": "2026-01-01", "ends_on": "2026-12-31"})

        internal = await Customer.create({"name": "Internal"})
        harbor = await Customer.create({"name": "Harbor and Co"})
        platform = await Project.create({"customer_id": internal.id, "name": "Platform"})
        site = await Project.create({"customer_id": harbor.id, "name": "Harbor portal"})
        development = await ProjectActivity.create({"project_id": platform.id, "name": "Development"})
        await ProjectActivity.create({"project_id": platform.id, "name": "Support"})
        await ProjectActivity.create({"project_id": site.id, "name": "Design"})

        travel = await ClaimType.create({"name": "Travel"})
        meals = await ClaimType.create({"name": "Meals"})

        await LanguagePack.create(
            {
                "code": "sw",
                "name": "Swahili",
                "catalog": {"dashboard.welcome": "Karibu", "leave.annual": "Likizo ya mwaka"},
            }
        )
        hire = await OnboardingTemplate.create({"name": "New hire", "kind": "hire"})
        laptop = await OnboardingTask.create({"template_id": hire.id, "title": "Collect a laptop"})
        await OnboardingTask.create({"template_id": hire.id, "title": "Read the leave policy"})
        await Course.create({"title": "Security basics"})
        await Course.create({"title": "Giving feedback"})
        pulse = await Survey.create({"title": "March pulse", "audience": "everyone"})
        await PolicyPost.create(
            {
                "title": "Leave",
                "body": "Request annual leave in the panel. Public holidays are already excluded.",
            }
        )
        await DocumentTemplate.create(
            {
                "name": "Offer letter",
                "body": "Northwind People offers you the role described in this letter.",
            }
        )
        await ScheduledReport.create({"name": "Headcount", "cadence": "monthly"})
        await PayrollConnector.create(
            {
                "name": "Northwind Pay",
                "endpoint": "https://pay.northwind.test/hook",
                "enabled": True,
            }
        )
        preferred = await CustomField.create({"name": "Preferred name", "screen": "personal"})

        return {
            "titles": titles,
            "grades": grades,
            "statuses": statuses,
            "hq": hq,
            "coast": coast,
            "engineering": engineering,
            "people_unit": people_unit,
            "finance": finance,
            "skills": skills,
            "nationalities": nationalities,
            "reasons": reasons,
            "annual": annual,
            "sick": sick,
            "platform": platform,
            "development": development,
            "travel": travel,
            "meals": meals,
            "hire": hire,
            "laptop": laptop,
            "pulse": pulse,
            "preferred": preferred,
        }

    async def _people(self, catalog: dict[str, object]) -> dict[str, Employee]:
        titles = catalog["titles"]
        statuses = catalog["statuses"]
        nationalities = catalog["nationalities"]
        hq = catalog["hq"]
        coast = catalog["coast"]
        engineering = catalog["engineering"]
        people_unit = catalog["people_unit"]
        finance = catalog["finance"]
        rows = (
            ("ada", "0001", "Ada", "Lovelace", "ada@northwind.test", None, "Chief Executive", "Full-time", "Kenyan", hq, None, "2015-01-15", None, None),
            ("grace", "0002", "Grace", "Hopper", "grace@northwind.test", "ada", "Engineering Manager", "Full-time", "American", hq, engineering, "2018-06-01", None, None),
            ("alan", "0003", "Alan", "Turing", "alan@northwind.test", "grace", "Engineer", "Full-time", "British", hq, engineering, "2024-03-01", None, None),
            ("katherine", "0011", "Katherine", "Johnson", "katherine@northwind.test", "grace", "Engineer", "Full-time", "Kenyan", hq, engineering, "2019-04-12", None, None),
            ("margaret", "0012", "Margaret", "Hamilton", "margaret@northwind.test", "grace", "Engineer", "Full-time", "Kenyan", coast, engineering, "2021-09-01", None, None),
            ("radia", "0013", "Radia", "Perlman", "radia@northwind.test", "ada", "People Partner", "Full-time", "Kenyan", hq, people_unit, "2017-02-14", None, None),
            ("barbara", "0014", "Barbara", "Liskov", "barbara@northwind.test", "ada", "Accountant", "Full-time", "Kenyan", hq, finance, "2020-11-02", None, None),
            ("frances", "0015", "Frances", "Allen", "frances@northwind.test", "grace", "Designer", "Contract", "Kenyan", coast, engineering, "2019-10-05", None, None),
            ("hedy", "0016", "Hedy", "Lamarr", "hedy@northwind.test", "grace", "Engineer", "Intern", "Kenyan", hq, engineering, "2026-02-02", None, None),
            ("tim", "0017", "Tim", "Berners-Lee", "tim@northwind.test", "grace", "Engineer", "Full-time", "British", hq, engineering, "2016-08-01", "2025-12-15", "Resignation"),
        )
        made: dict[str, Employee] = {}
        for key, number, first, last, email, manager, title, status, nation, location, unit, joined, ended, reason in rows:
            made[key] = await Employee.create(
                {
                    "employee_number": number,
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "supervisor_id": made[manager].id if manager else None,
                    "job_title_id": titles[title].id,
                    "employment_status_id": statuses[status].id,
                    "org_unit_id": unit.id if unit is not None else None,
                    "location_id": location.id,
                    "nationality_id": nationalities[nation].id,
                    "joined_on": joined,
                    "terminated_on": ended,
                    "termination_reason_id": catalog["reasons"][reason].id if reason else None,
                }
            )
        return made

    async def _accounts(self, people: dict[str, Employee]) -> None:
        password = Hash.make("secret")
        accounts = (
            ("Ada Lovelace", "ada@northwind.test", ROLE_ADMIN, people["ada"], True, admin_grants()),
            ("Grace Hopper", "grace@northwind.test", ROLE_SUPERVISOR, people["grace"], False, supervisor_grants()),
            ("Alan Turing", "alan@northwind.test", ROLE_ESS, people["alan"], False, ess_grants()),
        )
        for name, email, role, employee, is_admin, grants in accounts:
            user = await User.create(
                {
                    "name": name,
                    "email": email,
                    "password": password,
                    "role_slug": role,
                    "employee_id": employee.id,
                    "is_admin": is_admin,
                    "grants": grants,
                    "locale": "en",
                }
            )
            await employee.update({"user_id": user.id})

    async def _operations(self, catalog: dict[str, object], people: dict[str, Employee]) -> None:
        annual = catalog["annual"]
        sick = catalog["sick"]
        grades = catalog["grades"]
        skills = catalog["skills"]
        for key, person in people.items():
            if person.terminated_on:
                continue
            days = "20" if key != "hedy" else "10"
            await LeaveEntitlement.create(
                {"employee_id": person.id, "leave_type_id": annual.id, "days": days}
            )
            await LeaveEntitlement.create(
                {"employee_id": person.id, "leave_type_id": sick.id, "days": "10"}
            )

        pay = {
            "ada": ("L4", "450000"),
            "grace": ("L3", "280000"),
            "alan": ("L2", "160000"),
            "katherine": ("L2", "175000"),
            "margaret": ("L2", "170000"),
            "radia": ("L3", "220000"),
            "barbara": ("L2", "150000"),
            "frances": ("L2", "140000"),
            "hedy": ("L1", "60000"),
        }
        for key, (grade, amount) in pay.items():
            await EmployeeSalary.create(
                {
                    "employee_id": people[key].id,
                    "pay_grade_id": grades[grade].id,
                    "amount": amount,
                    "currency": "KES",
                }
            )

        await EmployeeContact.create(
            {
                "employee_id": people["alan"].id,
                "street": "12 Riverside Drive",
                "city": "Nairobi",
                "mobile": "+254700000003",
                "work_email": "alan@northwind.test",
            }
        )
        await EmergencyContact.create(
            {
                "employee_id": people["alan"].id,
                "name": "Joan Clarke",
                "relationship": "Spouse",
                "phone": "+254700000103",
            }
        )
        await Dependent.create(
            {
                "employee_id": people["grace"].id,
                "name": "Sam Hopper",
                "relationship": "Child",
                "date_of_birth": "2012-05-20",
            }
        )
        await EmployeeSkill.create(
            {"employee_id": people["alan"].id, "skill_id": skills["Python"].id, "years": "6"}
        )
        await EmployeeSkill.create(
            {"employee_id": people["katherine"].id, "skill_id": skills["SQL"].id, "years": "12"}
        )
        await CustomFieldValue.create(
            {
                "employee_id": people["alan"].id,
                "custom_field_id": catalog["preferred"].id,
                "value": "Alan",
            }
        )

        await LeaveRequest.create(
            {
                "employee_id": people["katherine"].id,
                "leave_type_id": annual.id,
                "starts_on": "2026-03-16",
                "ends_on": "2026-03-17",
                "partial": "",
                "days": "2",
                "state": "approved",
                "comment": "School visit",
            }
        )
        await LeaveRequest.create(
            {
                "employee_id": people["barbara"].id,
                "leave_type_id": annual.id,
                "starts_on": "2026-11-23",
                "ends_on": "2026-11-27",
                "partial": "",
                "days": "5",
                "state": "pending",
                "comment": "Family travel",
            }
        )

        sheet = await Timesheet.create(
            {
                "employee_id": people["katherine"].id,
                "starts_on": "2026-03-09",
                "ends_on": "2026-03-15",
                "state": "approved",
            }
        )
        await TimesheetItem.create(
            {
                "timesheet_id": sheet.id,
                "project_id": catalog["platform"].id,
                "activity_id": catalog["development"].id,
                "worked_on": "2026-03-09",
                "hours": "8",
            }
        )
        await ClaimRequest.create(
            {
                "employee_id": people["margaret"].id,
                "claim_type_id": catalog["travel"].id,
                "amount": "8400",
                "state": "submitted",
                "note": "Mombasa to Nairobi",
            }
        )
        await ClaimRequest.create(
            {
                "employee_id": people["frances"].id,
                "claim_type_id": catalog["meals"].id,
                "amount": "1800",
                "state": "draft",
                "note": "Client workshop lunch",
            }
        )

        vacancy = await Vacancy.create(
            {
                "title": "People Partner",
                "hiring_manager_id": people["ada"].id,
                "state": "open",
            }
        )
        candidate = await Candidate.create(
            {
                "vacancy_id": vacancy.id,
                "first_name": "Lin",
                "last_name": "Okello",
                "email": "lin.okello@example.test",
                "state": "interview",
            }
        )
        await Interview.create(
            {"candidate_id": candidate.id, "name": "Panel", "scheduled_on": "2026-04-16"}
        )
        await Kpi.create({"title": "Delivery", "min_rating": "1", "max_rating": "5"})
        await Tracker.create({"employee_id": people["alan"].id, "title": "Ship the leave calendar"})
        cycle = await ReviewCycle.create(
            {"name": "2026 mid-year", "starts_on": "2026-06-01", "ends_on": "2026-06-30"}
        )
        await Review.create(
            {
                "cycle_id": cycle.id,
                "employee_id": people["alan"].id,
                "reviewer_id": people["grace"].id,
                "state": "scheduled",
                "self_rating": "",
                "supervisor_rating": "",
            }
        )

        post = await BuzzPost.create(
            {
                "employee_id": people["grace"].id,
                "body": "Harbor portal shipped to the staging site today.",
            }
        )
        await BuzzComment.create(
            {
                "post_id": post.id,
                "employee_id": people["alan"].id,
                "body": "The leave calendar is next.",
            }
        )
        await BuzzLike.create({"post_id": post.id, "employee_id": people["ada"].id})

        await OnboardingAssignment.create(
            {
                "employee_id": people["hedy"].id,
                "template_id": catalog["hire"].id,
                "state": "active",
                "completed_task_ids": [catalog["laptop"].id],
            }
        )
        await DeskRequest.create(
            {
                "employee_id": people["alan"].id,
                "kind": "access",
                "subject": "Staging database access",
                "state": "submitted",
            }
        )
        await Shift.create(
            {
                "employee_id": people["frances"].id,
                "location_id": catalog["coast"].id,
                "starts_at": "2026-10-05T09:00:00",
                "ends_at": "2026-10-05T17:00:00",
                "published": True,
            }
        )
        await DevelopmentPlan.create(
            {"employee_id": people["alan"].id, "goal": "Lead a small feature from spec to release."}
        )
        await NineBoxPlacement.create(
            {"employee_id": people["katherine"].id, "performance": 3, "potential": 2}
        )
        security = await Course.where("title", "Security basics").first()
        await CourseEnrollment.create(
            {
                "course_id": security.id,
                "employee_id": people["hedy"].id,
                "completed": False,
                "certificate_code": "",
            }
        )
        await SurveyResponse.create(
            {
                "survey_id": catalog["pulse"].id,
                "employee_id": people["alan"].id,
                "answer": "The team is clear about priorities.",
            }
        )
        await Asset.create(
            {
                "name": "Laptop",
                "serial": "NW-LT-0003",
                "employee_id": people["alan"].id,
            }
        )
        await Asset.create(
            {
                "name": "Laptop",
                "serial": "NW-LT-0016",
                "employee_id": people["hedy"].id,
            }
        )


async def _named(model: type, names: tuple[str, ...]) -> dict[str, object]:
    made = {}
    for name in names:
        made[name] = await model.create({"name": name})
    return made
