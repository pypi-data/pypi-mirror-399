import typing

from everai.app import App, AppManager
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction, Namespace
from everai.namespace import Namespace as EveraiNamespace


class ListCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        list_parser = parser.add_parser('list', aliases=['ls'], help='List the namespaces')
        ListDisplayer.add_output_to_parser(list_parser)
        list_parser.set_defaults(func=ListCommand)
        ListCommand.parser = list_parser

    @command_error
    def run(self):
        namespaces = AppManager().list_namespaces()
        ListDisplayer[EveraiNamespace](namespaces).show_list(self.args.output)
