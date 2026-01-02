import functools
import typing

AppSetupCallable = typing.Callable[[], None]
AppSetupMethod = typing.Callable[[AppSetupCallable], AppSetupCallable]
T = typing.TypeVar('T')
A = typing.TypeVar('A')


class _AppSetupFunction:
    def __init__(self, func: AppSetupCallable,
                 optional: bool = False,
                 ):
        self.func = func
        self.name = func.__name__
        self.optional = optional

    def __call__(self):
        return self.func()


def setup_params(func):
    @functools.wraps(func)
    def decorator(self, optional=False):
        return func(self, optional=optional)

    return decorator


class AppSetupMixin:
    _prepare_funcs: typing.Optional[typing.List[_AppSetupFunction]] = None
    _clear_funcs: typing.Optional[typing.List[_AppSetupFunction]] = None

    @property
    def prepare_funcs(self) -> typing.List[_AppSetupFunction]:
        return self._prepare_funcs or []

    @property
    def clear_funcs(self) -> typing.List[_AppSetupFunction]:
        return self._clear_funcs or []

    @setup_params
    def prepare(self, *args, **kwargs) -> AppSetupMethod:
        def decorator(func: AppSetupCallable) -> AppSetupCallable:
            if self._prepare_funcs is None:
                self._prepare_funcs = []
            self._prepare_funcs.append(_AppSetupFunction(func, *args, **kwargs))
            return func

        return decorator

    @setup_params
    def clear(self, *args, **kwargs) -> AppSetupMethod:
        def decorator(func: AppSetupCallable) -> AppSetupCallable:
            if self._clear_funcs is None:
                self._clear_funcs = []
            self._clear_funcs.append(_AppSetupFunction(func, *args, **kwargs))
            return func

        return decorator
