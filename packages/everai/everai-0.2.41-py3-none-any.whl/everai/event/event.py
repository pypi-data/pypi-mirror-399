from __future__ import annotations
from datetime import datetime
from typing import (
    Optional,
    List
)

from everai.utils.datetime import format_datetime
from everai.utils.show_mixin import ShowMixin, TableField
from generated.apps import (
    V1Event
)


class Event(ShowMixin):
    event_type: Optional[str]
    message: Optional[str]
    event_from: Optional[str]
    created_at: Optional[datetime]

    table_fields: List[TableField] = [
        TableField('type',
                   picker=lambda e: e.event_type, formatter=lambda t: t.removeprefix('EVENT_TYPE_')),
        TableField('from', picker=lambda d: d.event_from),
        TableField('created_at', formatter=lambda dt: format_datetime(dt)),
        TableField('message'),
    ]

    wide_table_extra_fields: List[str] = []

    def __init__(self,
                 event_type: Optional[str] = None,
                 message: Optional[str] = None,
                 event_from: Optional[str] = None,
                 created_at: Optional[datetime] = None,
                 ):
        self.event_type = event_type
        self.message = message
        self.event_from = event_from
        self.created_at = created_at

    @staticmethod
    def from_proto(event: V1Event) -> Event:
        return Event(
            event_type=event.type,
            message=event.message,
            event_from=event.var_from,
            created_at=event.created_at,
        )

    def to_dict(self):
        return {
            'type': self.event_type.removeprefix('EVENT_TYPE_'),
            'from': self.event_from,
            'created_at': format_datetime(self.created_at),
            'message': self.message,
        }
