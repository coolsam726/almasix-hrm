"""Orbit panel: one shell for administrators and employees."""

from __future__ import annotations

from almasix.orbit import Panel, PanelRegistry
from almasix.orbit.panels.navigation import NavigationGroup

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
        .navigation_group(NavigationGroup.make("People").icon("heroicon-o-users").sort(20))
        .navigation_group(NavigationGroup.make("Leave").icon("heroicon-o-calendar").sort(30))
        .navigation_group(NavigationGroup.make("Time").icon("heroicon-o-clock").sort(40))
        .navigation_group(NavigationGroup.make("Talent").icon("heroicon-o-briefcase").sort(50))
        .navigation_group(NavigationGroup.make("Workplace").icon("heroicon-o-chat-bubble-left").sort(60))
        .navigation_group(NavigationGroup.make("Advanced").icon("heroicon-o-sparkles").sort(70))
        .widgets([WelcomeWidget, HeadcountNote])
        .database_notifications(True)
        .database_notifications_polling("30s")
        .database_notifications_using_almasix()
        .discover_panel_dirs()
    )
    registry.register(panel)
    return panel
