import functools
import typing

import regex


def myself_volume_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_args = 0
        if func.__qualname__.index(".") != -1:
            start_args = 1

        n: typing.Optional[str] = None
        if len(args) > start_args:
            n = args[start_args]

        if kwargs.get('name', None) is not None:
            n = kwargs.get('name')

        if kwargs.get('volume_name', None) is not None:
            n = kwargs.get('volume_name')
        if n is None:
            raise Exception('No volume name provided')

        if n.count("/") != 0:
            raise ValueError('only short volume name (do not include user name) permitted')

        return func(*args, **kwargs)
    return wrapper


def regular_name(name: str) -> str:
    if name.count('/') == 0 or regex.match('^users/[^/]+/volumes/[^/]+$', name):
        return name

    if name.count('/') != 1:
        raise ValueError(f'invalid volume name {name}')

    (user, volume) = name.split('/')
    return f'users/{user}/volumes/{volume}'


def regular_volume_name(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_args = 0
        if func.__qualname__.index(".") != -1:
            start_args = 1

        before_args = args[:start_args]
        after_args = []

        k: typing.Optional[str] = None
        n: typing.Optional[str] = None
        if len(args) > start_args:
            n = args[start_args]
            after_args = args[start_args + 1:]

        if kwargs.get('name', None) is not None:
            k = 'name'
            n = kwargs.get('name')

        if kwargs.get('volume_name', None) is not None:
            k = 'volume_name'
            n = kwargs.get('volume_name')

        if n is None:
            raise Exception('No volume name provided')
        n = regular_name(n)

        if k is not None:
            kwargs[k] = n
        else:
            args = list(before_args) + [n] + list(after_args)

        return func(*args, **kwargs)
    return wrapper
