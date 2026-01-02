import datetime
import functools
import typing
import abc

from everai.utils.datetime import format_datetime, parse_datetime
from everai.utils.generic_type_checker import GenericTypeChecker
from generated.apps import V1App, V1AppStatusV1Alpha1Status, AppSpecV1Alpha1RouteAuthType

AppSetupCallable = typing.Callable[[], None]
AppSetupMethod = typing.Callable[[AppSetupCallable], AppSetupCallable]
T = typing.TypeVar('T')
A = typing.TypeVar('A')
S = typing.TypeVar('S')
D = typing.TypeVar('D')


def check_if_dict_with_str_keys(data):
    return isinstance(data, dict) and all(isinstance(x, str) for x in data.keys())


class FieldMapper:
    path: typing.Optional[str]
    picker: typing.Optional[typing.Callable[[T, A], typing.Any]]

    def __init__(self, path: typing.Optional[str] = None,
                 picker: typing.Optional[typing.Callable[[T, A], typing.Any]] = None):
        self.path = path
        self.picker = picker
        if self.path is None and self.picker is None:
            raise ValueError('one of path and picker is required')


class Matcher(abc.ABC):
    @abc.abstractmethod
    def match(self, obj: typing.Dict[str, typing.Any]) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
        ...


class PathMatcher(Matcher):
    path: str

    def __init__(self, path: str):
        self.path = path

    def match(self, obj: typing.Dict[str, typing.Any]) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
        fields = self.path.split('.')
        current = obj
        for f in fields:
            if check_if_dict_with_str_keys(current):
                ret = current.get(f)
                current = ret
                if current is None:
                    break
        if current is not None:
            yield self.path, current


class TypeMatcher(Matcher):
    parent: str
    t: T

    def __init__(self, parent: str, t: type):
        self.parent = parent
        self.t = t

    def match(self, obj: typing.Dict[str, typing.Any]) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
        fields = self.parent.split('.')
        current = obj
        for f in fields:
            if check_if_dict_with_str_keys(current):
                ret = current.get(f)
                current = ret
                if current is None:
                    break
        if current is None or not check_if_dict_with_str_keys(current):
            return

        for k, v in current.items():
            if GenericTypeChecker[self.t]().is_right_type(v):
                yield f'{self.parent}.{k}', v


class Converter:
    matcher: Matcher
    action: typing.Callable[[S], D]

    def __init__(self, matcher: Matcher, action: typing.Callable[[S], D]):
        self.matcher = matcher
        self.action = action


class AppVersionedMixin:
    _app: V1App

    to_dict_converter: typing.Dict[str, typing.List[Converter]] = dict(
        v1alpha1=[
            Converter(matcher=PathMatcher(path='status.status'), action=lambda x: x.value.removeprefix('STATUS_')),
            Converter(matcher=PathMatcher(path='spec.routeAuthType'),
                      action=lambda x: x.value.removeprefix('ROUTE_AUTH_TYPE_')),
            Converter(matcher=TypeMatcher(parent='metadata', t=datetime.datetime),
                      action=lambda x: format_datetime(x)),
        ]
    )

    from_dict_converter = dict(
        v1alpha1=[
            Converter(matcher=PathMatcher(path='status.status'),
                      action=lambda x: V1AppStatusV1Alpha1Status(x if x.startswith('STATUS_') else 'STATUS_' + x)),
            Converter(matcher=PathMatcher(path='spec.routeAuthType'),
                      action=lambda x: AppSpecV1Alpha1RouteAuthType(x if x.startswith('STATUS_') else 'ROUTE_AUTH_TYPE_' + x)),
            Converter(matcher=TypeMatcher(parent='metadata', t=datetime.datetime),
                      action=lambda x: parse_datetime(x)),
        ]
    )

    def _get_data(self) -> typing.Any:
        def _get_attr(x, y):
            if y in x.__dict__.keys():
                return getattr(x, y)
            else:
                msg = f'no attribute {x} in {type(y)}'
                raise AttributeError(msg)

        v = functools.reduce(_get_attr, ['_app', 'app_v1alpha1'], self)
        if v is not None:
            return v
        else:
            raise ValueError('no any valid version for app')

    def _get_to_dict_converter(self) -> typing.List[Converter]:
        if self._app.app_v1alpha1 is not None:
            return AppVersionedMixin.to_dict_converter['v1alpha1']
        else:
            raise ValueError('no any valid version for app')

    @classmethod
    def _get_from_dict_converter(cls, version: str) -> typing.List[Converter]:
        if version == 'v1alpha1':
            return AppVersionedMixin.from_dict_converter['v1alpha1']
        else:
            raise ValueError(f'unsupported version {version} for app')

    @staticmethod
    def set_dict(d: typing.Dict[str, typing.Any], p: str, v: typing.Any):
        fields = p.split('.')
        current = d
        for field in fields[:-1]:
            current = current[field]
            if current is None:
                break
        current[fields[-1]] = v

    def get_to_dict(self) -> typing.Dict[str, typing.Any]:
        data = self._get_data()
        result = data.to_dict()
        to_dict = self._get_to_dict_converter()
        for c in to_dict:
            for path, value in c.matcher.match(result):
                new_value = c.action(value)
                AppVersionedMixin.set_dict(result, path, new_value)
        return result

    @staticmethod
    def convert_from_dict(data: typing.Dict[str, typing.Any], version: str) -> typing.Dict[str, typing.Any]:
        from_dict = AppVersionedMixin._get_from_dict_converter(version)
        for c in from_dict:
            for path, value in c.matcher.match(data):
                new_value = c.action(value)
                AppVersionedMixin.set_dict(data, path, new_value)
        return data

    @property
    def metadata(self):
        return self._app.app_v1alpha1.metadata

    @property
    def spec(self):
        return self._app.app_v1alpha1.spec

    @property
    def status(self):
        return self._app.app_v1alpha1.status

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def namespace(self) -> str:
        return self.metadata.namespace or 'default'

    @namespace.setter
    def namespace(self, namespace: str):
        self._app.app_v1alpha1.metadata.namespace = namespace

    @property
    def created_at(self):
        return self.metadata.created_at

    @property
    def updated_at(self):
        return self.metadata.updated_at

    def labels(self):
        return self.metadata.labels
