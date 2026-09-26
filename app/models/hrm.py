"""HR records. Each class maps one table and lists the columns mass assignment may set."""

from __future__ import annotations

from almasix.orm import Model


class Role(Model):
    table = "hrm_roles"
    fillable = ("name", "slug")


class WorkflowTransition(Model):
    table = "workflow_transitions"
    fillable = ("flow", "state", "role_slug", "action", "next_state")


class ModuleSetting(Model):
    table = "module_settings"
    fillable = ("key", "enabled")
    casts = {"enabled": "bool"}


class LocalizationSetting(Model):
    table = "localization_settings"
    fillable = ("date_format", "language")


class JobTitle(Model):
    table = "job_titles"
    fillable = ("name",)


class PayGrade(Model):
    table = "pay_grades"
    fillable = ("name",)


class EmploymentStatus(Model):
    table = "employment_statuses"
    fillable = ("name",)


class JobCategory(Model):
    table = "job_categories"
    fillable = ("name",)


class WorkShift(Model):
    table = "work_shifts"
    fillable = ("name", "start_time", "end_time")


class Location(Model):
    table = "locations"
    fillable = ("name", "city", "country")


class OrgUnit(Model):
    table = "org_units"
    fillable = ("name", "parent_id")


class Skill(Model):
    table = "skills"
    fillable = ("name",)


class EducationLevel(Model):
    table = "education_levels"
    fillable = ("name",)


class LicenseType(Model):
    table = "license_types"
    fillable = ("name",)


class Language(Model):
    table = "languages"
    fillable = ("name",)


class Membership(Model):
    table = "memberships"
    fillable = ("name",)


class Nationality(Model):
    table = "nationalities"
    fillable = ("name",)


class EmailSetting(Model):
    table = "email_settings"
    fillable = ("host", "port", "username", "from_address")


class BrandingSetting(Model):
    table = "branding_settings"
    fillable = ("brand_name", "primary_color")


class OidcProvider(Model):
    table = "oidc_providers"
    fillable = ("name", "issuer", "client_id", "enabled")
    casts = {"enabled": "bool"}


class TerminationReason(Model):
    table = "termination_reasons"
    fillable = ("name",)


class Employee(Model):
    table = "employees"
    fillable = (
        "employee_number",
        "first_name",
        "last_name",
        "email",
        "user_id",
        "supervisor_id",
        "job_title_id",
        "employment_status_id",
        "org_unit_id",
        "location_id",
        "nationality_id",
        "joined_on",
        "terminated_on",
        "termination_reason_id",
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class EmployeeContact(Model):
    table = "employee_contacts"
    fillable = ("employee_id", "street", "city", "mobile", "work_email")


class EmergencyContact(Model):
    table = "emergency_contacts"
    fillable = ("employee_id", "name", "relationship", "phone")


class Dependent(Model):
    table = "dependents"
    fillable = ("employee_id", "name", "relationship", "date_of_birth")


class ImmigrationRecord(Model):
    table = "immigration_records"
    fillable = ("employee_id", "document_type", "number", "expires_on")


class EmployeeSalary(Model):
    table = "employee_salaries"
    fillable = ("employee_id", "pay_grade_id", "amount", "currency")


class EmployeeSkill(Model):
    table = "employee_skills"
    fillable = ("employee_id", "skill_id", "years")


class CustomField(Model):
    table = "custom_fields"
    fillable = ("name", "screen")


class CustomFieldValue(Model):
    table = "custom_field_values"
    fillable = ("employee_id", "custom_field_id", "value")


class LeaveType(Model):
    table = "leave_types"
    fillable = ("name",)


class WorkWeek(Model):
    table = "work_weeks"
    fillable = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )
    casts = {day: "bool" for day in fillable}


class Holiday(Model):
    table = "holidays"
    fillable = ("name", "observed_on")


class LeavePeriod(Model):
    table = "leave_periods"
    fillable = ("starts_on", "ends_on")


class LeaveEntitlement(Model):
    table = "leave_entitlements"
    fillable = ("employee_id", "leave_type_id", "days")


class LeaveRequest(Model):
    table = "leave_requests"
    fillable = (
        "employee_id",
        "leave_type_id",
        "starts_on",
        "ends_on",
        "partial",
        "days",
        "state",
        "comment",
    )


class Customer(Model):
    table = "customers"
    fillable = ("name",)


class Project(Model):
    table = "projects"
    fillable = ("customer_id", "name")


