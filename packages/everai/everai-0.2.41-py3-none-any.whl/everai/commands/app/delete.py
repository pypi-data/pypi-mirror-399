import argparse
import typing
from argparse import _SubParsersAction

from everai.app import App
from everai.app.app_manager import AppManager
from everai.commands.app.utils import add_app_namespace_to_parser
from everai.commands.command import command_error, ClientCommand

from everai.commands.app import app_detect, add_app_name_to_parser


class DeleteCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    @app_detect(optional=True)
    def setup(parser: _SubParsersAction, app: typing.Optional[App]):
        delete_parser = parser.add_parser(
            "delete",
            help="Delete an app",
            # description='Delete an app from manifest file or an App object in app.py. \n'
            #             '--from-file indicates a manifest file for create app, \n'
            #             'otherwise, everai command line tool find app setup in app.py',
            # formatter_class=argparse.RawTextHelpFormatter,
        )

        add_app_name_to_parser(delete_parser, app, arg_name='name')
        add_app_namespace_to_parser(delete_parser, app, arg_name=['--namespace', '-n'])

        delete_parser.add_argument('--force', action='store_true')

        delete_parser.set_defaults(func=DeleteCommand)
        DeleteCommand.parser = delete_parser

    @command_error
    @app_detect(optional=True)
    def run(self, app: typing.Optional[App]):
        name = self.args.name
        namespace = self.args.namespace
        if not self.args.force:
            ret = input(f'\n[*] Deleting the app `{namespace}/{name}` is very dangerous, are you sure[y/N]')
            if ret not in ['y', "Y"]:
                print('user canceled')
                return

        AppManager().delete(name, namespace)

        print(f"App `{name}` deleted")
