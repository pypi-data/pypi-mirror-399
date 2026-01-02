from __future__ import annotations

import datetime
import glob
import json
import shutil

import bson
import jsonpickle
from bson import json_util
import os.path
from everai.constants import EVERAI_VOLUME_ROOT
from types import SimpleNamespace
import typing

from everai.utils.datetime import format_datetime
from everai.utils.dict import remove_empty_key
from everai.utils.list import ListUtils
from everai.utils.show_mixin import ShowMixin, TableField
from everai.utils.size import human_size
from generated.volumes import V1VolumeStatus
from generated.volumes.models.v1_volume import V1Volume


class Volume(ShowMixin):
    _id: str
    _name: str
    username: str
    revision: str
    _path: typing.Optional[str]
    _created_at: datetime.datetime
    _modified_at: datetime.datetime
    _files: int
    _size: int
    status: V1VolumeStatus
    _labels: typing.Optional[typing.Dict[str, str]]

    table_fields: typing.List[TableField] = [
        TableField('name'),
        TableField('revision'),
        TableField('created_at',
                   formatter=lambda dt: format_datetime(dt)),
        TableField('files'),
        TableField('size', formatter=lambda size: human_size(size)),
        TableField('status', formatter=lambda s: s.value.removeprefix("STATUS_")),
    ]

    wide_table_extra_fields: typing.List[TableField] = [
        TableField('labels')
    ]

    def __init__(self, id: str = None, name: str = None, username: str = None, revision: str = None, path: str = None,
                 created_at: datetime.datetime = None, modified_at: datetime.datetime = None,
                 files: int = None, size: int = None,
                 status: V1VolumeStatus = None,
                 labels: typing.Optional[typing.Dict[str, str]] = None):
        self._name = name
        self.username = username
        self.revision = revision or '000000-000'
        self._id = id or ''
        self._created_at = created_at
        self._modified_at = modified_at
        self._labels = labels
        self._path = path or ''
        self._files = files or 0
        self._size = size or 0
        self.status = status
        self.set_path(path)

    def __repr__(self):
        data = '<Volume: id: {}, name: {}, revision: {}, files: {}, size: {}>'.format(
            self.id,
            self.name,
            self.revision,
            self.files,
            human_size(int(self._size)),
        )
        return data

    def __eq__(self, obj):
        return (self.id == obj.id and
                self._name == obj.name and
                self.username == obj.username and
                self.revision == obj.revision and
                self.created_at == obj.created_at and
                self.modified_at == obj.modified_at and
                self.labels == obj.labels and
                self.status == obj.status)

    def to_dict(self):
        return remove_empty_key(
            {
                'id': self.id,
                'name': self.name,
                'username': self.username,
                'revision': self.revision,
                'files': self.files,
                'size': self.size,
                'labels': self.labels,
                'created_at': format_datetime(self.created_at) if self.created_at else None,
                'modified_at': format_datetime(self.modified_at) if self.modified_at else None,
                'status': self.status.value,
            }
        )

    @staticmethod
    def from_json(data: str) -> Volume:
        x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
        return Volume(
            id=x.id if hasattr(x, 'id') else None,
            name=x.name if hasattr(x, 'name') else None,
            username=x.username if hasattr(x, 'username') else None,
            revision=x.revision if hasattr(x, 'revision') else None,
            created_at=x.created_at if hasattr(x, 'created_at') else None,
            modified_at=x.created_at if hasattr(x, 'modified_at') else None,
            status=x.status if hasattr(x, 'status') else None
        )

    @staticmethod
    def from_proto(obj: V1Volume) -> Volume:
        return Volume(
            id=obj.id,
            name=obj.name,
            username=obj.username,
            revision=obj.revision,
            files=int(obj.files),
            size=int(obj.size),
            created_at=obj.created_at,
            modified_at=obj.modified_at,
            status=obj.status,
        )

    @staticmethod
    def from_path(path: str) -> typing.Optional[Volume]:
        if not os.path.exists(path):
            return None

        metafile = os.path.join(path, '.metadata')
        if not os.path.exists(metafile) or os.path.islink(metafile):
            raise None

        with open(metafile, 'r') as f:
            data = f.read()
            v = jsonpickle.loads(data, classes=Volume)
            v.set_path(path)
            return v

    def write_metadata(self) -> None:
        assert self.ready
        metadata = jsonpickle.dumps(self)

        with open(os.path.join(self._path, '.metadata'), 'w') as f:
            f.write(metadata)

    def set_path(self, path: str) -> None:
        self._path = path or ''

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @property
    def modified_at(self) -> datetime.datetime:
        return self._modified_at

    @property
    def path(self) -> str:
        return self._path

    @property
    def files(self) -> int:
        return self._files

    @property
    def size(self) -> int:
        return self._size

    @property
    def ready(self) -> bool:
        if self._path is not None and len(self._path) > 0:
            if os.path.exists(self._path):
                return True
        return False

    @property
    def labels(self) -> typing.Optional[typing.Dict[str, str]]:
        return self._labels
