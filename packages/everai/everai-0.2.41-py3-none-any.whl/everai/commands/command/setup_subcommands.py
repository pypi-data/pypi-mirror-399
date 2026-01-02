import typing
from argparse import ArgumentParser, _SubParsersAction

from everai.commands.command import ClientCommand


def setup_subcommands(
        parser: typing.Union[ArgumentParser, _SubParsersAction],
        subcommands: typing.List[typing.Type[ClientCommand]]):
    for subcommand in subcommands:
        subcommand.setup(parser)
