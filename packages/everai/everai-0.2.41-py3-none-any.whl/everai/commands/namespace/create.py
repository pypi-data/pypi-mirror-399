import typing

from everai.app import App, AppManager
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction, Namespace
from everai.namespace import Namespace as EveraiNamespace


class CreateCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        create_parser = parser.add_parser('create', help='Create a namespace')
        create_parser.add_argument('name', nargs='?', default='default', help="The namespace name")
        create_parser.set_defaults(func=CreateCommand)
        CreateCommand.parser = create_parser

    @command_error
    def run(self):
        namespace = AppManager().create_namespace(self.args.name)
        print(f'Namespace {namespace.name} successfully created')
