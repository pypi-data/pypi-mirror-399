import typing


def str_to_bool(s: typing.Optional[str]) -> bool:
    if s is None:
        return False
    return s.lower() in ['true', "yes", "1"]
