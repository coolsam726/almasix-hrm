"""Employee profile sections."""

from app.models.hrm import (
    CustomField,
    Dependent,
    EmergencyContact,
    Employee,
    EmployeeContact,
    EmployeeSalary,
    EmployeeSkill,
    ImmigrationRecord,
)
from app.orbit.hrm.resources.factory import crud

EmployeeResource = crud(
    "EmployeeResource",
    model=Employee,
    label="Employees",
    group="People",
    data_group="pim",
    icon="heroicon-o-users",
    sort=1,
    fields=("employee_number", "first_name", "last_name", "email", "joined_on"),
)
EmployeeContactResource = crud(
    "EmployeeContactResource",
    model=EmployeeContact,
    label="Contacts",
    group="People",
    data_group="pim",
    icon="heroicon-o-phone",
    sort=2,
    fields=("employee_id", "city", "mobile", "work_email"),
)
EmergencyContactResource = crud(
    "EmergencyContactResource",
    model=EmergencyContact,
    label="Emergency contacts",
    group="People",
    data_group="pim",
    icon="heroicon-o-heart",
    sort=3,
    fields=("employee_id", "name", "relationship", "phone"),
)
DependentResource = crud(
    "DependentResource",
    model=Dependent,
    label="Dependents",
    group="People",
    data_group="pim",
    icon="heroicon-o-user",
    sort=4,
    fields=("employee_id", "name", "relationship", "date_of_birth"),
)
ImmigrationRecordResource = crud(
    "ImmigrationRecordResource",
    model=ImmigrationRecord,
    label="Immigration",
    group="People",
    data_group="pim",
    icon="heroicon-o-identification",
    sort=5,
    fields=("employee_id", "document_type", "number", "expires_on"),
)
EmployeeSalaryResource = crud(
    "EmployeeSalaryResource",
    model=EmployeeSalary,
    label="Salaries",
    group="People",
    data_group="payroll",
    icon="heroicon-o-banknotes",
    sort=6,
    fields=("employee_id", "amount", "currency"),
)
EmployeeSkillResource = crud(
    "EmployeeSkillResource",
    model=EmployeeSkill,
    label="Employee skills",
    group="People",
    data_group="pim",
    icon="heroicon-o-academic-cap",
    sort=7,
    fields=("employee_id", "skill_id", "years"),
)
CustomFieldResource = crud(
    "CustomFieldResource",
    model=CustomField,
    label="Custom fields",
    group="People",
    data_group="pim",
    icon="heroicon-o-adjustments-horizontal",
    sort=8,
    fields=("name", "screen"),
)
