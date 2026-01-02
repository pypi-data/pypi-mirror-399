from __future__ import annotations
from everai.placeholder import PlaceholderValue


class Environment:
    name: str
    value: PlaceholderValue

    def __init__(
            self,
            name: str,
            value: PlaceholderValue
    ):
        self.name = name
        self.value = value
