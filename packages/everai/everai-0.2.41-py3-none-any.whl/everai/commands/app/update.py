import argparse
import typing

from everai.commands.command import ClientCommand, command_error
from argparse import _SubParsersAction

from everai.app import App
from everai.app.app_manager import AppManager
from everai.commands.app import app_detect


class UpdateCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        update_parser = parser.add_parser(
            "update",
            help="Update an app",
            description='Update an app from manifest file or an App object in app.py. \n'
                        '--from-file indicates a manifest file for update app, \n'
                        'otherwise, everai command line tools find App in app.py\n'
                        'this operation may be trigger the worker rollout, if image, command ... changed\n',
            formatter_class=argparse.RawTextHelpFormatter,
        )
        update_parser.add_argument('--dry-run', action='store_true')

        file_group = update_parser.add_argument_group('from file')
        file_group.add_argument(
            '-f',
            '--from-file',
            type=str,
            help='Update app from manifest file (format in yaml), for example: --from-file filename'
        )

        update_parser.set_defaults(func=UpdateCommand)
        UpdateCommand.parser = update_parser

    @command_error
    @app_detect(optional=True)
    def run(self, app: typing.Optional[App] = None):
        if self.args.from_file is not None:
            app = App.from_yaml_file(self.args.from_file)
            if app.spec.image is None:
                raise ValueError('spec.image is required for manifest mode')
        else:
            if app is None:
                UpdateCommand.parser.error('could not found App object in app.py')

        result = AppManager().update(app, dry_run=self.args.dry_run)

        print(f"App `{result.name}` updated successfully")
