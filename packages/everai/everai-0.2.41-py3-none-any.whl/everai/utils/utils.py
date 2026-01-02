from synchronicity import Synchronizer
import inspect
from typing import TypeVar

synchronizer = Synchronizer()


def synchronize(target, target_module=None):
    if inspect.isclass(target):
        target_name = target.__name__.strip("_")
    elif inspect.isfunction(object):
        target_name = target.__name__.strip("_")
    elif isinstance(target, TypeVar):
        target_name = "_BLOCKING_" + target.__name__
    else:
        target_name = None
    if target_module is None:
        target_module = target.__module__

    return synchronizer.create_blocking(target, target_name, target_module=target_module)