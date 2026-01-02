from everai.commands.command import ClientCommand
from argparse import _SubParsersAction

from .check import CheckCommand
from .create import CreateCommand
from .get import GetCommand
from .pause import PauseCommand
from .resume import ResumeCommand
from .update import UpdateCommand
from .prepare import PrepareCommand
from .list import ListCommand
from everai.commands.command import setup_subcommands
from .queue import QueueCommand
from .events import EventsCommand
from .delete import DeleteCommand

from everai.commands.worker import WorkerCommand
from everai.commands.run import RunCommand



class AppCommand(ClientCommand):
    parser: _SubParsersAction = None

    def __init__(self, args):
        self.args = args

    @staticmethod
    def setup(parser: _SubParsersAction):
        app_parser = parser.add_parser('app', aliases=['apps', 'a'], help='Manage app')
        app_subparser = app_parser.add_subparsers(help='App command help')

        setup_subcommands(app_subparser, [
            CreateCommand,
            RunCommand,
            GetCommand,
            UpdateCommand,
            PauseCommand,
            ResumeCommand,
            PrepareCommand,
            ListCommand,
            QueueCommand,
            EventsCommand,
            WorkerCommand,
            CheckCommand,
            DeleteCommand,
        ])

        app_parser.set_defaults(func=AppCommand)
        AppCommand.parser = app_parser

    def run(self):
        AppCommand.parser.print_help()
