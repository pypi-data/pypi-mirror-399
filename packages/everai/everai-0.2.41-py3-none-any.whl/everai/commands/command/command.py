from abc import ABC, abstractmethod
from argparse import _SubParsersAction, ArgumentParser


class ClientCommand(ABC):
    @abstractmethod
    def __init__(self, args):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def setup(parser: _SubParsersAction) -> None:
        raise NotImplementedError()

    @abstractmethod
    def run(self):
        raise NotImplementedError()