"""HR tables. Optional links are plain integers so a purge can delete in any order."""

from __future__ import annotations

from almasix.orm import Blueprint, Migration, Schema

NAME_TABLES = (
    "job_titles",
    "pay_grades",
    "employment_statuses",
    "job_categories",
    "skills",
    "education_levels",
    "license_types",
    "languages",
    "memberships",
    "nationalities",
    "termination_reasons",
    "leave_types",
    "customers",
    "claim_types",
)


def name_only(table: Blueprint) -> None:
    table.id()
    table.string("name")
    table.timestamps()


class CreateHrmTables(Migration):
    async def up(self) -> None:
        for name in NAME_TABLES:
            await Schema.create(name, name_only)
        await Schema.create("hrm_roles", self.roles)
        await Schema.create("workflow_transitions", self.workflow_transitions)
        await Schema.create("module_settings", self.module_settings)
        await Schema.create("localization_settings", self.localization_settings)
        await Schema.create("work_shifts", self.work_shifts)
        await Schema.create("locations", self.locations)
        await Schema.create("org_units", self.org_units)
        await Schema.create("email_settings", self.email_settings)
        await Schema.create("branding_settings", self.branding_settings)
        await Schema.create("oidc_providers", self.oidc_providers)
        await Schema.create("employees", self.employees)
        await Schema.create("employee_contacts", self.employee_contacts)
        await Schema.create("emergency_contacts", self.emergency_contacts)
        await Schema.create("dependents", self.dependents)
        await Schema.create("immigration_records", self.immigration_records)
        await Schema.create("employee_salaries", self.employee_salaries)
        await Schema.create("employee_skills", self.employee_skills)
        await Schema.create("custom_fields", self.custom_fields)
        await Schema.create("custom_field_values", self.custom_field_values)
        await Schema.create("work_weeks", self.work_weeks)
        await Schema.create("holidays", self.holidays)
        await Schema.create("leave_periods", self.leave_periods)
        await Schema.create("leave_entitlements", self.leave_entitlements)
        await Schema.create("leave_requests", self.leave_requests)
        await Schema.create("projects", self.projects)
        await Schema.create("project_activities", self.project_activities)
        await Schema.create("timesheets", self.timesheets)
        await Schema.create("timesheet_items", self.timesheet_items)
        await Schema.create("attendance_records", self.attendance_records)
        await Schema.create("vacancies", self.vacancies)
        await Schema.create("candidates", self.candidates)
        await Schema.create("interviews", self.interviews)
        await Schema.create("kpis", self.kpis)
        await Schema.create("trackers", self.trackers)
        await Schema.create("review_cycles", self.review_cycles)
        await Schema.create("reviews", self.reviews)
        await Schema.create("buzz_posts", self.buzz_posts)
        await Schema.create("buzz_comments", self.buzz_comments)
        await Schema.create("buzz_likes", self.buzz_likes)
        await Schema.create("claim_requests", self.claim_requests)
        await Schema.create("language_packs", self.language_packs)
        await Schema.create("onboarding_templates", self.onboarding_templates)
        await Schema.create("onboarding_tasks", self.onboarding_tasks)
        await Schema.create("onboarding_assignments", self.onboarding_assignments)
        await Schema.create("desk_requests", self.desk_requests)
        await Schema.create("shifts", self.shifts)
        await Schema.create("development_plans", self.development_plans)
        await Schema.create("nine_box_placements", self.nine_box_placements)
        await Schema.create("courses", self.courses)
        await Schema.create("course_enrollments", self.course_enrollments)
        await Schema.create("surveys", self.surveys)
        await Schema.create("survey_responses", self.survey_responses)
        await Schema.create("grievances", self.grievances)
        await Schema.create("discipline_cases", self.discipline_cases)
        await Schema.create("audit_events", self.audit_events)
        await Schema.create("assets", self.assets)
        await Schema.create("policy_posts", self.policy_posts)
        await Schema.create("document_templates", self.document_templates)
        await Schema.create("mfa_factors", self.mfa_factors)
        await Schema.create("scheduled_reports", self.scheduled_reports)
        await Schema.create("payroll_connectors", self.payroll_connectors)

    async def down(self) -> None:
        for name in (
            "payroll_connectors",
            "scheduled_reports",
            "mfa_factors",
            "document_templates",
            "policy_posts",
            "assets",
            "audit_events",
            "discipline_cases",
            "grievances",
            "survey_responses",
            "surveys",
            "course_enrollments",
            "courses",
            "nine_box_placements",
            "development_plans",
            "shifts",
            "desk_requests",
            "onboarding_assignments",
            "onboarding_tasks",
            "onboarding_templates",
            "language_packs",
            "claim_requests",
            "buzz_likes",
            "buzz_comments",
            "buzz_posts",
            "reviews",
            "review_cycles",
            "trackers",
            "kpis",
            "interviews",
            "candidates",
            "vacancies",
            "attendance_records",
            "timesheet_items",
            "timesheets",
            "project_activities",
            "projects",
            "leave_requests",
            "leave_entitlements",
            "leave_periods",
            "holidays",
            "work_weeks",
            "custom_field_values",
            "custom_fields",
            "employee_skills",
            "employee_salaries",
            "immigration_records",
            "dependents",
            "emergency_contacts",
            "employee_contacts",
            "employees",
            "oidc_providers",
            "branding_settings",
            "email_settings",
            "org_units",
            "locations",
            "work_shifts",
            "localization_settings",
            "module_settings",
            "workflow_transitions",
            "hrm_roles",
            *reversed(NAME_TABLES),
        ):
            await Schema.drop_if_exists(name)

    def roles(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("slug").unique()
        table.timestamps()

    def workflow_transitions(self, table: Blueprint) -> None:
        table.id()
        table.string("flow")
        table.string("state")
        table.string("role_slug")
        table.string("action")
        table.string("next_state")
        table.timestamps()
        table.unique(["flow", "state", "role_slug", "action"])

    def module_settings(self, table: Blueprint) -> None:
        table.id()
        table.string("key").unique()
        table.boolean("enabled").default(True)
        table.timestamps()

    def localization_settings(self, table: Blueprint) -> None:
        table.id()
        table.string("date_format").default("Y-m-d")
        table.string("language").default("en")
        table.timestamps()

    def work_shifts(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("start_time")
        table.string("end_time")
        table.timestamps()

    def locations(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("city").nullable()
        table.string("country").nullable()
        table.timestamps()

    def org_units(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.unsigned_big_integer("parent_id").nullable()
        table.timestamps()

    def email_settings(self, table: Blueprint) -> None:
        table.id()
        table.string("host")
        table.integer("port").default(587)
        table.string("username").nullable()
        table.string("from_address")
        table.timestamps()

    def branding_settings(self, table: Blueprint) -> None:
        table.id()
        table.string("brand_name")
        table.string("primary_color").default("#0f766e")
        table.timestamps()

    def oidc_providers(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("issuer")
        table.string("client_id")
        table.boolean("enabled").default(True)
        table.timestamps()

    def employees(self, table: Blueprint) -> None:
        table.id()
        table.string("employee_number").unique()
        table.string("first_name")
        table.string("last_name")
        table.string("email").unique()
        table.unsigned_big_integer("user_id").nullable()
        table.unsigned_big_integer("supervisor_id").nullable().index()
        table.unsigned_big_integer("job_title_id").nullable()
        table.unsigned_big_integer("employment_status_id").nullable()
        table.unsigned_big_integer("org_unit_id").nullable()
        table.unsigned_big_integer("location_id").nullable()
        table.unsigned_big_integer("nationality_id").nullable()
        table.date("joined_on").nullable()
        table.date("terminated_on").nullable()
        table.unsigned_big_integer("termination_reason_id").nullable()
        table.timestamps()

    def employee_contacts(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("street").nullable()
        table.string("city").nullable()
        table.string("mobile").nullable()
        table.string("work_email").nullable()
        table.timestamps()

    def emergency_contacts(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("name")
        table.string("relationship").nullable()
        table.string("phone").nullable()
        table.timestamps()

    def dependents(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("name")
        table.string("relationship").nullable()
        table.date("date_of_birth").nullable()
        table.timestamps()

    def immigration_records(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("document_type")
        table.string("number")
        table.date("expires_on").nullable()
        table.timestamps()

    def employee_salaries(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("pay_grade_id").nullable()
        table.string("amount")
        table.string("currency").default("USD")
        table.timestamps()

    def employee_skills(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("skill_id")
        table.integer("years").default(0)
        table.timestamps()

    def custom_fields(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("screen").default("personal")
        table.timestamps()

    def custom_field_values(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("custom_field_id")
        table.string("value")
        table.timestamps()

    def work_weeks(self, table: Blueprint) -> None:
        table.id()
        for day in (
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ):
            table.boolean(day).default(day not in {"saturday", "sunday"})
        table.timestamps()

    def holidays(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.date("observed_on")
        table.timestamps()

    def leave_periods(self, table: Blueprint) -> None:
        table.id()
        table.date("starts_on")
        table.date("ends_on")
        table.timestamps()

    def leave_entitlements(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("leave_type_id")
        table.string("days")
        table.timestamps()

    def leave_requests(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("leave_type_id")
        table.date("starts_on")
        table.date("ends_on")
        table.string("partial").default("full")
        table.string("days")
        table.string("state").default("pending")
        table.text("comment").nullable()
        table.timestamps()

    def projects(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("customer_id")
        table.string("name")
        table.timestamps()

    def project_activities(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("project_id")
        table.string("name")
        table.timestamps()

    def timesheets(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.date("starts_on")
        table.date("ends_on")
        table.string("state").default("open")
        table.timestamps()

    def timesheet_items(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("timesheet_id")
        table.unsigned_big_integer("project_id")
        table.unsigned_big_integer("activity_id").nullable()
        table.date("worked_on")
        table.string("hours")
        table.timestamps()

    def attendance_records(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("punched_at")
        table.string("kind")
        table.string("state").default("open")
        table.timestamps()

    def vacancies(self, table: Blueprint) -> None:
        table.id()
        table.string("title")
        table.unsigned_big_integer("hiring_manager_id").nullable()
        table.string("state").default("open")
        table.timestamps()

    def candidates(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("vacancy_id")
        table.string("first_name")
        table.string("last_name")
        table.string("email")
        table.string("state").default("applied")
        table.unsigned_big_integer("employee_id").nullable()
        table.timestamps()

    def interviews(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("candidate_id")
        table.string("name")
        table.date("scheduled_on")
        table.timestamps()

    def kpis(self, table: Blueprint) -> None:
        table.id()
        table.string("title")
        table.integer("min_rating").default(1)
        table.integer("max_rating").default(5)
        table.timestamps()

    def trackers(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("title")
        table.timestamps()

    def review_cycles(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.date("starts_on")
        table.date("ends_on")
        table.timestamps()

    def reviews(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("cycle_id")
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("reviewer_id")
        table.string("state").default("scheduled")
        table.integer("self_rating").nullable()
        table.integer("supervisor_rating").nullable()
        table.timestamps()

    def buzz_posts(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.text("body")
        table.timestamps()

    def buzz_comments(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("post_id")
        table.unsigned_big_integer("employee_id")
        table.text("body")
        table.timestamps()

    def buzz_likes(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("post_id")
        table.unsigned_big_integer("employee_id")
        table.timestamps()
        table.unique(["post_id", "employee_id"])

    def claim_requests(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("claim_type_id")
        table.string("amount")
        table.string("state").default("draft")
        table.text("note").nullable()
        table.timestamps()

    def language_packs(self, table: Blueprint) -> None:
        table.id()
        table.string("code")
        table.string("name")
        table.json("catalog")
        table.timestamps()

    def onboarding_templates(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("kind").default("onboarding")
        table.timestamps()

    def onboarding_tasks(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("template_id")
        table.string("title")
        table.timestamps()

    def onboarding_assignments(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("template_id")
        table.string("state").default("pending")
        table.json("completed_task_ids").nullable()
        table.timestamps()

    def desk_requests(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("kind")
        table.string("subject")
        table.string("state").default("open")
        table.timestamps()

    def shifts(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id").nullable()
        table.unsigned_big_integer("location_id").nullable()
        table.string("starts_at")
        table.string("ends_at")
        table.boolean("published").default(False)
        table.timestamps()

    def development_plans(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.text("goal")
        table.timestamps()

    def nine_box_placements(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.integer("performance")
        table.integer("potential")
        table.timestamps()

    def courses(self, table: Blueprint) -> None:
        table.id()
        table.string("title")
        table.timestamps()

    def course_enrollments(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("course_id")
        table.unsigned_big_integer("employee_id")
        table.boolean("completed").default(False)
        table.string("certificate_code").nullable()
        table.timestamps()
        table.unique(["course_id", "employee_id"])

    def surveys(self, table: Blueprint) -> None:
        table.id()
        table.string("title")
        table.string("audience").default("everyone")
        table.timestamps()

    def survey_responses(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("survey_id")
        table.unsigned_big_integer("employee_id")
        table.text("answer")
        table.timestamps()
        table.unique(["survey_id", "employee_id"])

    def grievances(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.string("kind")
        table.text("body")
        table.string("state").default("open")
        table.timestamps()

    def discipline_cases(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("employee_id")
        table.unsigned_big_integer("investigator_id").nullable()
        table.text("summary")
        table.string("state").default("open")
        table.timestamps()

    def audit_events(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("actor_id").nullable()
        table.string("action")
        table.string("subject")
        table.timestamps()

    def assets(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("serial").nullable()
        table.unsigned_big_integer("employee_id").nullable()
        table.timestamps()

    def policy_posts(self, table: Blueprint) -> None:
        table.id()
        table.string("title")
        table.text("body")
        table.timestamps()

    def document_templates(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.text("body")
        table.timestamps()

    def mfa_factors(self, table: Blueprint) -> None:
        table.id()
        table.unsigned_big_integer("user_id")
        table.string("kind")
        table.string("secret")
        table.boolean("confirmed").default(False)
        table.timestamps()

    def scheduled_reports(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("cadence")
        table.timestamps()

    def payroll_connectors(self, table: Blueprint) -> None:
        table.id()
        table.string("name")
        table.string("endpoint")
        table.boolean("enabled").default(False)
        table.timestamps()
