from everai.app import App
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction
from everai.app.app_manager import AppManager


class ListCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        list_parser = parser.add_parser('list', aliases=['ls'], help='List apps')
        namespaced = list_parser.add_mutually_exclusive_group()
        namespaced.add_argument('-n', '--namespace', default='default', help='List all apps in specified namespaces')

        all_namespaces = list_parser.add_mutually_exclusive_group()
        all_namespaces.add_argument('-A', '--all-namespaces', action='store_true',
                                    help='List all apps in all namespaces')

        ListDisplayer.add_output_to_parser(list_parser)
        list_parser.set_defaults(func=ListCommand)

    @command_error
    def run(self):
        from tabulate import tabulate
        if self.args.all_namespaces:
            apps = AppManager().list(all_namespaces=True)
        else:
            apps = AppManager().list(namespace=self.args.namespace or 'default')

        ListDisplayer[App](apps).show_list(self.args.output)
