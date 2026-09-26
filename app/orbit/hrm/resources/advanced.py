"""Advanced modules. Each screen follows the spec in docs/advanced."""

from app.models.hrm import (
    Asset,
    Course,
    CourseEnrollment,
    DeskRequest,
    DevelopmentPlan,
    DisciplineCase,
    DocumentTemplate,
    Grievance,
    MfaFactor,
    NineBoxPlacement,
    OnboardingAssignment,
    OnboardingTemplate,
    PayrollConnector,
    PolicyPost,
    ScheduledReport,
    Shift,
    Survey,
)
from app.orbit.hrm.resources.factory import crud

OnboardingTemplateResource = crud(
    "OnboardingTemplateResource",
    model=OnboardingTemplate,
    label="Onboarding templates",
    group="Advanced",
    data_group="onboarding",
    icon="heroicon-o-clipboard-document-list",
    sort=1,
    fields=("name", "kind"),
)
OnboardingAssignmentResource = crud(
    "OnboardingAssignmentResource",
    model=OnboardingAssignment,
    label="Onboarding",
    group="Advanced",
    data_group="onboarding",
    icon="heroicon-o-check-circle",
    sort=2,
    fields=("employee_id", "state"),
    mutable=False,
)
DeskRequestResource = crud(
    "DeskRequestResource",
    model=DeskRequest,
    label="Request desk",
    group="Advanced",
    data_group="desk",
    icon="heroicon-o-inbox",
    sort=3,
    fields=("employee_id", "kind", "subject", "state"),
    mutable=False,
)
ShiftResource = crud(
    "ShiftResource",
    model=Shift,
    label="Shifts",
    group="Advanced",
    data_group="roster",
    icon="heroicon-o-calendar",
    sort=4,
    fields=("employee_id", "location_id", "starts_at", "ends_at"),
)
DevelopmentPlanResource = crud(
    "DevelopmentPlanResource",
    model=DevelopmentPlan,
    label="Development plans",
    group="Advanced",
    data_group="career",
    icon="heroicon-o-map",
    sort=5,
    fields=("employee_id", "goal"),
)
NineBoxPlacementResource = crud(
    "NineBoxPlacementResource",
    model=NineBoxPlacement,
    label="9-box",
    group="Advanced",
    data_group="career",
    icon="heroicon-o-squares-2x2",
    sort=6,
    fields=("employee_id", "performance", "potential"),
    mutable=False,
)
CourseResource = crud(
    "CourseResource",
    model=Course,
    label="Courses",
    group="Advanced",
    data_group="training",
    icon="heroicon-o-academic-cap",
    sort=7,
    fields=("title",),
)
CourseEnrollmentResource = crud(
    "CourseEnrollmentResource",
    model=CourseEnrollment,
    label="Enrollments",
    group="Advanced",
    data_group="training",
    icon="heroicon-o-ticket",
    sort=8,
    fields=("course_id", "employee_id", "certificate_code"),
    mutable=False,
)
SurveyResource = crud(
    "SurveyResource",
    model=Survey,
    label="Surveys",
    group="Advanced",
    data_group="surveys",
    icon="heroicon-o-chart-pie",
    sort=9,
    fields=("title", "audience"),
)
GrievanceResource = crud(
    "GrievanceResource",
    model=Grievance,
    label="Employee voice",
    group="Advanced",
    data_group="voice",
    icon="heroicon-o-megaphone",
    sort=10,
    fields=("employee_id", "kind", "state"),
    mutable=False,
)
DisciplineCaseResource = crud(
    "DisciplineCaseResource",
    model=DisciplineCase,
    label="Discipline",
    group="Advanced",
    data_group="discipline",
    icon="heroicon-o-scale",
    sort=11,
    fields=("employee_id", "summary", "state"),
    mutable=False,
)
AssetResource = crud(
    "AssetResource",
    model=Asset,
    label="Assets",
    group="Advanced",
    data_group="assets",
    icon="heroicon-o-computer-desktop",
    sort=12,
    fields=("name", "serial", "employee_id"),
)
PolicyPostResource = crud(
    "PolicyPostResource",
    model=PolicyPost,
    label="Policies",
    group="Advanced",
    data_group="policies",
    icon="heroicon-o-newspaper",
    sort=13,
    fields=("title", "body"),
)
DocumentTemplateResource = crud(
    "DocumentTemplateResource",
    model=DocumentTemplate,
    label="Document templates",
    group="Advanced",
    data_group="documents",
    icon="heroicon-o-document-text",
    sort=14,
    fields=("name", "body"),
)
MfaFactorResource = crud(
    "MfaFactorResource",
    model=MfaFactor,
    label="Authenticators",
    group="Advanced",
    data_group="admin",
    icon="heroicon-o-device-phone-mobile",
    sort=15,
    fields=("user_id", "kind"),
    mutable=False,
)
ScheduledReportResource = crud(
    "ScheduledReportResource",
    model=ScheduledReport,
    label="Scheduled reports",
    group="Advanced",
    data_group="reports",
    icon="heroicon-o-document-chart-bar",
    sort=16,
    fields=("name", "cadence"),
)
PayrollConnectorResource = crud(
    "PayrollConnectorResource",
    model=PayrollConnector,
    label="Payroll connectors",
    group="Advanced",
    data_group="payroll",
    icon="heroicon-o-link",
    sort=17,
    fields=("name", "endpoint"),
)
