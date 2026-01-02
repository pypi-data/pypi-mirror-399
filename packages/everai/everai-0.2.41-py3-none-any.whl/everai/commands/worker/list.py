import typing

from everai.app import App, AppManager
from everai.commands.command import ClientCommand, command_error, ListDisplayer
from argparse import _SubParsersAction, Namespace
from everai.commands.app import app_detect, add_app_name_to_parser
from everai.worker import Worker


class ListCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args: Namespace):
        self.args = args

    @staticmethod
    @app_detect(optional=True)
    def setup(parser: _SubParsersAction, app: typing.Optional[App]):
        list_parser = parser.add_parser('list', aliases=['ls'], help='List workers of app')
        add_app_name_to_parser(list_parser, app)
        ListDisplayer.add_output_to_parser(list_parser)
        list_parser.add_argument('--all', '-a', action='store_true',
                                 help='show all workers, include deleted and errors')
        list_parser.add_argument('--recent-days', '-d', nargs='?', type=int,
                                 default=2,
                                 help='show not running workers who is created in recent days')
        list_parser.add_argument('--namespace', '-n', nargs='?', type=str, default='default',
                                 help='namespace of app')

        list_parser.set_defaults(func=ListCommand)
        ListCommand.parser = list_parser

    @command_error
    def run(self):
        show_all = vars(self.args).pop('all', False)
        recent_days = vars(self.args).pop('recent_days', 2)
        output = vars(self.args).pop('output', 'table')

        workers = AppManager().list_worker(
            app_name=self.args.app_name,
            namespace=self.args.namespace,
            show_all=show_all,
            recent_days=recent_days,
        )
        ListDisplayer[Worker](workers).show_list(output)
