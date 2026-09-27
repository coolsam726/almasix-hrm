"""HTTP routes. The panel is mounted by Orbit; these routes are the JSON API."""

from __future__ import annotations

from almasix.routing import Route

from app.http.api import (
    anniversaries_route,
    assistant_route,
    dashboard_route,
    directory_route,
    health,
    leave_act,
    leave_apply,
    org_chart_route,
)

with Route.group(prefix="/api/hrm", middleware=["api"]):
    Route.get("/health", health)
    Route.get("/dashboard", dashboard_route)
    Route.get("/directory", directory_route)
    Route.get("/org-chart", org_chart_route)
    Route.get("/anniversaries", anniversaries_route)
    Route.post("/leave", leave_apply)
    Route.post("/leave/{leave_id}/act", leave_act)
    Route.post("/assistant", assistant_route)