class ProjectActivity(Model):
    table = "project_activities"
    fillable = ("project_id", "name")


class Timesheet(Model):
    table = "timesheets"
    fillable = ("employee_id", "starts_on", "ends_on", "state")


class TimesheetItem(Model):
    table = "timesheet_items"
    fillable = ("timesheet_id", "project_id", "activity_id", "worked_on", "hours")


class AttendanceRecord(Model):
    table = "attendance_records"
    fillable = ("employee_id", "punched_at", "kind", "state")


class Vacancy(Model):
    table = "vacancies"
    fillable = ("title", "hiring_manager_id", "state")


class Candidate(Model):
    table = "candidates"
    fillable = (
        "vacancy_id",
        "first_name",
        "last_name",
        "email",
        "state",
        "employee_id",
    )


class Interview(Model):
    table = "interviews"
    fillable = ("candidate_id", "name", "scheduled_on")


class Kpi(Model):
    table = "kpis"
    fillable = ("title", "min_rating", "max_rating")


class Tracker(Model):
    table = "trackers"
    fillable = ("employee_id", "title")


class ReviewCycle(Model):
    table = "review_cycles"
    fillable = ("name", "starts_on", "ends_on")


class Review(Model):
    table = "reviews"
    fillable = (
        "cycle_id",
        "employee_id",
        "reviewer_id",
        "state",
        "self_rating",
        "supervisor_rating",
    )


class BuzzPost(Model):
    table = "buzz_posts"
    fillable = ("employee_id", "body")


class BuzzComment(Model):
    table = "buzz_comments"
    fillable = ("post_id", "employee_id", "body")


class BuzzLike(Model):
    table = "buzz_likes"
    fillable = ("post_id", "employee_id")


class ClaimType(Model):
    table = "claim_types"
    fillable = ("name",)


class ClaimRequest(Model):
    table = "claim_requests"
    fillable = ("employee_id", "claim_type_id", "amount", "state", "note")


class LanguagePack(Model):
    table = "language_packs"
    fillable = ("code", "name", "catalog")
    casts = {"catalog": "json"}


class OnboardingTemplate(Model):
    table = "onboarding_templates"
    fillable = ("name", "kind")


class OnboardingTask(Model):
    table = "onboarding_tasks"
    fillable = ("template_id", "title")


class OnboardingAssignment(Model):
    table = "onboarding_assignments"
    fillable = ("employee_id", "template_id", "state", "completed_task_ids")
    casts = {"completed_task_ids": "json"}


class DeskRequest(Model):
    table = "desk_requests"
    fillable = ("employee_id", "kind", "subject", "state")


class Shift(Model):
    table = "shifts"
    fillable = ("employee_id", "location_id", "starts_at", "ends_at", "published")
    casts = {"published": "bool"}


class DevelopmentPlan(Model):
    table = "development_plans"
    fillable = ("employee_id", "goal")


class NineBoxPlacement(Model):
    table = "nine_box_placements"
    fillable = ("employee_id", "performance", "potential")


class Course(Model):
    table = "courses"
    fillable = ("title",)


class CourseEnrollment(Model):
    table = "course_enrollments"
    fillable = ("course_id", "employee_id", "completed", "certificate_code")
    casts = {"completed": "bool"}


class Survey(Model):
    table = "surveys"
    fillable = ("title", "audience")


class SurveyResponse(Model):
    table = "survey_responses"
    fillable = ("survey_id", "employee_id", "answer")


class Grievance(Model):
    table = "grievances"
    fillable = ("employee_id", "kind", "body", "state")


class DisciplineCase(Model):
    table = "discipline_cases"
    fillable = ("employee_id", "investigator_id", "summary", "state")


class AuditEvent(Model):
    table = "audit_events"
    fillable = ("actor_id", "action", "subject")


class Asset(Model):
    table = "assets"
    fillable = ("name", "serial", "employee_id")


class PolicyPost(Model):
    table = "policy_posts"
    fillable = ("title", "body")


class DocumentTemplate(Model):
    table = "document_templates"
    fillable = ("name", "body")


class MfaFactor(Model):
    table = "mfa_factors"
    fillable = ("user_id", "kind", "secret", "confirmed")
    casts = {"confirmed": "bool"}


class ScheduledReport(Model):
    table = "scheduled_reports"
    fillable = ("name", "cadence")


class PayrollConnector(Model):
    table = "payroll_connectors"
    fillable = ("name", "endpoint", "enabled")
    casts = {"enabled": "bool"}
