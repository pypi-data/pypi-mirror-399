import argparse
import typing
from argparse import _SubParsersAction

from everai.app import App
from everai.app.app_manager import AppManager
from everai.commands.command import command_error, ClientCommand

from everai.commands.app import app_detect, add_app_name_to_parser

route_name_description = ('Globally unique route name. '
                          'By default, it is same with the app name. '
                          'Once the application name conflicts, route-name needs to be set explicitly.')


class CreateCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        create_parser = parser.add_parser(
            "create",
            help="Create an app",
            description='Create an app from manifest file or an App object in app.py. \n'
                        '--from-file indicates a manifest file for create app, \n'
                        'otherwise, everai command line tool find app setup in app.py',
            formatter_class=argparse.RawTextHelpFormatter,
        )
        create_parser.add_argument('--dry-run', action='store_true')

        file_group = create_parser.add_argument_group('from file')
        file_group.add_argument(
            '-f',
            '--from-file',
            type=str,
            help='Create app from manifest file (format in yaml), for example: --from-file filename'
        )

        create_parser.add_argument('-n', '--namespace',
                                   default=None,
                                   help='indicate namespace of the app, commandline > [yaml file | app.py] > default')

        create_parser.set_defaults(func=CreateCommand)
        CreateCommand.parser = create_parser

    @command_error
    @app_detect(optional=True)
    def run(self, app: typing.Optional[App]):
        if self.args.from_file is not None:
            app = App.from_yaml_file(self.args.from_file)
            if app.spec.image is None:
                raise ValueError('spec.image is required for manifest mode')
        else:
            if app is None:
                CreateCommand.parser.error('could not found App object in app.py')

        if self.args.namespace is not None:
            app.namespace = self.args.namespace

        result = AppManager().create(app, dry_run=self.args.dry_run)
        print(f"App `{result.name}` successfully created")
