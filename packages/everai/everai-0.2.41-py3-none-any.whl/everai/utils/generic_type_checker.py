import typing

T = typing.TypeVar('T')


class GenericTypeChecker(typing.Generic[T]):
    def is_right_type(self, x: typing.Any) -> bool:
        # print(self.__orig_class__.__args__[0])
        # print(type(x))
        return isinstance(x, self.__orig_class__.__args__[0])
