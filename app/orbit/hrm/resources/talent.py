"""Hiring and reviews."""

from app.models.hrm import (
    Candidate,
    Interview,
    Kpi,
    Review,
    ReviewCycle,
    Tracker,
    Vacancy,
)
from app.orbit.hrm.resources.factory import crud

VacancyResource = crud(
    "VacancyResource",
    model=Vacancy,
    label="Vacancies",
    group="Recruitment",
    subgroup="",
    data_group="recruitment",
    icon="heroicon-o-megaphone",
    sort=1,
    fields=("title", "state"),
)
CandidateResource = crud(
    "CandidateResource",
    model=Candidate,
    label="Candidates",
    group="Recruitment",
    subgroup="",
    data_group="recruitment",
    icon="heroicon-o-user-plus",
    sort=2,
    fields=("first_name", "last_name", "email", "state"),
    mutable=False,
)
InterviewResource = crud(
    "InterviewResource",
    model=Interview,
    label="Interviews",
    group="Recruitment",
    subgroup="",
    data_group="recruitment",
    icon="heroicon-o-chat-bubble-left-right",
    sort=3,
    fields=("candidate_id", "name", "scheduled_on"),
)
KpiResource = crud(
    "KpiResource",
    model=Kpi,
    label="KPIs",
    group="Performance",
    subgroup="Configure",
    data_group="performance",
    modal=True,
    icon="heroicon-o-chart-bar",
    sort=4,
    fields=("title", "min_rating", "max_rating"),
)
TrackerResource = crud(
    "TrackerResource",
    model=Tracker,
    label="Trackers",
    group="Performance",
    subgroup="Configure",
    data_group="performance",
    icon="heroicon-o-flag",
    sort=5,
    fields=("employee_id", "title"),
)
ReviewCycleResource = crud(
    "ReviewCycleResource",
    model=ReviewCycle,
    label="Review cycles",
    group="Performance",
    subgroup="Configure",
    data_group="performance",
    modal=True,
    icon="heroicon-o-arrow-path",
    sort=6,
    fields=("name", "starts_on", "ends_on"),
)
ReviewResource = crud(
    "ReviewResource",
    model=Review,
    label="Reviews",
    group="Performance",
    subgroup="Manage reviews",
    data_group="performance",
    icon="heroicon-o-clipboard-document-check",
    sort=7,
    fields=("employee_id", "state", "self_rating", "supervisor_rating"),
    mutable=False,
)
