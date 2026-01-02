from __future__ import annotations

import base64
import json
import typing

import yaml

from everai.utils.show_mixin import ShowMixin, TableField
from generated.secrets import V1Secret


class Secret(ShowMixin):
    def __init__(self, name: str, data: typing.Dict[str, str],
                 labels: typing.Optional[typing.Dict[str, str]] = None):

        self.name = name or ''
        self.data = data or {}
        self.labels = labels

    table_fields: typing.List[TableField] = [
        TableField('name'),
        TableField('data', 'ITEMS',
                   lambda item: str(len(item)))
    ]
    wide_table_extra_fields: typing.List[TableField] = [
        TableField('labels'),
    ]

    def get(self, key: str, default: str | None = None) -> str:
        value = self.data.get(key, None)
        if value is None:
            return default
        return value

    def __show(self) -> str:
        lines: typing.List[str] = [f"Secret(Name: {self.name})"]
        data = {} if self.data is None else self.data

        lines.extend([f'\t{k} - ******' for k in data])

        return '\n'.join(lines) + '\n'

    @staticmethod
    def from_proto(sec: V1Secret) -> Secret:
        plaintext_data = {key: base64.b64decode(value).decode('utf-8')
                          for key, value in sec.data.items()}

        return Secret(name=sec.name, data=plaintext_data, labels=sec.labels)

    @staticmethod
    def from_yaml_file(file: str) -> Secret:
        with open(file, 'r') as f:
            obj = yaml.safe_load(f)
        return Secret.from_dict(obj)

    @staticmethod
    def from_dict(obj: typing.Dict[str, typing.Any]) -> Secret:
        v1secret = V1Secret.from_dict(obj)
        return Secret.from_proto(v1secret)

    def to_proto(self) -> V1Secret:
        base64_dict = {key: base64.b64encode(value.encode('utf-8')).decode('utf-8')
                       for key, value in self.data.items()}
        return V1Secret(name=self.name, data=base64_dict, labels=self.labels)

    def to_json(self):
        v1secret = self.to_proto()
        result = {
            'name': self.name,
            'data': v1secret.data,
        }
        if self.labels is not None and len(self.labels) > 0:
            result['labels'] = self.labels
        return json.dumps(result, ensure_ascii=False)

    def to_dict(self):
        v1secret = self.to_proto()
        result = {
            'name': self.name,
            'data': v1secret.data,
        }
        if self.labels is not None and len(self.labels) > 0:
            result['labels'] = self.labels
        return result

    def __str__(self):
        return self.__show()

    def __repr__(self):
        return self.__show()
