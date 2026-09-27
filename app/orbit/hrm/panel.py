"""Orbit panel: one shell for administrators and employees."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup, NavigationSubgroup

from app.orbit.hrm.widgets.home import HeadcountNote, WelcomeWidget


def register_hrm_panel(registry: PanelRegistry) -> Panel:
    panel = (
        Panel.make("hrm")
        .path("/")
        .brand_name("Almasix HRM")
        .font("Outfit")
        .primary("#0f766e")
        .colors(danger="#ef4444", success="#22c55e", warning="#f59e0b", info="#0ea5e9")
        .dark_mode()
        .theme_switcher()
        .default_theme_mode("system")
        .sidebar_collapsible(False)
        .login()
        .navigation_group(NavigationGroup.make("Admin").icon("heroicon-o-cog-6-tooth").sort(10))
        .navigation_group(NavigationGroup.make("PIM").icon("heroicon-o-users").sort(20))
        .navigation_group(NavigationGroup.make("Contracts").icon("heroicon-o-document-text").sort(25))
        .navigation_group(NavigationGroup.make("Leave").icon("heroicon-o-calendar").sort(30))
        .navigation_group(NavigationGroup.make("Time").icon("heroicon-o-clock").sort(40))
        .navigation_group(NavigationGroup.make("Recruitment").icon("heroicon-o-user-plus").sort(50))
        .navigation_group(NavigationGroup.make("ESS").icon("heroicon-o-user").sort(60))
        .navigation_group(NavigationGroup.make("Performance").icon("heroicon-o-chart-bar").sort(70))
        .navigation_group(NavigationGroup.make("Directory").icon("heroicon-o-book-open").sort(80))
        .navigation_group(NavigationGroup.make("Maintenance").icon("heroicon-o-trash").sort(90))
        .navigation_group(NavigationGroup.make("Buzz").icon("heroicon-o-chat-bubble-left").sort(100))
        .navigation_group(NavigationGroup.make("Claim").icon("heroicon-o-receipt-percent").sort(110))
        .navigation_group(NavigationGroup.make("Advanced").icon("heroicon-o-sparkles").sort(120))
        .navigation_subgroups(
            [
                NavigationSubgroup.make("Job").parent("Admin").icon("heroicon-o-briefcase").sort(10),
                NavigationSubgroup.make("Organization").parent("Admin").icon("heroicon-o-building-office").sort(20),
                NavigationSubgroup.make("Qualifications").parent("Admin").icon("heroicon-o-academic-cap").sort(30),
                NavigationSubgroup.make("Configuration").parent("Admin").icon("heroicon-o-adjustments-horizontal").sort(40),
                NavigationSubgroup.make("Configuration").parent("PIM").icon("heroicon-o-adjustments-horizontal").sort(30),
                NavigationSubgroup.make("Personal").parent("ESS").icon("heroicon-o-identification").sort(10),
                NavigationSubgroup.make("Job").parent("ESS").icon("heroicon-o-briefcase").sort(20),
                NavigationSubgroup.make("Qualifications").parent("ESS").icon("heroicon-o-academic-cap").sort(30),
                NavigationSubgroup.make("Configure").parent("Leave").icon("heroicon-o-cog-6-tooth").sort(10),
                NavigationSubgroup.make("Requests").parent("Leave").icon("heroicon-o-inbox").sort(20),
                NavigationSubgroup.make("Projects").parent("Time").icon("heroicon-o-folder").sort(10),
                NavigationSubgroup.make("Attendance").parent("Time").icon("heroicon-o-clock").sort(20),
                NavigationSubgroup.make("Configure").parent("Performance").icon("heroicon-o-cog-6-tooth").sort(10),
                NavigationSubgroup.make("Manage reviews").parent("Performance").icon("heroicon-o-clipboard-document-check").sort(20),
                NavigationSubgroup.make("Onboarding").parent("Advanced").icon("heroicon-o-flag").sort(10),
                NavigationSubgroup.make("Desk").parent("Advanced").icon("heroicon-o-inbox-stack").sort(20),
                NavigationSubgroup.make("Roster").parent("Advanced").icon("heroicon-o-calendar-days").sort(30),
                NavigationSubgroup.make("Career").parent("Advanced").icon("heroicon-o-map").sort(40),
                NavigationSubgroup.make("Learning").parent("Advanced").icon("heroicon-o-academic-cap").sort(50),
                NavigationSubgroup.make("Cases").parent("Advanced").icon("heroicon-o-scale").sort(60),
                NavigationSubgroup.make("Company").parent("Advanced").icon("heroicon-o-building-library").sort(70),
            ]
        )
        .widgets([WelcomeWidget, HeadcountNote])
        .database_notifications(True)
        .database_notifications_polling("30s")
        .database_notifications_using_almasix()
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
