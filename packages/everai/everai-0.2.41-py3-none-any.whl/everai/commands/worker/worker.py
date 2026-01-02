import typing
from argparse import _SubParsersAction

from everai.commands.command import ClientCommand, setup_subcommands
from .list import ListCommand
from .exec import ExecCommand
from everai.commands.app import app_detect
from everai.app import App


class WorkerCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        worker_parser = parser.add_parser('worker',
                                          aliases=['workers', 'w'],
                                          help='Manage the worker of app')
        worker_subparser = worker_parser.add_subparsers(help='Worker command help')

        setup_subcommands(worker_subparser, [
            ListCommand,
            ExecCommand,
        ])

        worker_parser.set_defaults(func=WorkerCommand)
        WorkerCommand.parser = worker_parser

    @app_detect(optional=True)
    def run(self, app: typing.Optional[App]):
        if app is not None:
            self.args.app_name = app.name

        WorkerCommand.parser.print_help()
