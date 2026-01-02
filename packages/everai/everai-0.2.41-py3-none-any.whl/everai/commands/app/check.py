import typing

import everai.utils.verbose as vb
from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.runner.run import find_target


class CheckCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        check_parser = parser.add_parser("check", help="Check app is correct in app directory")

        check_parser.set_defaults(func=CheckCommand)

    def run(self):
        find_target(raise_exception=True)

