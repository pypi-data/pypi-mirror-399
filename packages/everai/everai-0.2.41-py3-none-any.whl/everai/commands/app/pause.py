import typing

from everai.app import App
from everai.commands.app.utils import add_app_namespace_to_parser
from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction
from everai.app.app_manager import AppManager
from everai.commands.app import add_app_name_to_parser, app_detect


class PauseCommand(ClientCommand):
    def __init__(self, args):
        self.args = args

    @staticmethod
    @app_detect(optional=True)
    def setup(parser: _SubParsersAction, app: typing.Optional[App]):
        pause_parser = parser.add_parser("pause", help="Pause an app, all worker will be stopped")

        add_app_name_to_parser(pause_parser, app, arg_name='name')
        add_app_namespace_to_parser(pause_parser, app, ['-n', '--namespace'])
        pause_parser.add_argument("--dry-run", action="store_true", help="dry run in client")

        pause_parser.set_defaults(func=PauseCommand)

    @command_error
    def run(self):
        if self.args.dry_run is True:
            print(f'pause app `{self.args.namespace}/{self.args.name}` (dry-run)')
        else:
            AppManager().pause(self.args.name, namespace=self.args.namespace)
