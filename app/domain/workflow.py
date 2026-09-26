"""Generic (flow, state, role, action) -> next state lookup."""

from __future__ import annotations

from typing import Any


class IllegalTransition(Exception):
    """This role cannot take that action from the current state."""


def _field(row: Any, name: str) -> str:
    if isinstance(row, dict):
        return str(row[name])
    return str(getattr(row, name))


def resolve_transition(rows: Any, *, flow: str, state: str, role: str, action: str) -> str:
    for row in rows:
        if (
            _field(row, "flow") == flow
            and _field(row, "state") == state
            and _field(row, "role_slug") == role
            and _field(row, "action") == action
        ):
            return _field(row, "next_state")
    raise IllegalTransition(f"{role} cannot {action} a {flow} record that is {state}.")
