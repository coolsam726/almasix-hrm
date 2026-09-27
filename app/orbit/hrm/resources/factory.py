"""Build a standard list/create/edit resource for a setup table."""

from __future__ import annotations

from typing import Any

from almasix.orbit import Resource
from almasix.orbit.actions import (
    BulkActionGroup,
    CreateAction,
    DeleteAction,
    DeleteBulkAction,
    EditAction,
    ViewAction,
)
from almasix.orbit.forms import TextInput
from almasix.orbit.infolists import Infolist, TextEntry
from almasix.orbit.tables import Table, TextColumn

from app.domain.access import employee_in_scope, grant_for, user_can_read, user_can_write


def _actor() -> Any:
    from almasix.orbit.panels.pages.resource_pages import _auth_user

    return _auth_user()


def _owner(record: Any, key: str) -> Any:
    if record is None:
        return None
    if isinstance(record, dict):
        return record.get(key)
    return getattr(record, key, None)


def _menu_scope(user: Any, group: str) -> str:
    if user is None:
        return "self"
    if getattr(user, "is_admin", False):
        return "all"
    grant = grant_for(user, group) or {}
    return str(grant.get("scope") or "self")


def _may_hire(user: Any, group: str) -> bool:
    if user is None:
        return False
    if getattr(user, "is_admin", False):
        return True
    grant = grant_for(user, group) or {}
    return bool(grant.get("write") and str(grant.get("scope") or "") == "all")


def crud(
    class_name: str,
    *,
    model: type[Any],
    label: str,
    group: str,
    subgroup: str,
    data_group: str,
    icon: str,
    sort: int,
    fields: tuple[str, ...],
    mutable: bool = True,
    modal: bool = False,
    employee_scope: str | None = None,
    menu_when: str = "read",
) -> type[Resource]:
    def inputs(cls: type[Resource]) -> list[Any]:
        return [TextInput.make(name).required() for name in cls.entry_fields]

    def form(cls: type[Resource], form: Any) -> Any:
        return form.schema(inputs(cls))

    def table(cls: type[Resource], table: Table) -> Table:
        built = table.columns([TextColumn.make(name) for name in cls.entry_fields])
        if not cls.quick_modal:
            if getattr(cls, "employee_scope", None) != "id":
                return built

            def may_hire(**_: Any) -> bool:
                return _may_hire(_actor(), cls.data_group)

            def may_write(**_: Any) -> bool:
                return user_can_write(_actor(), cls.data_group)

            return (
                built.header_actions(
                    [
                        CreateAction.make()
                        .url(lambda **_: cls.page_url("create"))
                        .visible(may_hire),
                    ]
                )
                .actions(
                    [
                        ViewAction.make().url(
                            lambda record=None, **_: cls.page_url("view", record)
                        ),
                        EditAction.make()
                        .url(lambda record=None, **_: cls.page_url("edit", record))
                        .visible(may_write),
                        DeleteAction.make().visible(may_hire),
                    ]
                )
                .bulk_actions(
                    [
                        BulkActionGroup.make(
                            [DeleteBulkAction.make().icon("heroicon-o-trash")]
                        ).visible(may_hire),
                    ]
                )
            )
        return (
            built.header_actions(
                [
                    CreateAction.make()
                    .modal()
                    .modal_heading(cls.navigation_label)
                    .form(inputs(cls))
                    .create_another(),
                ]
            )
            .actions(
                [
                    ViewAction.make().modal_heading(cls.navigation_label).form(inputs(cls)),
                    EditAction.make()
                    .modal()
                    .modal_heading(cls.navigation_label)
                    .form(inputs(cls)),
                    DeleteAction.make(),
                ]
            )
        )

    def infolist(cls: type[Resource], infolist: Infolist) -> Infolist:
        return infolist.schema([TextEntry.make(name) for name in cls.entry_fields])

    def can_view_any(cls: type[Resource], user: Any) -> bool:
        if not user_can_read(user, cls.data_group):
            return False
        rule = getattr(cls, "menu_when", "read")
        scope = _menu_scope(user, cls.data_group)
        if rule == "beyond_self":
            return scope in {"subordinates", "all"}
        if rule == "company":
            return scope == "all"
        return True

    namespace: dict[str, Any] = {
        "model": model,
        "navigation_label": label,
        "navigation_group": group,
        "navigation_subgroup": subgroup,
        "navigation_icon": icon,
        "navigation_sort": sort,
        "record_title_attribute": fields[0],
        "data_group": data_group,
        "entry_fields": fields,
        "records_mutable": mutable,
        "quick_modal": modal,
        "menu_when": menu_when,
        "form": classmethod(form),
        "table": classmethod(table),
        "infolist": classmethod(infolist),
        "can_view_any": classmethod(can_view_any),
    }
    if employee_scope:
        scope_key = "id" if employee_scope == "id" else "employee_id"

        async def scope_records(cls: type[Resource], user: Any, records: list[Any]) -> list[Any]:
            from app.domain.operations import subordinate_ids_for

            subs = await subordinate_ids_for(user) if user is not None else set()
            kept: list[Any] = []
            for record in records:
                owner = _owner(record, scope_key)
                if employee_in_scope(user, cls.data_group, owner, subs, write=False):
                    kept.append(record)
            return kept

        async def record_allowed(
            cls: type[Resource], user: Any, record: Any, *, write: bool = False
        ) -> bool:
            from app.domain.operations import subordinate_ids_for

            subs = await subordinate_ids_for(user) if user is not None else set()
            return employee_in_scope(
                user, cls.data_group, _owner(record, scope_key), subs, write=write
            )

        def can_create(cls: type[Resource], user: Any) -> bool:
            if cls.employee_scope == "id":
                return _may_hire(user, cls.data_group)
            return user_can_write(user, cls.data_group)

        def can_delete(cls: type[Resource], user: Any, record: Any = None) -> bool:
            if cls.employee_scope == "id":
                return _may_hire(user, cls.data_group)
            return user_can_write(user, cls.data_group)

        namespace["employee_scope"] = employee_scope
        namespace["scope_records"] = classmethod(scope_records)
        namespace["record_allowed"] = classmethod(record_allowed)
        namespace["can_create"] = classmethod(can_create)
        namespace["can_delete"] = classmethod(can_delete)

    return type(class_name, (Resource,), namespace)
