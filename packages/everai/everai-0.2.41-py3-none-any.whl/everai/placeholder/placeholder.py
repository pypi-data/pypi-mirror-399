from __future__ import annotations
import typing

from everai.app.context import context
from generated.apps import Commonv1Value, V1ValueFrom, V1KeyReference


class Placeholder:
    def __init__(self, name: str, key: str,
                 kind: typing.Literal['ConfigMap', "Secret"] = 'Secret'):
        self.name = name
        self.key = key
        self.kind = kind

    def __call__(self) -> str:

        match self.kind:
            case 'ConfigMap':
                holder = context.get_configmap(self.name)
            case 'Secret':
                holder = context.get_secret(self.name)
            case _:
                raise ValueError(f'Unsupported placeholder kind {self.kind}')

        assert holder is not None

        value = holder.get(self.key)
        assert value is not None

        return value


class PlaceholderValue:
    value: typing.Union[str, Placeholder]

    def __init__(
            self,
            value: typing.Optional[str] = None,
            placeholder: typing.Optional[Placeholder] = None,
    ):
        assert value is not None or placeholder is not None
        self.value = value if value is not None else placeholder

    def to_proto(self) -> Commonv1Value:
        if isinstance(self.value, str):
            return Commonv1Value(value=self.value)
        else:
            if isinstance(self.value, Placeholder):
                if self.value.kind == "Secret":
                    return Commonv1Value(value_from=V1ValueFrom(
                        secret_key_ref=V1KeyReference(name=self.value.name, key=self.value.key)
                    ))
                elif self.value.kind == "ConfigMap":
                    return Commonv1Value(value_from=V1ValueFrom(
                        config_map_key_ref=V1KeyReference(name=self.value.name, key=self.value.key)
                    ))
                else:
                    raise ValueError(f'unsupported placeholder kind {self.value.kind}')
            else:
                raise ValueError(f'unsupported username value {type(self)}')

    def __call__(self) -> str:
        if self.value is None:
            raise ValueError('PlaceholderValue is None')

        if isinstance(self.value, str):
            return self.value
        elif isinstance(self.value, Placeholder):
            return self.value()
        else:
            raise ValueError('invalid placeholder value')

    @classmethod
    def from_proto(cls, proto: Commonv1Value) -> PlaceholderValue:
        if proto.value is not None:
            return PlaceholderValue(value=proto.value)
        elif proto.value_from is not None:
            if proto.value_from.secret_key_ref is not None:
                return PlaceholderValue(placeholder=Placeholder(
                    kind='Secret',
                    name=proto.value_from.secret_key_ref.name,
                    key=proto.value_from.secret_key_ref.key,
                ))
            elif proto.value_from.config_map_key_ref is not None:
                return PlaceholderValue(placeholder=Placeholder(
                    kind='ConfigMap',
                    name=proto.value_from.config_map_key_ref.name,
                    key=proto.value_from.config_map_key_ref.key,
                ))
            else:
                raise ValueError(f'empty proto value[value_from]')
        else:
            raise ValueError(f'empty proto value')