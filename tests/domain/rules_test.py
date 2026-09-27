"""Rules that do not need a database."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.domain.access import employee_in_scope, user_can_read
from app.domain.advanced import can_publish_shift, nine_box_cell, payroll_export, valid_cadence
from app.domain.assistant import answer
from app.domain.catalog import admin_grants, ess_grants, supervisor_grants
from app.domain.i18n import authorize_url, parse_xliff
from app.domain.leave import count_leave_days, summarize
from app.domain.mfa import confirm_totp, totp
from app.domain.people import (
    directory_rows,
    next_employee_number,
    org_tree,
    parse_employee_csv,
    subordinate_set,
    upcoming_anniversaries,
)
from app.domain.timekeeping import next_punch, validate_hours
from app.domain.workflow import IllegalTransition, resolve_transition


class Actor:
    def __init__(self, *, is_admin: bool = False, grants: dict | None = None, employee_id: int = 1):
        self.is_admin = is_admin
        self.grants = grants or {}
        self.employee_id = employee_id


WEEK = {
    "monday": True,
    "tuesday": True,
    "wednesday": True,
    "thursday": True,
    "friday": True,
    "saturday": False,
    "sunday": False,
}


class RulesTest:
    def test_scopes_follow_the_role(self) -> None:
        admin = Actor(is_admin=True, grants=admin_grants(), employee_id=1)
        supervisor = Actor(grants=supervisor_grants(), employee_id=2)
        ess = Actor(grants=ess_grants(), employee_id=3)
        reports = {3}

        assert user_can_read(admin, "admin")
        assert not user_can_read(ess, "admin")
        assert not user_can_read(admin, "leave", modules={"leave": False})
        assert user_can_read(admin, "admin", modules={"leave": False})
        assert employee_in_scope(ess, "leave", 3, set(), write=True)
        assert not employee_in_scope(ess, "leave", 2, set(), write=True)
        assert employee_in_scope(supervisor, "leave", 3, reports, write=True)
        assert not employee_in_scope(supervisor, "pim", 1, reports, write=True)
        assert employee_in_scope(ess, "directory", 1, set())

    def test_leave_days_skip_weekends_holidays_and_count_halves(self) -> None:
        monday = date(2026, 1, 5)
        friday = date(2026, 1, 9)
        assert count_leave_days(monday, friday, WEEK, set()) == Decimal("5")
        assert count_leave_days(monday, friday, WEEK, {friday}) == Decimal("4")
        assert count_leave_days(friday, friday, WEEK, {friday}, partial="half") == Decimal("0")
        assert count_leave_days(monday, monday, WEEK, set(), partial="half_morning") == Decimal("0.5")
        used, pending, remaining = summarize(
            Decimal("20"),
            [("approved", Decimal("2")), ("pending", Decimal("1"))],
        )
        assert (used, pending, remaining) == (Decimal("2"), Decimal("1"), Decimal("17"))

    def test_illegal_workflow_and_punch_order(self) -> None:
        rows = [
            {
                "flow": "leave",
                "state": "pending",
                "role_slug": "supervisor",
                "action": "approve",
                "next_state": "approved",
            }
        ]
        assert (
            resolve_transition(rows, flow="leave", state="pending", role="supervisor", action="approve")
            == "approved"
        )
        try:
            resolve_transition(rows, flow="leave", state="pending", role="ess", action="approve")
            raise AssertionError("expected an illegal transition")
        except IllegalTransition:
            pass
        assert next_punch([], "in") == "in"
        try:
            next_punch(["in"], "in")
            raise AssertionError("expected a rejected punch")
        except ValueError:
            pass
        try:
            validate_hours(Decimal("25"))
            raise AssertionError("expected hours to be rejected")
        except ValueError:
            pass

    def test_people_helpers(self) -> None:
        assert subordinate_set([(2, 1), (3, 2), (4, 1)], 1) == {2, 3, 4}
        assert next_employee_number(["0001", "0008"]) == "0009"
        tree = org_tree(
            [
                {"id": 1, "name": "Ada", "supervisor_id": None},
                {"id": 2, "name": "Grace", "supervisor_id": 1},
            ]
        )
        assert tree[0]["reports"][0]["name"] == "Grace"
        listed = directory_rows(
            [
                {"id": 1, "name": "Ada", "job_title": "Engineer", "location": "Nairobi"},
                {
                    "id": 2,
                    "name": "Gone",
                    "job_title": "Engineer",
                    "location": "Nairobi",
                    "terminated_on": "2026-01-01",
                },
            ]
        )
        assert [row["name"] for row in listed] == ["Ada"]
        anniversaries = upcoming_anniversaries(
            [{"id": 1, "name": "Ada", "joined_on": date(2015, 1, 20), "terminated_on": None}],
            date(2026, 1, 10),
        )
        assert anniversaries[0]["on"] == "2026-01-20"
        imported = parse_employee_csv(
            "first_name,last_name,email,employee_number\nLin,Chen,lin@northwind.test,0004\n"
        )
        assert imported[0]["email"] == "lin@northwind.test"

    def test_xliff_oidc_and_assistant_limits(self) -> None:
        language, catalog = parse_xliff(
            """<?xml version="1.0"?>
            <xliff>
              <file source-language="en" target-language="fr">
                <body><trans-unit id="hello"><source>Hello</source><target>Bonjour</target></trans-unit></body>
              </file>
            </xliff>"""
        )
        assert language == "fr"
        assert catalog["hello"] == "Bonjour"
        url = authorize_url(
            issuer="https://login.example.com",
            client_id="hrm",
            redirect_uri="https://hr.example.com/callback",
            state="abc",
        )
        assert url.startswith("https://login.example.com/authorize?")
        ess = Actor(grants=ess_grants(), employee_id=3)
        assert answer("please delete this employee", ess, {}).refused
        assert answer("what is the salary?", ess, {"payroll_summary": "hidden"}).refused
        headcount = answer("how many people?", ess, {"headcount": 3})
        assert headcount.text == "Active headcount: 3."
        assert not headcount.refused

    def test_advanced_rules_and_totp(self) -> None:
        assert not can_publish_shift(
            employee_id=None,
            location_id=1,
            starts_at="2026-01-05T09:00:00",
            ends_at="2026-01-05T17:00:00",
        )
        assert can_publish_shift(
            employee_id=3,
            location_id=1,
            starts_at="2026-01-05T09:00:00",
            ends_at="2026-01-05T17:00:00",
        )
        assert nine_box_cell(3, 2) == (3, 2)
        exported = payroll_export(
            [{"employee_number": "0001", "name": "Ada", "amount": "100"}],
            include_salary=False,
        )
        assert "amount" not in exported[0]
        assert valid_cadence("weekly") == "weekly"
        secret = b"12345678901234567890"
        code = totp(secret, 1_700_000_000)
        assert confirm_totp(secret, code, 1_700_000_000)
        assert not confirm_totp(secret, "000000", 1_700_000_000)
