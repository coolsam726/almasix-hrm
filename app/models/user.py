"""User accounts. Grants are a JSON cache of the role matrix."""

from __future__ import annotations

from almasix.auth import AuthenticatableMixin
from almasix.notifications import Notifiable
from almasix.orm import Model


class User(AuthenticatableMixin, Notifiable, Model):
    table = "users"
    fillable = (
        "name",
        "email",
        "password",
        "remember_token",
        "role_slug",
        "employee_id",
        "is_admin",
        "grants",
        "locale",
    )
    hidden = ("password", "remember_token")
    casts = {
        "is_admin": "bool",
        "grants": "json",
    }
