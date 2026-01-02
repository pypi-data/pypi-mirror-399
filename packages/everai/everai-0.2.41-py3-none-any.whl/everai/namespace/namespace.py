from __future__ import annotations

import datetime
import typing

from everai.utils.datetime import format_datetime
from everai.utils.show_mixin import ShowMixin, TableField
from generated.apps import V1Namespace


class Namespace(ShowMixin):
    name: str
    created_at: typing.Optional[datetime.datetime]
    labels: typing.Optional[typing.Dict[str, str]]

    table_fields: typing.List[TableField] = [
        TableField('name'),
        TableField('created_at', formatter=lambda dt: '' if dt is None else format_datetime(dt)),
    ]

    wide_table_extra_fields: typing.List[TableField] = []

    def __init__(self,
                 name: str,
                 created_at: typing.Optional[datetime.datetime] = None,
                 labels: typing.Optional[typing.Dict[str, str]] = None):
        self.name = name
        self.created_at = created_at
        self.labels = labels

    @classmethod
    def from_proto(cls, proto: V1Namespace):
        return Namespace(
            name=proto.name,
            created_at=proto.created_at,
            labels=proto.labels,
        )

    def to_proto(self) -> V1Namespace:
        return V1Namespace(
            name=self.name,
            created_at=self.created_at,
            labels=self.labels,
        )

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        origin_dict = self.to_proto().to_dict()
        origin_dict.update({
            'created_at': format_datetime(self.created_at),
        })
        return origin_dict

    @classmethod
    def from_dict(cls, data: typing.Dict[str, typing.Any]) -> Namespace:
        return Namespace.from_proto(V1Namespace.from_dict(data))
