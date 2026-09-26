"""Build a standard list/create/edit resource for a setup table."""

from __future__ import annotations

from typing import Any

from almasix.orbit import Resource
from almasix.orbit.forms import TextInput
from almasix.orbit.infolists import Infolist, TextEntry
from almasix.orbit.tables import Table, TextColumn

from app.domain.access import user_can_read


def crud(
    class_name: str,
    *,
    model: type[Any],
    label: str,
    group: str,
    data_group: str,
    icon: str,
    sort: int,
    fields: tuple[str, ...],
    mutable: bool = True,
) -> type[Resource]:
    def form(cls: type[Resource], form: Any) -> Any:
        return form.schema([TextInput.make(name).required() for name in cls.entry_fields])

    def table(cls: type[Resource], table: Table) -> Table:
        return table.columns([TextColumn.make(name) for name in cls.entry_fields])

    def infolist(cls: type[Resource], infolist: Infolist) -> Infolist:
        return infolist.schema([TextEntry.make(name) for name in cls.entry_fields])

    def can_view_any(cls: type[Resource], user: Any) -> bool:
        return user_can_read(user, cls.data_group)

    return type(
        class_name,
        (Resource,),
        {
            "model": model,
            "navigation_label": label,
            "navigation_group": group,
            "navigation_icon": icon,
            "navigation_sort": sort,
            "record_title_attribute": fields[0],
            "data_group": data_group,
            "entry_fields": fields,
            "records_mutable": mutable,
            "form": classmethod(form),
            "table": classmethod(table),
            "infolist": classmethod(infolist),
            "can_view_any": classmethod(can_view_any),
        },
    )
