import typing

from everai.app import App, AppManager
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction, Namespace
from everai.namespace import Namespace as EveraiNamespace


class DeleteCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        delete_parser = parser.add_parser('delete', help='Delete a namespace')
        delete_parser.add_argument('name', help="The namespace name")
        delete_parser.set_defaults(func=DeleteCommand)
        DeleteCommand.parser = delete_parser

    @command_error
    def run(self):
        AppManager().delete_namespace(self.args.name)
