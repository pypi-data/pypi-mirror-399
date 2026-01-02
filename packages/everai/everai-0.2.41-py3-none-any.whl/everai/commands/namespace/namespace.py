import typing
from argparse import _SubParsersAction

from everai.commands.command import ClientCommand, setup_subcommands, command_error
from .list import ListCommand
from .get import GetCommand
from .create import CreateCommand
from .delete import DeleteCommand


class NamespaceCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        worker_parser = parser.add_parser('namespace',
                                          aliases=['namespaces', 'ns'],
                                          help='Manage the namespaces')
        worker_subparser = worker_parser.add_subparsers(help='Namespace command help')

        setup_subcommands(worker_subparser, [
            ListCommand,
            GetCommand,
            CreateCommand,
            DeleteCommand,
        ])

        worker_parser.set_defaults(func=NamespaceCommand)
        NamespaceCommand.parser = worker_parser

    def run(self):
        NamespaceCommand.parser.print_help()
