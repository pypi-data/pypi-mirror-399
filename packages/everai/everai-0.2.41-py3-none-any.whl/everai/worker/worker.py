from __future__ import annotations

import typing
from datetime import datetime

from everai.utils.datetime import format_datetime
from everai.utils.dict import remove_empty_key
from everai.utils.show_mixin import ShowMixin, TableField
from generated.apps import V1Worker, WorkerWorkerStatus


class Worker(ShowMixin):
    worker_id: str
    device_id: str
    status: WorkerWorkerStatus
    detail_status: str
    created_at: datetime
    last_serve_at: datetime
    deleted_at: typing.Optional[datetime]
    failed_count: int
    success_count: int

    table_fields: typing.List[TableField] = [
        TableField('worker_id', "ID"),
        TableField('status', formatter=lambda s: '' if s is None else s.removeprefix("STATUS_")),
        TableField('detail_status', formatter=lambda s: '' if s is None else s.value.removeprefix("DETAIL_STATUS_")),
        TableField('created_at', formatter=lambda dt: format_datetime(dt) if dt else ''),
        TableField('deleted_at', formatter=lambda dt: format_datetime(dt) if dt else ''),
    ]

    wide_table_extra_fields: typing.List[TableField] = [
        TableField('device_id', "DEVICE"),
        TableField('last_serve_at', formatter=lambda dt: format_datetime(dt) if dt else ''),
        TableField('success_count'),
        TableField('failed_count'),
    ]

    def __init__(self, worker_id: str, device_id: str, status: WorkerWorkerStatus,
                 detail_status: str,
                 created_at: datetime,
                 last_serve_at: datetime,
                 success_count: int = 0,
                 failed_count: int = 0,
                 deleted_at: typing.Optional[datetime] = None,
                 ):
        self.worker_id = worker_id
        self.device_id = device_id
        self.status = status
        self.detail_status = detail_status
        self.created_at = created_at
        self.deleted_at = deleted_at
        self.last_serve_at = last_serve_at
        self.success_count = success_count
        self.failed_count = failed_count

    @staticmethod
    def from_proto(worker: V1Worker) -> Worker:
        return Worker(
            worker_id=worker.id,
            device_id=worker.device_id,
            status=worker.status,
            detail_status=worker.detail_status,
            created_at=worker.created_at,
            deleted_at=worker.deleted_at,
            last_serve_at=worker.last_serve_at,
            success_count=worker.success_count,
            failed_count=worker.failed_count,
        )

    def to_proto(self) -> V1Worker:
        return V1Worker(
            id=self.worker_id,
            device_id=self.device_id,
            status=self.status,
            detail_status=self.detail_status,
            created_at=self.created_at,
            deleted_at=self.deleted_at,
            last_serve_at=self.last_serve_at,
            success_count=self.success_count,
            failed_count=self.failed_count,
        )

    def to_dict(self):
        result = remove_empty_key({
            'id': self.worker_id,
            'device': self.device_id,
            'status': self.status.value.removeprefix("STATUS_"),
            'detail_status': self.detail_status.removeprefix("DETAIL_STATUS_") if self.detail_status else None,
            'success_count': self.success_count,
            'failed_count': self.failed_count,
            'last_serve_at': format_datetime(self.last_serve_at) if self.last_serve_at else None,
            'created_at': format_datetime(self.created_at),
            'deleted_at': format_datetime(self.deleted_at) if self.deleted_at else None,
        })
        return result
