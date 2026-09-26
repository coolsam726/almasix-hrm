"""Leave and time records. Requests and timesheets are edited through the domain API."""

from app.models.hrm import (
    AttendanceRecord,
    Customer,
    Holiday,
    LeaveEntitlement,
    LeavePeriod,
    LeaveRequest,
    LeaveType,
    Project,
    ProjectActivity,
    Timesheet,
    WorkWeek,
)
from app.orbit.hrm.resources.factory import crud

LeaveTypeResource = crud(
    "LeaveTypeResource",
    model=LeaveType,
    label="Leave types",
    group="Leave",
    data_group="leave",
    icon="heroicon-o-tag",
    sort=1,
    fields=("name",),
)
WorkWeekResource = crud(
    "WorkWeekResource",
    model=WorkWeek,
    label="Work week",
    group="Leave",
    data_group="admin",
    icon="heroicon-o-calendar-days",
    sort=2,
    fields=("monday", "tuesday", "wednesday", "thursday", "friday"),
)
HolidayResource = crud(
    "HolidayResource",
    model=Holiday,
    label="Holidays",
    group="Leave",
    data_group="leave",
    icon="heroicon-o-sun",
    sort=3,
    fields=("name", "observed_on"),
)
LeavePeriodResource = crud(
    "LeavePeriodResource",
    model=LeavePeriod,
    label="Leave periods",
    group="Leave",
    data_group="leave",
    icon="heroicon-o-calendar",
    sort=4,
    fields=("starts_on", "ends_on"),
)
LeaveEntitlementResource = crud(
    "LeaveEntitlementResource",
    model=LeaveEntitlement,
    label="Entitlements",
    group="Leave",
    data_group="leave",
    icon="heroicon-o-calculator",
    sort=5,
    fields=("employee_id", "leave_type_id", "days"),
)
LeaveRequestResource = crud(
    "LeaveRequestResource",
    model=LeaveRequest,
    label="Leave requests",
    group="Leave",
    data_group="leave",
    icon="heroicon-o-paper-airplane",
    sort=6,
    fields=("employee_id", "starts_on", "ends_on", "days", "state"),
    mutable=False,
)
CustomerResource = crud(
    "CustomerResource",
    model=Customer,
    label="Customers",
    group="Time",
    data_group="time",
    icon="heroicon-o-building-storefront",
    sort=1,
    fields=("name",),
)
ProjectResource = crud(
    "ProjectResource",
    model=Project,
    label="Projects",
    group="Time",
    data_group="time",
    icon="heroicon-o-folder",
    sort=2,
    fields=("customer_id", "name"),
)
ProjectActivityResource = crud(
    "ProjectActivityResource",
    model=ProjectActivity,
    label="Activities",
    group="Time",
    data_group="time",
    icon="heroicon-o-list-bullet",
    sort=3,
    fields=("project_id", "name"),
)
TimesheetResource = crud(
    "TimesheetResource",
    model=Timesheet,
    label="Timesheets",
    group="Time",
    data_group="time",
    icon="heroicon-o-table-cells",
    sort=4,
    fields=("employee_id", "starts_on", "ends_on", "state"),
    mutable=False,
)
AttendanceRecordResource = crud(
    "AttendanceRecordResource",
    model=AttendanceRecord,
    label="Attendance",
    group="Time",
    data_group="time",
    icon="heroicon-o-finger-print",
    sort=5,
    fields=("employee_id", "punched_at", "kind", "state"),
    mutable=False,
)
