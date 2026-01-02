from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction, Namespace

from everai import __version__ as package_version


class VersionCommand(ClientCommand):
    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction) -> None:
        version_parser = parser.add_parser('version', help='Show package and client version')
        version_parser.set_defaults(func=VersionCommand)

    @command_error
    def run(self):
        print(package_version)
