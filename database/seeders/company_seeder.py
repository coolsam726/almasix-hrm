"""Northwind People — three employees, roles, and the default workflows."""

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
    BrandingSetting,
    ClaimType,
    Customer,
    Employee,
    Holiday,
    JobTitle,
    LeaveEntitlement,
    LeavePeriod,
    LeaveType,
    LocalizationSetting,
    Location,
    ModuleSetting,
    Project,
    Role,
    WorkflowTransition,
    WorkWeek,
)
from app.models.user import User


class CompanySeeder(Seeder):
    async def run(self) -> None:
        if await User.where("email", "ada@northwind.test").first():
            return

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
        await Holiday.create({"name": "New Year", "observed_on": "2026-01-01"})
        title = await JobTitle.create({"name": "Engineer"})
        location = await Location.create(
            {"name": "Headquarters", "city": "Nairobi", "country": "Kenya"}
        )
        annual = await LeaveType.create({"name": "Annual"})
        await LeavePeriod.create({"starts_on": "2026-01-01", "ends_on": "2026-12-31"})
        customer = await Customer.create({"name": "Internal"})
        await Project.create({"customer_id": customer.id, "name": "Platform"})
        await ClaimType.create({"name": "Travel"})

        ada = await Employee.create(
            {
                "employee_number": "0001",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@northwind.test",
                "job_title_id": title.id,
                "location_id": location.id,
                "joined_on": "2015-01-15",
            }
        )
        grace = await Employee.create(
            {
                "employee_number": "0002",
                "first_name": "Grace",
                "last_name": "Hopper",
                "email": "grace@northwind.test",
                "supervisor_id": ada.id,
                "job_title_id": title.id,
                "location_id": location.id,
                "joined_on": "2018-06-01",
            }
        )
        alan = await Employee.create(
            {
                "employee_number": "0003",
                "first_name": "Alan",
                "last_name": "Turing",
                "email": "alan@northwind.test",
                "supervisor_id": grace.id,
                "job_title_id": title.id,
                "location_id": location.id,
                "joined_on": "2024-03-01",
            }
        )

        password = Hash.make("secret")
        accounts = (
            ("Ada Lovelace", "ada@northwind.test", ROLE_ADMIN, ada, True, admin_grants()),
            ("Grace Hopper", "grace@northwind.test", ROLE_SUPERVISOR, grace, False, supervisor_grants()),
            ("Alan Turing", "alan@northwind.test", ROLE_ESS, alan, False, ess_grants()),
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

        for employee in (ada, grace, alan):
            await LeaveEntitlement.create(
                {"employee_id": employee.id, "leave_type_id": annual.id, "days": "20"}
            )
