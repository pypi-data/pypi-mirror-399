import typing
from functools import cmp_to_key

T = typing.TypeVar('T')
T2 = typing.TypeVar('T2')

PreProcessFunction = typing.Callable[[T], T]
CompareFunction = typing.Callable[[T, T], int]
PickupFunction = typing.Callable[[T], T2]


def pickup_compare_func(f: PickupFunction, reverse: bool = False) -> CompareFunction:
    def compare_func(a: T, b: T) -> int:
        a_field = f(a)
        b_field = f(b)
        reverse_value = -1 if reverse else 1
        return 0 if a_field == b_field else (1 * reverse_value) if a_field > b_field else (-1 * reverse_value)

    return compare_func


class ListUtils:
    @staticmethod
    def diff(src: typing.List[T], dst: typing.List[T],
             src_processor: PreProcessFunction = None,
             dst_processor: PreProcessFunction = None,
             ) -> (typing.List[T], typing.List[T], typing.List[T]):

        processed_src = [x if src_processor is None else src_processor(x) for x in src]
        processed_dst = [x if dst_processor is None else dst_processor(x) for x in dst]

        in_both: typing.List[T] = []
        in_dst: typing.List[T] = []
        in_src: typing.List[T] = []
        for s in processed_src:
            if s in processed_dst:
                in_both.append(s)
            else:
                in_src.append(s)

        for d in processed_dst:
            if d not in processed_src:
                in_dst.append(d)

        return in_src, in_both, in_dst

    @staticmethod
    def sort(src: typing.List[T], compare_func: CompareFunction = None) -> None:
        if compare_func is None:
            return src.sort()
        else:
            return src.sort(key=cmp_to_key(compare_func))

    @staticmethod
    def compare_list2(src: typing.List[T], dst: typing.List[T],
                      src_func: PreProcessFunction = None,
                      both_func: PreProcessFunction = None,
                      dst_func: PreProcessFunction = None
                      ) -> (typing.List[T], typing.List[T], typing.List[T]):
        in_both: typing.List[T] = []
        in_dst: typing.List[T] = []
        in_src: typing.List[T] = []
        for s in src:
            if s in dst:
                in_both.append(s) if both_func is None or both_func(s) else None
            else:
                in_src.append(s) if src_func is None or src_func(s) else None

        for d in dst:
            if d not in src:
                in_dst.append(d) if dst_func is None or dst_func(d) else None

        return in_src, in_dst, in_both
